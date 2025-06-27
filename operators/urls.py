"""This script extracts links of all tour operators 
from safaribookings.com website
"""

import json
import logging
import requests
from bs4 import BeautifulSoup
from typing import Tuple, Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def getPageNumbers() -> int:
    """This fucntion extracts the number of pages that contain the 
    list of tour operators from safaribookings.com site

    Return:
          pages (int): Number of pages containing the operators
    """
    url = "https://www.safaribookings.com/operators/page/1"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error accessing {url}: {e}")
        return None
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        pagination = soup.find("div", class_="list__paginator")
        if pagination:
            page_links = pagination.find_all('a')
            page_numbers = [int(a.text) for a in page_links if a.text.isdigit()]
            if page_numbers:
                pages = max(page_numbers)
                logging.info(f"Found {pages} pages of tour operators.")
                return pages
            else:
                logging.warning("No page numbers found in pagination.")
                return 1
        else:
            logging.warning("Pagination not found on the page.")
            return 1
    else:
        logging.error(f"Unexpected status code: {response.status_code}")
        return None

def getURLS(pages: int):

    pass

def main():
    pages = getPageNumbers()
    print(pages)

if __name__ == "__main__":
    main()