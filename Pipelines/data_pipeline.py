import csv
import os
import time
from dataclasses import fields, asdict
import logging

# Set up a logger for this module

logger = logging.getLogger(__name__)

class DataPipeline:

    # Initializes the DataPipeline with a CSV filename, a queue limit, and internal structures to track seen data and manage file writing.

    def __init__(self, csv_filename='', storage_queue_limit=50):
        # Keeps track of names already seen to avoid duplicates
        self.names_seen = []
        # Temporary storage for incoming data before writing to CSV
        self.storage_queue = []
        # Maximum number of items to hold before saving to CSV
        self.storage_queue_limit = storage_queue_limit
        # Name of the SCV file to write to
        self.csv_filename = csv_filename
        # Flag to indicate if the DSV file is currently being written to
        self.csv_file_open = False

    # Saves all items currently in the storage queue to the CSV file. Writes headers if the file is new, and clears the queue after saving. Prevents concurrent writes using a flag.
    
    def save_to_csv(self):
        # Mark the file as open to prevent concurrent writes
        self.csv_file_open = True
        # Copy the current storage queue and clear it
        data_to_save = self.storage_queue[:]
        self.storage_queue.clear()
        # If there is nothing to save, exit early
        if not data_to_save:
            return
        # Get field names from the dataclass
        keys = [field.name for field in fields (data_to_save[0])]
        # Check if the file exists and is not empty
        file_exists = os.path.isfile(self.csv_filename) and os.path.getsize(self.csv_filename) >0
        # Open the file in append mode
        with open(self.csv_filename, mode='a', newline='',encoding='utf-8') as output_file:
            writer = csv.DictWriter(output_file, fieldnames=keys)
            # Write header only if the file is new
            if not file_exists:
                writer.writeheader()
            # Write each item as a dictionary
            for item in data_to_save: 
                writer.writerow(asdict(item))
        
        # Mark the file as closed after writing
        self.csv_file_open = False
    
    # Adds a new data item to the storage queue if it's not a duplicate. Automatically triggers a save to CSV if the queue reaches its limit.

    def add_data(self, scraped_data):
        # Add data only if it is not a duplicate
        if not self.is_duplicate(scraped_data):
            self.storage_queue.append(scraped_data)
            # Save to CSV if queue limit is reached and file is not in use
            if len (self.storage_queue) >= self.storage_queue_limit and not self.csv_file_open:
                self.save_to_csv()
    
    # Checks whether the given data item has already been added based on its 'name' attribute. Logs a warning if a duplicate is found and prevents it from being added again.

    def is_duplicate ( self, input_data):
        # Check if the name has already been seen
        if input_data.name in self.names_seen: 
            logger.warning(f"Duplicate item found: {input_data.name}")
            return True
        # Otherwise, add the name to the list
        self.names_seen.append(input_data.name)
        return False
    
    # Finalizes the pipeline by saving any remaining data in the queue. Waits briefly if a file write is in progress to ensure safe closure.

    def close_pipeline (self):
        # Wait if the file is currently begin written to
        if self.csv_file_open:
            time.sleep(5)
        # Save any remaining data in the queue
        if len (self.storage_queue)> 0:
            self.save_to_csv()