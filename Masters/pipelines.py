# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pandas as pd
import regex as re
from decimal import Decimal


class MastersPipeline:
    
    """
        Crates a pipeline that will clean, validate and post-process the data before it is stored in the database or wherever we want to store it.
    """
    def process_item(self, item, spider):
        """
            Process each element in the item        
        """
        adapter = ItemAdapter(item)
        
        # * Strip the trailing white spaces and new line from the fields
        field_names = adapter.field_names()
        for field_name in field_names:
            value = adapter.get(field_name)
            if value is not None:
                adapter[field_name] = value.strip() # strip the white spaces and newline
        
        # * change the approximate judgement string to float
        # * change the upset amount string to float
        # remove the dollar sign
        value_keys = ['approx_judgement', 'approx_upset', 'min_bid']
        for key in value_keys:
            value = adapter.get(key)
            if value == '' or value is None:
                adapter[key] = None
            elif value and ("$" in value or "," in value):
                value = value.replace('$', '')
                value = value.replace(',', '') # remove the comma - it creates issues when converting to float
                adapter[key] = Decimal(value)
        
        
        # *prior field has a lot of white spaces and new lines
        value = adapter.get('priors')
        if value is not None:
            value = value.replace('\n', '')
            value = value.replace('\t', '')
            value = value.replace('  ', '')
            adapter['priors'] = value
            
        
        # *descriptions field has a lot of white spaces and new lines
        # ! Later i want to implement a function that will recognize the "Upset Price" that is usually in the description
        value = adapter.get('description')
        if value is not None:
            value = value.replace('\n', '')
            value = value.replace('\t', '')
            value = value.replace('  ', '')
            adapter['description'] = value
            
        # *plaintiff and defendant fields have a lot of white spaces and new lines
        value_keys = ['plaintiff', 'defendant']
        for key in value_keys:
            value = adapter.get(key)
            if value is not None:
                value = value.replace('\n', '')
                value = value.replace('\t', '')
                value = value.replace('  ', '')
                adapter[key] = value
            
            
        # **Process 'status_history' field**
        status_history = adapter.get('status_history')
        if status_history:
            status_history = status_history.replace(': ', ':').strip()
            status_list = [s.strip() for s in status_history.split('\n') if s.strip()]
            adapter['status_history'] = status_list
            new_dict = {}

            for entry in adapter['status_history']:
                parts = entry.split(":")
                if len(parts) >= 2:
                    key = parts[0].strip()
                    
                    # mm/dd/yyy is 10 characters long
                    # if the date is not in the expected format, most likely because of the time attached to it
                    # check this
                    if "PM" not in parts[-1] and "AM" not in parts[-1]: 
                        date_str = parts[-1].strip()
                    elif "PM" in parts[-1] or "AM" in parts[-1]:
                        date_str = parts[-2].strip()
                        temp = date_str.split(" ")
                        date_str = temp[0]
                        
                        
                    try:
                        date_obj = pd.to_datetime(date_str)
                        date_formatted = date_obj.strftime('%Y-%m-%d')
                    except (ValueError, TypeError) as e:
                        spider.logger.warning(f"Error parsing date '{date_str}': {e}")
                        date_formatted = None
                    new_dict[key] = date_formatted
                else:
                    spider.logger.warning(f"Unexpected status history format: {entry}")
                    new_dict[entry] = None

            adapter['status_history'] = new_dict
        else:
            adapter['status_history'] = {}
                
                
        # create address and zip code from it. 
        # note: i can possibly use the google maps api to extract coordinates
        # **Process 'address' and 'zip_code' fields**
        value = adapter.get('address')
        if value:
            if "https:" in value:
                # Extract address from URL
                address = value.split('/')[-1].replace('+', ' ')
                address = address.replace('a%2fk%2fa', '')
                address = address.replace('F%2fK%2fA ', '')
                # address = address.replace('%', '')
                adapter['address'] = address
            else:
                adapter['address'] = value.strip()

            # Extract zip code
            address_parts = adapter['address'].split(' ')
            if address_parts:
                zip_code = address_parts[-1]
                adapter['zip_code'] = zip_code.strip()
            else:
                adapter['zip_code'] = None
        else:
            adapter['address'] = None
            adapter['zip_code'] = None

        # * Parse county name
        value = adapter.get('county_name')
        value = value if value else ''
        # extract the county name from the string
        match = re.search(r"\(([^,]+)", value)
        if match:
            adapter['county_name'] = match.group(1).strip()
        else:
            adapter['county_name'] = None
            
            
        # * Change the sale date to a date object
        value = adapter.get('sale_date')
        if value is not None:
            if len(value) <= 10: # expecting a certain format
                x = pd.to_datetime(value, format='%m/%d/%Y')
                x = x.strftime('%Y-%m-%d')
                adapter['sale_date'] = x
            
            # if PM or AM is in the date string
            if len(value) > 10:
                temp = value.split(" ")
                x = pd.to_datetime(temp[0], format='%m/%d/%Y')
                x = x.strftime('%Y-%m-%d')
                adapter['sale_date'] = x
        
        
        # * Make Phone numbers consistent
        value = adapter.get('attorney_phone')
        if value is not None:
            value = value.strip()
            if "(" in value:
                value = value.replace('(', '')
                value = value.replace(')', '')
                value = value.replace(' ', '-')
                adapter['attorney_phone'] = value 
                
        return item



# * Database Pipeline
import os
from dotenv import load_dotenv
import psycopg2
from scrapy.exceptions import DropItem
# load environment variables
load_dotenv()

class SaveToPostgresPipeline:
    """
        This class is used to save the data to a postgres database
    """
    
    def __init__(self):
        """
            This function initializes the class, basically all the settings for the database
        """
        # * Connect to the database
        self.connection = psycopg2.connect(
            user = os.getenv('DB_USER'),
            host = os.getenv('DB_HOST'),
            dbname = os.getenv('DB_NAME'),
            port = os.getenv('DB_PORT'),
            password = os.getenv('DB_PASSWORD')
        )
        
        # * Open a cursor to perform database operations
        self.cursor = self.connection.cursor()
        
        # * Creates a table if it does not exist for the sheriff properties
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS sheriff_property (
                sheriff_num VARCHAR(255) PRIMARY KEY,
                address VARCHAR(512)  NOT NULL,
                approx_judgement NUMERIC(15,2),
                attorney TEXT,
                county_name VARCHAR(255) NOT NULL ,
                court_case_num VARCHAR(255) NOT NULL UNIQUE,
                deed VARCHAR(255),
                deed_address VARCHAR(255),
                defendant TEXT,
                plaintiff TEXT,
                priors TEXT,
                sale_date DATE NOT NULL,
                approx_upset NUMERIC(15,2),
                zip_code VARCHAR(10),
                url VARCHAR(2048),
                description TEXT,
                attorney_phone VARCHAR(15),
                attorney_file VARCHAR(255),
                min_bid NUMERIC(15,2),
                parcel_num VARCHAR(255)
            )
        """)
        
        # * Creates a table if it does not exist for the status history
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS status_history (
                id SERIAL PRIMARY KEY,
                sheriff_num VARCHAR(255) REFERENCES sheriff_property(sheriff_num) ON DELETE CASCADE,
                status_desc VARCHAR(255),
                status_date DATE
            )
        """)
        
        # Commit the table creation
        self.connection.commit()
        
        
        
    def process_item(self, item, spider):
        """
            This function processes the items and saves them to the database
        """
        try:
            self.cursor.execute("""
                            INSERT INTO sheriff_property (
                                address,
                                sheriff_num,
                                approx_judgement,
                                attorney,
                                county_name,
                                court_case_num,
                                deed,
                                deed_address,
                                defendant,
                                plaintiff,
                                priors,
                                sale_date,
                                approx_upset,
                                zip_code,
                                url,
                                description,
                                min_bid,
                                attorney_phone,
                                attorney_file,
                                parcel_num) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(
                                item.get('address'),
                                item.get('sheriff_num'),
                                item.get('approx_judgement'),
                                item.get('attorney'),
                                item.get('county_name'),
                                item.get('court_case_num'),
                                item.get('deed'),
                                item.get('deed_address'),
                                item.get('defendant'),
                                item.get('plaintiff'),
                                item.get('priors'),
                                item.get('sale_date'),
                                item.get('approx_upset'),
                                item.get('zip_code'),
                                item.get('url'),
                                item.get('description'),  # This will be None if 'description' key is missing
                                item.get('min_bid'),
                                item.get('attorney_phone'),
                                item.get('attorney_file'),
                                item.get('parcel_num')))
            
        
            # * Execute the command into the database
            self.connection.commit()
        
            # * Save the status history to the database
        
            # Check if status history is empty
            if not item['status_history']:
                raise DropItem(f"No status history found for sheriff_num: {item['sheriff_num']}") # drop the item
        
            # Loop through the status history and save to the database
            for status, date in item['status_history'].items():
                self.cursor.execute("""
                            INSERT INTO status_history (
                                sheriff_num,
                                status_desc,
                                status_date) values (%s,%s,%s)""",(item['sheriff_num'],
                                    status,
                                    date))
    
            # * Execute the command into the database
            self.connection.commit()
        
        except psycopg2.Error as e:
            spider.logger.error(f"Error saving item to database: {e}")
            self.connection.rollback()
            raise DropItem(f"Error saving item to database: {e}")
        
        print(f"Item saved to database: {item['sheriff_num']}")
        return item
    
    
    def close_spider(self, spider):
        """
            function to close spider when done with the database
        """
        self.cursor.close()
        self.connection.close()