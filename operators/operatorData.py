import time
import logging

# Local import
from urls import getURLS, saveToMongodb
from mongodb import collection, operatorCollection

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
    else:
        logging.error("Operatord data not found..")

    return operatorData