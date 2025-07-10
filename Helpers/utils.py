
print("Loading get_scrapeops_url from utils.py")


from Helpers.config import API_KEY

# Import the urlencode function to build a URL query string

from urllib.parse import urlencode

# Function that constructs a ScrapeOps URL for scraping a given URL with a specified location

def get_scrapeops_url (url, location):
    # Check if API_KEY is available, raise an error if it's missing
    if not API_KEY:
        raise ValueError ("API KEY is missing from environment")
    
    # Create a dictionary of parameters to include in the URL query string
    payload = {
        "api_key": API_KEY,    # Your ScrapeOps API key
        "url":url,             # The target URL to scrape
        "country": location    # The country to route the request through
    }
    return "https://proxy.scrapeops.io/v1/?" + urlencode(payload)