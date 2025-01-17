# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MastersItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class SheriffPropertyItem(scrapy.Item):
    """
        This class defines the fields we want for our sheriff property item
    """
    county_name = scrapy.Field() # *
    # property_id = scrapy.Field() # this changes dynamically by the website
    sheriff_num = scrapy.Field() # *
    court_case_num = scrapy.Field() # *
    sale_date = scrapy.Field() # *
    plaintiff = scrapy.Field() # *
    defendant = scrapy.Field() # *
    # address_url = scrapy.Field() # ! I am not using this at the moment - I am using address, maybe use google api lateR?
    address = scrapy.Field() # *
    zip_code = scrapy.Field() # *
    priors = scrapy.Field() # *
    attorney = scrapy.Field() # *
    approx_judgement = scrapy.Field() # *
    approx_upset = scrapy.Field() # *
    deed = scrapy.Field() # *
    deed_address = scrapy.Field() # *
    url = scrapy.Field() # *
    status_history = scrapy.Field() # *
    
    # additional field not in the first page.
    description = scrapy.Field() # *
    attorney_phone = scrapy.Field() # *
    min_bid = scrapy.Field() # *
    attorney_file = scrapy.Field() # * 
    parcel_num = scrapy.Field() #22

    
    # note: Description, Attorney File, Parcel number, Good Faith Upset, property details, 
    # note: not all addresses are url. Some are just text