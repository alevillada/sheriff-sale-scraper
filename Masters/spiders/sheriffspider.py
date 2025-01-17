import scrapy
from urllib.parse import urljoin
from Masters.items import SheriffPropertyItem
from twisted.internet.error import DNSLookupError, TimeoutError, TCPTimedOutError


class SheriffspiderSpider(scrapy.Spider):
    name = "sheriffspider"
    allowed_domains = ["salesweb.civilview.com"]
    start_urls = ["https://salesweb.civilview.com/"]
    
    custom_settings = {
        'COOKIES_ENABLED': True,
        'REDIRECT_MAX_TIMES': 2,
    }
    
    def start_requests(self):
        """ 
        
    this function starts the spider and sends a request to the start_urls
        """
        for url in self.start_urls:
            yield scrapy.Request(
                url= url,
                callback= self.parse,
                cookies={
                    'js_enabled': 'true',
                    'is_cookie_active': 'true',
                }, 
                meta= {
                       'playwright': True,
                       'playwright_context': 'persistent',
                       'errback': self.errback,
                       'download_delay': 5,}
            )

    def parse(self, response):
        """ 
          this function parses the information on each book hyperlink
        """
        
        county_list = response.css('.table-striped td')
        county = county_list[2] # 46
        
        #for county in county_list:  #! The page breaks down when I try to scrape all the counties - do 1 at a time
        if county_list: # note: just so i dont have to fix the indentation
            # extract county name
            county_name = county.css('a::text').get()
            
            # check if county name is not empty and is in NJ
            if county_name is not None and 'NJ' in county_name:
                county_href = county.css('a').attrib['href']
                
                # create the full url
                full_county_url = urljoin(self.start_urls[0], county_href) 
                
               
                self.logger.info(f"\n\nCOUNTY CHANGE!!!!county name: {county_name}\ncounty URL: {full_county_url}\n\n")
                
                yield response.follow(full_county_url, callback=self.parse_county_page,  meta= {
                       'playwright': True,
                       'playwright_context': 'persistent',
                       'errback': self.errback,
                       'download_delay': 5,})
                
    
    def parse_county_page(self, response):
        """ this function parses the information on each county page - This where the list for every house is found.

    #     Args:
    #         response: This is the information that is returned from scrapy
    #     """
        
        property_list = response.css('.table-striped tr')
        
        # the first item on the list is the title so lets remove this
        property_list = property_list[1:] # for testing purposes
        
        page_count=0
        
        for prop in property_list:
            # we need to primarily extract the link to the property
            prop_href = prop.css('.hidden-print a').attrib['href']
            full_prop_url = urljoin(self.start_urls[0], prop_href)
            
            page_count+=1
            # Follow the property URL with dont_redirect set to True
            self.logger.info(f"RABBIT HOLE!!!Following property URL: {full_prop_url}\ncount={page_count}")
            # go to that link  
            yield response.follow(full_prop_url, callback=self.parse_property_page, meta= {
                       'playwright': True,
                       'errback': self.errback,
                       'playwright_context': 'persistent',
                       'download_delay': 5,
                       })
            
            
    def parse_property_page(self, response):
        
        """ this function parses the information on each property page - This is where the property details are found
        """
        
        property_details = response.css('.table-striped tr')
        property_item = SheriffPropertyItem()
        
        # Check if property_details has any elements
        if not property_details:
            self.logger.warning(f"No property details found for URL: {response.url}")
            return
        
        
        # ? I am facing an issue, the order and categories of the property details are not the same for all the properties
        # ? I need to adjust my code in order to have checks of different categories and what column they fall on the database
        
        # Extract the county name from the tittle of the page
        # note: this is the same for every property page
        property_item['county_name'] = response.css('div.container h3::text').get()
    
        # extract elements from the property_details
        # this needs to be done dynamically as the order of the elements is not the same for all the properties
         
        for value in property_details:
            category = value.css('.heading-bold::text').get(default='N/A').strip()
            details = value.css('td:nth-child(2)::text').get(default='N/A').strip()
            
            # dynamically assign the values to the property_item
            match category:
                case "Sheriff #:":
                    property_item['sheriff_num'] = details
                case "Court Case #:":
                    property_item['court_case_num'] = details
                case "Sales Date:":
                    property_item['sale_date'] = details
                case "Plaintiff:":
                    property_item['plaintiff'] = details
                case "Defendant:":
                    property_item['defendant'] = details
                case "Address:":
                    #? Addresses that are hyperlink are under a tag
                    #? if the check_address is empty than it's a hyperlink
                    #? if it's not empty than it's just text
                    if details == '':
                        property_item['address'] = value.css('td:nth-child(2) a::attr(href)').get()
                    else:
                        property_item['address'] = ' '.join(value.css('td:nth-child(2)::text').getall()).strip()
                case 'Priors:':
                    property_item['priors'] = details
                case 'Attorney:':
                    property_item['attorney'] = details
                case 'Approx. Judgment*:':
                    property_item['approx_judgement'] = details
                case 'Upset Amount:':
                    property_item['approx_upset'] = details
                case 'Deed:':
                    property_item['deed'] = details
                case 'Deed Address:':
                    property_item['deed_address'] = details
                    
                # note: New Categories
                case 'Description:':
                    property_item['description'] = details
                case 'Attorney Phone:':
                    property_item['attorney_phone'] = details 
                case 'Minimum Bid:':
                    property_item['min_bid'] = details
                case 'Attorney File #:':
                    property_item['attorney_file'] = details
                case 'Parcel #:':
                    property_item['parcel_num'] = details
                
                
                
                # note: Redirected Categories
                # this is for categories that have a different name but still represent existing categories
                case 'Approx Judgment:':
                    property_item['approx_judgement'] = details
                case 'Approx. Upset*:':
                    property_item['approx_upset'] = details # upset amount
                case 'Approximate Judgment:':
                    property_item['approx_judgement'] = details
                case 'Approx Judgment*:':
                    property_item['approx_judgement'] = details
                case 'Property Address:':
                    if details == '':
                        property_item['address'] = value.css('td:nth-child(2) a::attr(href)').get()
                    else:
                        property_item['address'] = ' '.join(value.css('td:nth-child(2)::text').getall()).strip()
                case 'Good Faith Upset*:':
                    property_item['approx_upset'] = details
                case 'Property Details:':
                    property_item['description'] = details
                case "Approx. Judgment:":
                    property_item['approx_judgement'] = details
                case "Sale Date:":
                    property_item['sale_date'] = details
                    
                    
                case _:
                    if category != 'N/A':
                        self.logger.warning(f"Category not found: {category}\n")
                        
        property_item['url'] = response.url 
        
        # * In every property page there is a status history table
        # this is variable so we need to extract it in a different way
        status_history = response.css('#longTable tbody tr')
        status_log = ""
        for status in status_history:
            status_date = status.css('td:nth-child(1)::text').get(default='N/A')
            status_desc = status.css('td:nth-child(2)::text').get(default='N/A')
            status_log = status_log + f"{status_date}: {status_desc}\n"
            
        property_item['status_history'] = status_log
        
        yield property_item
    
        
    def errback(self, failure):
        """
        This function is called when a request fails. It logs the error and retries the request
        """
        self.logger.error(repr(failure))
        if failure.check(DNSLookupError):
            request = failure.request
            self.logger.error(f'DNS Lookup Error on {request.url}')
        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error(f'Timeout Error on {request.url}')
        else:
            self.logger.error('An unknown error occurred')
    #! ISSUE - NOT ALL THE PAGES HAVE THE SAME LAYOUT, AS IN NOT ALL THE PAGES HAVE THE SAME CATEGORY - SOME MISS SOME. 