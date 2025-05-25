# data_collector.py

import requests
from bs4 import BeautifulSoup
import csv
import json
import logging # Use standard logging
from datetime import datetime
import os

# Import custom exceptions
from ..utils.custom_exceptions import DataCollectionError

# Get a logger for this module
logger = logging.getLogger(__name__)

class DataCollector:
    """Handles the collection of data from websites."""

    def __init__(self, output_directory="collected_data"):
        """
        Initializes the DataCollector.

        Args:
            output_directory (str): The directory where collected data will be stored.
        """
        self.output_directory = output_directory
        try:
            if not os.path.exists(self.output_directory):
                os.makedirs(self.output_directory)
        except OSError as e:
            logger.error(f"Failed to create output directory {self.output_directory}: {e}")
            raise DataCollectionError(f"Failed to create output directory {self.output_directory}: {e}")
            
        self.session = requests.Session()
        self.session.headers.update({
            # Standard User-Agent to avoid being blocked by simple checks
            # Users should be aware of the implications of User-Agent strings.
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 WebAnalysisTool/1.0"
        })
        logger.info(f"DataCollector initialized. Output directory: {self.output_directory}")

    def fetch_page(self, url):
        """
        Fetches the content of a given URL.

        Args:
            url (str): The URL to fetch.

        Returns:
            requests.Response: The response object if successful.
        Raises:
            DataCollectionError: If fetching or response validation fails.
        """
        try:
            logger.info(f"Fetching URL: {url}")
            response = self.session.get(url, timeout=15) # Increased timeout slightly
            response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
            
            logger.debug(f"Request Headers for {url}: {response.request.headers}")
            logger.debug(f"Response Headers for {url}: {response.headers}")
            logger.info(f"Successfully fetched {url} with status code: {response.status_code}")
            
            return response
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error fetching {url}: {e}")
            raise DataCollectionError(f"Timeout error fetching {url}: {e}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for {url}: {e}. Status code: {e.response.status_code}")
            raise DataCollectionError(f"HTTP error for {url}: {e}. Status code: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Generic error fetching {url}: {e}")
            raise DataCollectionError(f"Error fetching {url}: {e}")

    def parse_html(self, html_content):
        """
        Parses HTML content using BeautifulSoup.

        Args:
            html_content (str or bytes): The HTML content to parse.

        Returns:
            BeautifulSoup: The BeautifulSoup object.
        Raises:
            DataCollectionError: If HTML parsing fails.
        """
        try:
            soup = BeautifulSoup(html_content, "lxml")
            logger.info("HTML content parsed successfully.")
            return soup
        except Exception as e: # BeautifulSoup can raise various errors
            logger.error(f"Error parsing HTML: {e}")
            raise DataCollectionError(f"Error parsing HTML: {e}")

    def extract_metadata(self, soup):
        """
        Extracts metadata from a BeautifulSoup object.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object of the parsed page.

        Returns:
            dict: A dictionary containing extracted metadata.
        """
        metadata = {}
        if not soup:
            logger.warning("Soup object is None, cannot extract metadata.")
            return metadata

        try:
            title_tag = soup.find("title")
            metadata["title"] = title_tag.string.strip() if title_tag and title_tag.string else None

            description_tag = soup.find("meta", attrs={"name": "description"})
            metadata["description"] = description_tag["content"].strip() if description_tag and description_tag.has_attr("content") else None

            keywords_tag = soup.find("meta", attrs={"name": "keywords"})
            metadata["keywords"] = keywords_tag["content"].strip() if keywords_tag and keywords_tag.has_attr("content") else None
            
            author_tag = soup.find("meta", attrs={"name": "author"})
            metadata["author"] = author_tag["content"].strip() if author_tag and author_tag.has_attr("content") else None
            
            logger.info(f"Extracted metadata: {metadata}")
        except Exception as e:
            logger.error(f"Error during metadata extraction: {e}", exc_info=True)
            # Continue with what was extracted, or raise error depending on desired strictness
        return metadata

    def extract_links(self, soup, base_url):
        """
        Extracts all hyperlinks from a BeautifulSoup object.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object.
            base_url (str): The base URL of the page, for resolving relative links.

        Returns:
            list: A list of absolute URLs found on the page.
        """
        links = set() # Use a set to avoid duplicate links initially
        if not soup:
            logger.warning("Soup object is None, cannot extract links.")
            return []
        
        from urllib.parse import urljoin # Moved import here to keep it local if needed
        try:
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"].strip()
                if href and not href.startswith(("mailto:", "tel:", "javascript:")):
                    absolute_link = urljoin(base_url, href)
                    links.add(absolute_link)
            logger.info(f"Extracted {len(links)} unique links.")
        except Exception as e:
            logger.error(f"Error during link extraction: {e}", exc_info=True)
        return list(links)

    def extract_all_text(self, soup):
        """
        Extracts all visible text content from a BeautifulSoup object.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object.

        Returns:
            str: All extracted text, concatenated.
        """
        if not soup:
            logger.warning("Soup object is None, cannot extract text.")
            return ""
        try:
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            text = soup.get_text(separator=" ", strip=True)
            logger.info(f"Extracted text length: {len(text)} characters.")
            return text
        except Exception as e:
            logger.error(f"Error during text extraction: {e}", exc_info=True)
            return "" # Return empty string on error

    def _generate_filename(self, url, extension):
        """
        Generates a sanitized filename based on the URL and current timestamp.
        """
        try:
            domain = url.split("//")[-1].split("/")[0].replace(".", "_").replace(":", "_") # Sanitize port numbers too
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f") # Added microseconds for more uniqueness
            safe_domain = "".join(c if c.isalnum() or c in (".", "_") else "_" for c in domain)
            return os.path.join(self.output_directory, f"{safe_domain}_{timestamp}.{extension}")
        except Exception as e:
            logger.error(f"Error generating filename for URL {url}: {e}")
            # Fallback filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            return os.path.join(self.output_directory, f"error_filename_{timestamp}.{extension}")

    def save_data_to_csv(self, data_list, url, filename_prefix="web_extract"):
        """
        Saves a list of dictionaries to a CSV file.

        Args:
            data_list (list): A list of dictionaries to save.
            url (str): The URL from which data was collected, used for filename generation.
            filename_prefix (str): Prefix for the filename (currently not used in _generate_filename, but kept for compatibility).

        Returns:
            str: The path to the saved file.
        Raises:
            DataCollectionError: If saving to CSV fails.
        """
        if not data_list:
            logger.warning("No data provided to save to CSV.")
            raise DataCollectionError("No data to save to CSV.")
        
        filename = self._generate_filename(url, "csv")
        try:
            with open(filename, "w", newline="", encoding="utf-8") as csvfile:
                if not data_list: # Should be caught above, but double check
                    raise DataCollectionError("Cannot write empty data_list to CSV.")
                
                # Ensure all dicts have the same keys for DictWriter, or handle varying keys
                # For simplicity, assuming all dicts in data_list have similar structure or taking keys from the first.
                fieldnames = list(data_list[0].keys()) if isinstance(data_list[0], dict) else [f"column_{i}" for i in range(len(data_list[0]))]
                
                if isinstance(data_list[0], dict):
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data_list)
                else: # Assuming list of lists
                    writer = csv.writer(csvfile)
                    if fieldnames and not isinstance(data_list[0], dict): # Write header for list of lists if fieldnames were derived
                        # This part is a bit tricky if data_list is not list of dicts. 
                        # For now, we assume if it is not list of dicts, it is list of lists and we don't write a header unless explicitly passed.
                        pass # writer.writerow(fieldnames) # if header is desired for list of lists
                    writer.writerows(data_list if isinstance(data_list[0], list) else [[d] for d in data_list])
            logger.info(f"Data saved to CSV: {filename}")
            return filename
        except IOError as e:
            logger.error(f"IOError saving data to CSV {filename}: {e}")
            raise DataCollectionError(f"Failed to save data to CSV {filename}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving data to CSV {filename}: {e}", exc_info=True)
            raise DataCollectionError(f"Unexpected error saving data to CSV {filename}: {e}")

    def save_data_to_json(self, data, url, filename_prefix="web_extract_details"):
        """
        Saves data to a JSON file.

        Args:
            data (dict or list): The data to save.
            url (str): The URL from which data was collected, used for filename generation.
            filename_prefix (str): Prefix for the filename.

        Returns:
            str: The path to the saved file.
        Raises:
            DataCollectionError: If saving to JSON fails.
        """
        if not data:
            logger.warning("No data provided to save to JSON.")
            raise DataCollectionError("No data to save to JSON.")

        filename = self._generate_filename(url, "json")
        try:
            with open(filename, "w", encoding="utf-8") as jsonfile:
                json.dump(data, jsonfile, indent=4, ensure_ascii=False)
            logger.info(f"Data saved to JSON: {filename}")
            return filename
        except IOError as e:
            logger.error(f"IOError saving data to JSON {filename}: {e}")
            raise DataCollectionError(f"Failed to save data to JSON {filename}: {e}")
        except TypeError as e: # Handle non-serializable data
            logger.error(f"TypeError: Data not JSON serializable for {filename}: {e}")
            raise DataCollectionError(f"Data not JSON serializable for {filename}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving data to JSON {filename}: {e}", exc_info=True)
            raise DataCollectionError(f"Unexpected error saving data to JSON {filename}: {e}")

    def collect_and_store(self, url, collect_text=True, collect_links=True, store_csv=True, store_json=True):
        """
        Orchestrates the collection and storage of data from a URL.

        Args:
            url (str): The URL to process.
            collect_text (bool): Whether to extract all text.
            collect_links (bool): Whether to extract all links.
            store_csv (bool): Whether to save extracted data to CSV.
            store_json (bool): Whether to save extracted data (metadata primarily) to JSON.

        Returns:
            dict: A dictionary containing paths to saved files and extracted data.
        Raises:
            DataCollectionError: If a critical step in collection or storage fails.
        """
        logger.info(f"Starting collection and storage process for URL: {url}")
        results = {
            "url": url,
            "metadata": None,
            "text_content_preview": None,
            "full_text_content_path": None, # Path to separate file if text is too long
            "links": None,
            "csv_filepath": None,
            "json_filepath": None,
            "http_log": {
                "request_headers": None,
                "response_headers": None,
                "status_code": None
            }
        }

        try:
            response = self.fetch_page(url)
            results["http_log"]["request_headers"] = dict(response.request.headers)
            results["http_log"]["response_headers"] = dict(response.headers)
            results["http_log"]["status_code"] = response.status_code

            soup = self.parse_html(response.content)
            
            metadata = self.extract_metadata(soup)
            results["metadata"] = metadata

            # Prepare data for CSV - typically a flat structure or simple list of dicts
            # For this example, we save metadata and optionally link/text summaries in one CSV row.
            csv_row_data = {**metadata} # Start with metadata
            csv_row_data["url"] = url # Add URL to the CSV data
            csv_row_data["collection_timestamp"] = datetime.now().isoformat()

            text_content = None
            if collect_text:
                text_content = self.extract_all_text(soup)
                results["text_content_preview"] = (text_content[:500] + "...") if text_content and len(text_content) > 500 else text_content
                csv_row_data["text_preview"] = results["text_content_preview"]
                # Optionally save full text to a separate file if very long
                # text_filepath = self._generate_filename(url, "txt")
                # with open(text_filepath, "w", encoding="utf-8") as f:
                # f.write(text_content)
                # results["full_text_content_path"] = text_filepath

            if collect_links:
                # Ensure base_url is correctly derived for urljoin
                parsed_url = urlparse(response.url) # Use response.url as it might have followed redirects
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                links = self.extract_links(soup, base_url)
                results["links"] = links
                csv_row_data["extracted_links_count"] = len(links)
                # Storing all links in a single CSV cell can be problematic. Consider storing a sample or count.
                csv_row_data["sample_links"] = json.dumps(links[:5]) # Store first 5 links as JSON string
            
            # Comprehensive data for JSON storage
            json_data_to_store = {
                "url": url,
                "collection_timestamp": datetime.now().isoformat(),
                "metadata": metadata,
                "http_info": results["http_log"],
                "links": results["links"],
                # Full text can be large, consider if it should always be in JSON or linked as a file path
                "full_text": text_content if collect_text else None 
            }

            if store_csv and csv_row_data:
                # CSV expects a list of dictionaries
                csv_path = self.save_data_to_csv([csv_row_data], url, filename_prefix="web_extract")
                results["csv_filepath"] = csv_path
            
            if store_json and json_data_to_store:
                json_path = self.save_data_to_json(json_data_to_store, url, filename_prefix="web_extract_details")
                results["json_filepath"] = json_path
                
            logger.info(f"Successfully processed and stored data for {url}.")
            return results

        except DataCollectionError as e:
            logger.error(f"DataCollectionError during processing of {url}: {e}", exc_info=True)
            # results dictionary will contain partial data if any step succeeded before failure
            # The error is re-raised to be handled by the caller (e.g., GUI)
            raise
        except Exception as e:
            logger.critical(f"Unexpected critical error during processing of {url}: {e}", exc_info=True)
            raise DataCollectionError(f"An unexpected critical error occurred while processing {url}: {e}")

# Example Usage (for testing purposes, will be called from GUI later)
if __name__ == "__main__":
    # This setup should ideally be in the main application entry point
    from ..utils.logger_config import setup_logging
    setup_logging(logging.DEBUG) # Set to DEBUG for detailed output during testing

    # Create a test output directory relative to this script for easy cleanup
    script_dir = os.path.dirname(os.path.abspath(__file__))
    test_output_dir = os.path.join(script_dir, "..", "..", "test_collected_data_output") # Up two levels to project root, then into test_collected_data
    
    logger.info(f"Test output directory will be: {test_output_dir}")

    collector = DataCollector(output_directory=test_output_dir)
    
    test_url = "http://example.com"
    
    logger.info(f"--- Collecting data from {test_url} (main test execution) ---")
    try:
        collection_results = collector.collect_and_store(test_url, collect_text=True, collect_links=True, store_csv=True, store_json=True)
        
        if collection_results:
            logger.info("--- Collection Summary ---")
            logger.info(f"URL: {collection_results.get("url")}")
            logger.info(f"Metadata: {collection_results.get("metadata")}")
            logger.info(f"Text Preview: {collection_results.get("text_content_preview")}")
            logger.info(f"Extracted Links (first 5): {collection_results.get("links", [])[:5]}")
            logger.info(f"CSV saved to: {collection_results.get("csv_filepath")}")
            logger.info(f"JSON saved to: {collection_results.get("json_filepath")}")
            logger.info(f"HTTP Status: {collection_results.get("http_log", {}).get("status_code")}")

            if collection_results.get("json_filepath") and os.path.exists(collection_results.get("json_filepath")):
                with open(collection_results["json_filepath"], "r", encoding="utf-8") as f:
                    loaded_data = json.load(f)
                    logger.info("--- Loaded JSON Data (sample) ---")
                    logger.info(f"Title from loaded JSON: {loaded_data.get("metadata", {}).get("title")}")
            else:
                logger.warning("JSON file was not created or path is incorrect.")
        else:
            logger.warning("Collection did not return results.")
            
    except DataCollectionError as e:
        logger.error(f"MAIN TEST: Data collection failed for {test_url}: {e}")
    except Exception as e:
        logger.error(f"MAIN TEST: An unexpected error occurred: {e}", exc_info=True)

    # Test with a non-existent URL to check error handling
    non_existent_url = "http://thissitedefinitelydoesnotexist12345.com"
    logger.info(f"--- Attempting to collect data from non-existent URL: {non_existent_url} ---")
    try:
        collector.collect_and_store(non_existent_url)
    except DataCollectionError as e:
        logger.error(f"MAIN TEST: Successfully caught DataCollectionError for non-existent URL: {e}")
    except Exception as e:
        logger.error(f"MAIN TEST: Unexpected error for non-existent URL: {e}", exc_info=True)

