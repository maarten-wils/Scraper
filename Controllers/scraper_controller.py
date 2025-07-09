import requests
import logging
from bs4 import BeautifulSoup
from Products.product import ScrapedProduct

# Initialize logger to capture log messages during scraping

logger= logging.getLogger(__name__)

# Main function to search for products on Amazon

def search_products( product_name: str, page_number: int=1, location:str="us", retries: int=2):
    scraped_products = []   # List to store succesfully scraped products
    attempts = 0            # Counter for retry attempts
    success = False         # Flag to indicate if scraping was successful

    # Retry loop: attempts scraping until it succeeds or max retries are reached

    while attempts < retries and not success:
        try:
            # Construct the Amazon search URL 
            search_url = f"https://www.amazon.com/s?k={product_name}&page={page_number}"
            logger.info ( f" Fetching: {search_url}")

            # Send HTTP GET request to the search URL
            response = requests.get(search_url)
            if response.status_code!=200:
                raise Exception (f"Status code: {response.status_code}")
            
            logger.info( "Successfull fetched page")

            # Parse the HTML content of the page using BeautifulSoup
            soup= BeautifulSoup(response.text, "html.parser")

            # Remove unwanted elements like ads
            # 'decompose()' removes the tag from the tree and destroys it

            for ad_div in soup.find_all("div",class_="AdHolder"):
                ad_div.decompose()
            
            # Find all product containders (divs)
            product_divs = soup.find_all("div")
            for product_div in product_divs:
                h2 = product_div.find("h2")
                if not h2 or not h2.text.strip():
                    continue # Skip if no product title is found

                product_title = h2.text.strip()
                a=h2.find("a")
                product_url = a.get("href") if a and a.get("href") else "no product url"

                # Extract ASIN (Amazon Standard Identification Number), a unique product ID
                name = product_div.get("data-asin")
                if not name: 
                    continue # Skip if no ASIN is found

                # Check if the product is sponsored
                is_sponsored= "sspa" in product_url.lower()


                # Extract currency symbol (e.g., $, €, £)
                price_currency=product_div.find("span", class_="a-price-symbol")

                currency= price_currency.text if price_currency else ""

                # Extract current and original prices
                prices = product_div.find_all("span", class_="a-offscreen")
                try: 

                    current_price = float(prices[0].text.replace(currency, "").replace(",","").strip()) if prices else 0.0
                    original_price = float(prices[1].text.replace(currency,"").replace(",","").strip()) if len(prices)>1 else current_price
                except:
                 continue # Skip product if price parsing fails

                # Extract product rating (e.g., 4.5 out of 5 stars)
                rating_tag= product_div.find("span", class_="a-icon-alt")
                try:
                    rating = float(rating_tag.text[0:3]) if rating_tag else 0.0
                except: 
                    rating= 0.0 # Default to 0.0 if rating parsing fails
                
                # Create a ScrapedProduct object and add it to the list
                product = ScrapedProduct(
                    name=name, 
                    product_title=product_title,
                    product_url=product_url,
                    current_price=current_price,
                    original_price=original_price,
                    currency=currency,
                    rating=rating,
                    is_sponsored=is_sponsored  
                )
                scraped_products.append(product)
            
            success = True # Mark scraping as succesful

        except Exception as e: 
            logger.warning(f"Attempts {attempts +1 } failed: {e}")
            attempts+=1
    
    if not success:
        logger.error(" scraping failed")
    
# Return the list of scraped products

    return scraped_products