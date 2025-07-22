"""This is a file that will be used to extract the information about the 
tour operators and store them in both MongoDB and csv file
"""

import os
import re
import sys
import json
import typing
import logging
import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool

# Add parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Local import
from operatorData import getOperatorData
from mongodb import collection, operatorCollection


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def getDetails():
    """
    Extracts and stores detailed information about safari tour operators 
    from SafariBookings.com using operator IDs retrieved from MongoDB.

    This function processes each operator's URL to extract data including:
        - Review score
        - Number of reviews
        - Office location
        - Company size
        - Membership affiliations
        - Tour types offered
        - Destination coverage
        - Price range
        - Company profile/description
        - Contact page URL

    The extracted data is stored in the `operatorCollection` MongoDB collection.

    Returns:
        list: A list of insertion result objects (`InsertOneResult`) from 
        MongoDB for each operator whose data was successfully stored.
    """
    
    # Extract the MongoDB data
    mongoData = getOperatorData()
    
    # Extract operators data from MongoDB data
    operatorData = json.loads(mongoData["operators"])

    # Clear any existing data
    operatorCollection.delete_many({})

    #Initialize empty list for company profiles
    companyProfiles = []
    
    # Extract data for each url
    for i, (key, value) in enumerate(operatorData.items()):

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

            # Extracting clean text content
            if profileHTML:
                profile = profileHTML.get_text(separator=" ", strip=True)
            else:
                logging.info("Description not found.")

            # Extracting review score
            scoreSpan = profileSoup.find('span', class_='review-score review-score--white')
            
            if scoreSpan and scoreSpan.find('em'):
                 score = scoreSpan.find('em').text.strip()
            else:
                score = None 

            # Extracting number of reviews
            reveiwsHTML = profileSoup.find('a', class_='reviews-link')
            if reveiwsHTML:
                numberOfReviews = reveiwsHTML.text.strip()
            else:
                numberOfReviews = None

            # Extracting data from the summary table
            summaryTable = profileSoup.find('dl', class_='hide show-t')

            # Extract all dd elements
            tableValues = summaryTable.find_all('dd')

            # Helper function to safely extract value at index
            def getTableValues(index):
                return tableValues[index].get_text(strip=True) if len(tableValues) > index else None
            
            # Safely extract each table value
            officeLocation = getTableValues(0)
            companySize = getTableValues(1)
            memberOf = getTableValues(2)
            tourTypes = getTableValues(3)
            destinations = getTableValues(4)
            priceRange = getTableValues(5)

            if priceRange:
                match = re.findall(r"\$\d+", priceRange)
            else:
                match = []

            if len(match) == 2:
                range = f"{match[0]} - {match[1]}"
            else:
                logging.warning("Price range format not as expected")
                
        else:
            logging.warning("Company profile not found.")
        

        operatorDetails = operatorCollection.insert_one({
            "name": value["name"],
            "URL": profileURL,
            "Reviews score": score,
            "Number of reviews": numberOfReviews,
            "Office location": officeLocation,
            "Company size": companySize,
            "Member of": memberOf,
            "Tour Types": tourTypes,
            "Destinations": destinations,
            "Price range": range,
            "Company profile": profile
        })
        companyProfiles.append(operatorDetails)

    return companyProfiles


# def main():
#     """Main entry point for loading or extracting operator data."""
#     logging.info("🚀 Starting operator data loading process...")

#     # Call your function to get the operator data
#     details = getDetails()

# if __name__ == "__main__":
#     main()

