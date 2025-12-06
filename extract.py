from typing import List, Dict, Optional
import requests
import time
import logging
import os
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



class DogDataExtractor:
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.thedogapi.com/v1/breeds"
        self.api_key = os.environ.get("x-api-key")
        self.max_retries = 3
        self.timeout = 10
    
    def extract_data(self) -> List[Dict]:
        headers = {}
        if self.api_key:
            headers['x-api-key'] = self.api_key
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempting to fetch data (attempt {attempt + 1}/{self.max_retries})")
                response = requests.get(
                    self.base_url,
                    headers=headers,
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                logger.info(f"Successfully extracted {len(data)} dog breeds")
                return data
            
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout occurred on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("Max retries reached. Timeout error.")
                    raise
            
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error("Max retries reached. Connection error.")
                    raise
            
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error occurred: {e}")
                raise
            
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise
        
        return []