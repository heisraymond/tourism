"""This is a file that will be used to extract the information about the 
tour operators and store them in both MongoDB and csv file
"""

import os
import sys
import json
import logging
import requests
from typing import Dict
from bs4 import BeautifulSoup
from multiprocessing import Pool

# Add parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Local import
import mongodb
from urls import getURLS


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def getDetails():
    """This function will recieve urls and start processing one url
    after another

    The details to be extracted are:
    - Review score
    - Offices branches
    - Size
    - Member of 
    - Tour types
    - Destinations
    - Price range
    - Number of safari & tours
    - Number of reviews
    - Company profile
    - contacts
    """
    
    # Extract the operator URLS
    urls = getURLS()
    
    # Convert the urls from strings to python dictionary
    if isinstance(urls, str):
        urls = json.loads(urls)
    
    # Extract data for each url
    for i, (key, value) in enumerate(urls.items()):

        # Initialize the id variable
        id = value["id"]

        # Initialize num
        num = None

        operatorURLS = {
           "overview": f"https://www.safaribookings.com/{id}",
           "safariandtours": f"https://www.safaribookings.com/operator-tours/{id}/page/{num}",
           "reviews": f"https://www.safaribookings.com/reviews/{id}/page/{num}",
           "companyprofile": f"https://www.safaribookings.com/profile/{id}",
           "destinations": f"https://www.safaribookings.com/profile/{id}",
           "contact": f"https://www.safaribookings.com/operator-contact/{id}" 
        }

        # Extract company profile for an indvidual company
        profileURL = operatorURLS["companyprofile"]

        try:
            profileResponse = requests.get(profileURL, timeout=10)
            profileResponse.raise_for_status()
        except requests.RequestException as e:
            logging.error(f"Error accessing {profileURL}: {e}")
            return {}
        
        if profileResponse.status_code == 200:
            profileSoup = BeautifulSoup(profileResponse.text, "html.parser")
            profileHTML = profileSoup.find("div", class_="col col-12 profile-desc")

            # Print the clean text content
            if profileHTML:
                description = profileHTML.get_text(separator=" ", strip=True)
                print(description)
            else:
                logging.info("Description not found.")


    return description
    

def main():
    try:
        logging.info("Starting the tour operator extraction process...")
        details = getDetails()
        logging.info("Extraction completed successfully.")
        # You can add logic to store data in MongoDB or CSV here.
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
