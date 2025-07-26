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
from operators.operatorURLData import getOperatorData
from mongodb import collection, operatorCollection


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def getDetails(operator):
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
        - Number of Tours
        - Destination coverage
        - Price range
        - Company profile/description
        - Contact page URL

    The extracted data is stored in the `operatorCollection` MongoDB collection.

    Args:
        operator: A dictionary of operator data

    Returns:
        list: A list of insertion result objects (`InsertOneResult`) from 
        MongoDB for each operator whose data was successfully stored.
    """

    id = operator["id"]
    name = operator["name"]

    operatorURLS = {
        "companyprofile": f"https://www.safaribookings.com/profile/{id}",
        "contact": f"https://www.safaribookings.com/operator-contact/{id}" 
    }

    profileURL = operatorURLS["companyprofile"]

    try:
        profileResponse = requests.get(profileURL, timeout=10)
        profileResponse.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"[{name}] Error accessing profile page: {e}")
        return None

    if profileResponse.status_code == 200:
        profileSoup = BeautifulSoup(profileResponse.text, "html.parser")
        profileHTML = profileSoup.find("div", class_="col col-12 profile-desc")

        # Extracting clean text content
        if profileHTML:
            profile = profileHTML.get_text(separator=" ", strip=True)
        else:
            logging.info("Description not found.")
            return None

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

        # Extracting number of tours
        toursSoup = profileSoup.find('ul', class_='filters__countries')
        toursList = toursSoup.find_all('li')
        listTwo = toursList[1]

        numberOfTours = None
        if listTwo:
            span = listTwo.find("span", class_="hide show-ti")
            if span:
                numberOfTours = span.get_text(strip=True)
            else:
                logging.info("numberOfTours span not found.")
        else:
            logging.info("listTwo not found.")

        # Extracting data from the summary table
        summaryTable = profileSoup.find('dl', class_='hide show-t')

        # Extract all dd elements
        tableValues = summaryTable.find_all('dd')

        # Extract all dt elements
        tableLabels = summaryTable.find_all('dt')

        def getIndexLabel(dt_elements, word):
            """
            Returns the index of the first <dt> element containing the given word (case-insensitive).
            If not found, returns -1.
            """
            word = word.lower()
            return next(
                (i for i, dt in enumerate(dt_elements) if word in dt.get_text(strip=True).lower()),
                -1
            )

        def getTableValue(index):
            """
            Safely extracts the text value from the dd element at the given index.
            Returns None if index is out of range or value is missing.
            """
            if 0 <= index < len(tableValues):
                value = tableValues[index]
                if value:
                    return value.get_text(strip=True)
            # Optionally log a warning
            logging.warning(f"Invalid index: {index}. tableValues length: {len(tableValues)}")
            return None

        
        # Safely extract each table value
        officeLocationIndex = getIndexLabel(
            tableLabels, word="Office In:"
        )
        officeLocation = getTableValue(officeLocationIndex)
        companySizeIndex = getIndexLabel(
            tableLabels, word="Size:"
        )
        companySize = getTableValue(companySizeIndex)
        memberOfIndex = getIndexLabel(
            tableLabels, word="Member Of:"
        )
        memberOf = getTableValue(memberOfIndex)
        tourTypesIndex = getIndexLabel(
            tableLabels, word="Tour Types:"
        )
        tourTypes = getTableValue(tourTypesIndex)
        destinationsIndex = getIndexLabel(
            tableLabels, word="Destinations:"
        )
        destinations = getTableValue(destinationsIndex)
        priceRangeIndex = getIndexLabel(
            tableLabels, word="Price Range:"
        )
        priceRange = getTableValue(priceRangeIndex)

        range = None  # Default fallback
        if priceRange:
            match = re.findall(r"\$\d{1,3}(?:,\d{3})*(?:\.\d{2})?", priceRange)
            if len(match) == 2:
                range = f"{match[0]} - {match[1]}"
            else:
                logging.warning("Price range format not as expected")
        else:
            logging.warning("Price range is missing.")

    else:
        logging.warning("Company profile not found.")

    
    """**************************************************
                EXTRACTING COMPANY CONTACTS
       **************************************************
    """
    operatorCONTACT = operatorURLS["contact"]

    try:
        conactsResponse = requests.get(operatorCONTACT, timeout=10)
        conactsResponse.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"[{name}] Error accessing profile page: {e}")
        return None
    
    if conactsResponse.status_code == 200:
        contactsSoup = BeautifulSoup(conactsResponse.text, "html.parser")
        contactsHTML = contactsSoup.find("div", class_="operator__content")

        contactsContent = contactsHTML.find_all(
            "div", class_="col col-12 detail__content__block--addressblock"
            )
        
        # Initialize empty list of contacts
        contacts = []

        for block in enumerate(contactsContent):
            text = block.get_text(separator="\n", strip=True)
            contactOffice = text
            contacts.append(contactOffice)

        # Extract website
        websiteHTML = contactsHTML.find(
            "div", class_="col col-12 detail__content__block--addressblock"
            )
        website = websiteHTML.find("a").get_text(strip=True)

        # Extract phone number
        phoneNumber = contactsHTML.get_text(separator="\n", strip=True)
        # Extract the word that starts with '+'
        match = re.search(r"\+\d+", phoneNumber)
        if match:
            phone_number = match.group()
        else:
            logging.warning("No phone number found.")


    return {
            "name": operator["name"],
            "URL": profileURL,
            "Reviews score": score,
            "Number of reviews": numberOfReviews,
            "Office location": officeLocation,
            "Company size": companySize,
            "Member of": memberOf,
            "Tour Types": tourTypes,
            "Number of tours": numberOfTours,
            "Destinations": destinations,
            "Price range": range,
            "Company profile": profile,
            "Contacts": contacts,
            "Website": website,
            "Phone number": phone_number
        }
        



def getOperatorProfileDetails():
    """
    Processes all operators using multiprocessing and inserts into MongoDB.
    """
    mongoData = getOperatorData()
    operatorData = json.loads(mongoData["operators"])
    operators = [{"id": v["id"], "name": v["name"]} for v in operatorData.values()]

    # Clear previous options
    operatorCollection.delete_many({})  

    with Pool(processes=10) as pool:  
        results = pool.map(getDetails, operators)

    # Filter out None results (failed ones)
    valid_results = [res for res in results if res]

    # Insert into MongoDB
    if valid_results:
        insert_result = operatorCollection.insert_many(valid_results)
        return insert_result.inserted_ids
    else:
        return []


def main():
    logging.info("Starting...")
    inserted = getOperatorProfileDetails()
    logging.info(f"Done. Inserted: {len(inserted)}")

if __name__ == "__main__":
    main()



# operatorURLS = {
#            "overview": f"https://www.safaribookings.com/{id}",
#            "safariandtours": f"https://www.safaribookings.com/operator-tours/{id}/page/{num}",
#            "reviews": f"https://www.safaribookings.com/reviews/{id}/page/{num}",
#            "companyprofile": f"https://www.safaribookings.com/profile/{id}",
#            "destinations": f"https://www.safaribookings.com/profile/{id}",
#            "contact": f"https://www.safaribookings.com/operator-contact/{id}" 
#     }

