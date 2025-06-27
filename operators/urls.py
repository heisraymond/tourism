"""This script extracts links of all tour operators 
from safaribookings.com website
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
    








def fetchPageURLS(page: int) -> Dict[int, Dict[str, str]]:
    """
    This function extracts the links of tour operators from each page.

    Args:
        pages (int): The number of pages to extract links from.

    Returns:
        Dict[int, Dict[str, str]]: A dictionary where each key is a link number
                                   and the value is another dictionary containing
                                   the operator's name and link.
        Example:
            {
              1: {
                   "name": "Random operator 1",
                   "link": "https://www.safaribookings.com/p1"
              },
              2: {
                   "name": "Random operator 2",
                   "link": "https://www.safaribookings.com/p2"
              },
              ...
            }
    """

    url = f"https://www.safaribookings.com/operators/page/{page}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error accessing {url}: {e}")
        return {}
        
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        operator_links = soup.select('a.row[href^="https://www.safaribookings.com/p"]')
            
        # Initialize the dictionary
        pageURLS = {}

        for i, a in enumerate(operator_links):
            name = a.get("title", f"Operator's {a} name not found")
            link = a.get("href", f"{a}. {name}'s link not found")

            pageURLS[i] = {
                "name": name,
                "link": link
            }

        return pageURLS
    
    else:
        return {}
    



 
def getURLS() -> str:

    # Get the number of pages from the utility function
    pages = getPageNumbers()
    operatorURLS = {}
    count = 1

    with Pool(3) as pool:  # Use 3 CPUs
        results = pool.map(fetchPageURLS, range(1, pages + 1))

    # Combine all page dictionaries and re-index keys globally
    for page_data in results:
        for operator in page_data.values():
            operatorURLS[count] = operator
            count += 1

    # Convert to JSON string before returning
    operatorURLS = json.dumps(operatorURLS, indent=2)

    return operatorURLS 





def saveToMongodb(data: Dict):
    """
    Save all operatorURLS into a single MongoDB document
    Returns the MongoDB inserted document ID
    """
    # Clear any existing data
    mongodb.collection.delete_many({})

    # Insert one document with all operator data
    result = mongodb.collection.insert_one({
        "type": "List of operators",
        "total": len(data),
        "operators": data  
    })

    inserted_id = result.inserted_id
    logging.info(f"Saved all operators into one document with _id: {inserted_id}")

    return inserted_id 


  


def main():
    operatorURLS = getURLS()
    id = saveToMongodb(operatorURLS)
    logging.info("Done!")

if __name__ == "__main__":
    main()