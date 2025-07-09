"""This is a file that will be used to extract the information about the 
tour operators and store them in both MongoDB and csv file
"""

import os
import sys
import time
import json
import logging
import requests
from typing import Dict
from bs4 import BeautifulSoup
from multiprocessing import Pool

# Add parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Local import
from urls import getURLS, saveToMongodb
from mongodb import collection


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def getOperatorData():
    """This funtion will check if operatorData is available in the
    database and extract the required data, and if not it will run
    the urls.py script to extract the data and store them in the 
    database
    """

    # Check if data is available in the database first
    if collection.count_documents({}) == 0:
        logging.warning("No data found in 'operatorsURLS' collection")

        #Call the function for extracting the URLS and save them
        MAX_RETRIES = 5  
        retries = 0

        while True:
            try:
                operatorURLS = getURLS()              # Extract URLs
                id = saveToMongodb(operatorURLS)      # Attempt to save

                if id:
                    logging.info("Successfully stored data in the database.")
                    break  # Exit loop if successful
                else:
                    raise Exception("Data was not stored successfully.")

            except Exception as e:
                retries += 1
                logging.warning(f"Attempt {retries} failed: {e}")

                if retries >= MAX_RETRIES:
                    logging.error("Maximum retries reached. Exiting.")
                    break

                logging.info("🔁 Retrying in 5 seconds...")
                time.sleep(5)  
    
    else:
        logging.info("Data found in 'operatorsURLS' collection. Loading from DB...")

    operatorData = collection.find_one()

    if operatorData:
        logging.info("Operator data found..")
        print(operatorData)
    else:
        logging.error("Operatord data not found..")

    return operatorData



# def getDetails():
#     """This function will recieve urls and start processing one url
#     after another

#     The details to be extracted are:
#     - Review score
#     - Offices branches
#     - Size
#     - Member of 
#     - Tour types
#     - Destinations
#     - Price range
#     - Number of safari & tours
#     - Number of reviews
#     - Company profile
#     - contacts
#     """
    
#     # Extract the operator URLS
#     urls = getURLS()
    
#     # Convert the urls from strings to python dictionary
#     if isinstance(urls, str):
#         urls = json.loads(urls)
    
#     # Extract data for each url
#     for i, (key, value) in enumerate(urls.items()):

#         # Initialize the id variable
#         id = value["id"]

#         # Initialize num
#         num = None

#         operatorURLS = {
#            "overview": f"https://www.safaribookings.com/{id}",
#            "safariandtours": f"https://www.safaribookings.com/operator-tours/{id}/page/{num}",
#            "reviews": f"https://www.safaribookings.com/reviews/{id}/page/{num}",
#            "companyprofile": f"https://www.safaribookings.com/profile/{id}",
#            "destinations": f"https://www.safaribookings.com/profile/{id}",
#            "contact": f"https://www.safaribookings.com/operator-contact/{id}" 
#         }

#         # Extract company profile for an indvidual company
#         profileURL = operatorURLS["companyprofile"]

#         try:
#             profileResponse = requests.get(profileURL, timeout=10)
#             profileResponse.raise_for_status()
#         except requests.RequestException as e:
#             logging.error(f"Error accessing {profileURL}: {e}")
#             return {}
        
#         if profileResponse.status_code == 200:
#             profileSoup = BeautifulSoup(profileResponse.text, "html.parser")
#             profileHTML = profileSoup.find("div", class_="col col-12 profile-desc")

#             # Print the clean text content
#             if profileHTML:
#                 profile = profileHTML.get_text(separator=" ", strip=True)
#                 print(profile)
#             else:
#                 logging.info("Description not found.")


#     return profile
    

# def main():
#     try:
#         logging.info("Starting the tour operator extraction process...")
#         details = getDetails()
#         logging.info("Extraction completed successfully.")
#         # You can add logic to store data in MongoDB or CSV here.
#     except Exception as e:
#         logging.error(f"An error occurred: {e}")

# if __name__ == "__main__":
#     main()

def main():
    """Main entry point for loading or extracting operator data."""
    logging.info("🚀 Starting operator data loading process...")

    # Call your function to get the operator data
    operator_data = getOperatorData()

if __name__ == "__main__":
    main()

