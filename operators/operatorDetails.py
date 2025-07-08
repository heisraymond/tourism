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

operatorURLS = {
    "overview": f"https://www.safaribookings.com/{id}",
    "safariandtours": f"https://www.safaribookings.com/operator-tours/{id}",
    "reviews": f"https://www.safaribookings.com/reviews/{id}",
    "companyprofile": f"https://www.safaribookings.com/profile/{id}",
    "destinations": f"https://www.safaribookings.com/profile/{id}",
    "contact": f"https://www.safaribookings.com/operator-contact/{id}"
}

def getDetails(urls: Dict):
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
    pass
