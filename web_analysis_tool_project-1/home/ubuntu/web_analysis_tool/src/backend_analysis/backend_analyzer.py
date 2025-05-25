# backend_analyzer.py

import builtwith
import logging # Use standard logging
import json
import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

# Import custom exceptions
from ..utils.custom_exceptions import BackendAnalysisError

# Get a logger for this module
logger = logging.getLogger(__name__)

class BackendAnalyzer:
    """Analyzes backend characteristics of a website based on collected data."""

    def __init__(self):
        """Initializes the BackendAnalyzer."""
        logger.info("BackendAnalyzer initialized.")

    def identify_technologies(self, url):
        """
        Identifies web technologies used by a given URL.

        Args:
            url (str): The URL to analyze.

        Returns:
            dict: A dictionary of identified technologies.
        Raises:
            BackendAnalysisError: If technology identification fails.
        """
        logger.info(f"Identifying technologies for {url}")
        try:
            # Ensure URL has a scheme for builtwith
            if not url.startswith("http://") and not url.startswith("https://"):
                # Prepend http:// if no scheme is present. builtwith might handle this, 
                # but being explicit can avoid potential issues.
                url = "http://" + url 
            
            tech_info = builtwith.parse(url)
            if not tech_info:
                logger.warning(f"No technologies identified by builtwith for {url}. This might be normal for some sites or indicate an issue.")
            else:
                logger.info(f"Technologies identified for {url}: {tech_info}")
            return tech_info if tech_info else {}
        except Exception as e:
            logger.error(f"Error identifying technologies for {url}: {e}", exc_info=True)
            raise BackendAnalysisError(f"Failed to identify technologies for {url}: {e}")

    def analyze_authentication(self, soup, response_headers):
        """
        Performs a basic analysis of authentication mechanisms based on HTML forms and response headers.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object of the page.
            response_headers (dict): The HTTP response headers, keys should be lowercased for consistent access.

        Returns:
            dict: Analysis results regarding authentication.
        """
        logger.info("Analyzing authentication mechanisms.")
        auth_analysis = {
            "login_forms_found": False,
            "form_details": [],
            "cookies_used": False,
            "session_cookies_likely": False,
            "http_auth_headers_present": False,
            "auth_header_details": None,
            "jwt_likely": False
        }

        if not soup:
            logger.warning("Soup object is None, cannot analyze HTML for authentication clues.")
            # Continue with header analysis if possible

        if soup:
            try:
                # Check for login forms (more specific selectors might be needed)
                login_forms = soup.find_all("form", attrs={"action": re.compile(r"login|auth|signin|session", re.IGNORECASE)})
                # Also check for forms with password fields as a strong indicator
                password_input_forms = soup.find_all("form", lambda tag: tag.find("input", attrs={"type": "password"}))
                
                all_potential_login_forms = list(set(login_forms + password_input_forms))

                if all_potential_login_forms:
                    auth_analysis["login_forms_found"] = True
                    for form in all_potential_login_forms:
                        form_detail = {"action": form.get("action", "N/A"), "method": form.get("method", "GET").upper()}
                        inputs = []
                        for input_tag in form.find_all("input"):
                            inputs.append({
                                "name": input_tag.get("name"), 
                                "type": input_tag.get("type", "text")
                            })
                        form_detail["inputs"] = inputs
                        auth_analysis["form_details"].append(form_detail)
            except Exception as e:
                logger.error(f"Error analyzing HTML forms for authentication: {e}", exc_info=True)

        # Standardize header keys to lowercase for consistent checking
        normalized_headers = {k.lower(): v for k, v in response_headers.items()} if response_headers else {}

        try:
            if "set-cookie" in normalized_headers:
                auth_analysis["cookies_used"] = True
                cookies_header = normalized_headers["set-cookie"]
                # Ensure cookies_header is a string before calling lower()
                if isinstance(cookies_header, list):
                    cookies_header = "; ".join(cookies_header) # Join if it's a list of cookie strings
                
                if any(c_name in cookies_header.lower() for c_name in ["sessionid", "sessid", "jsessionid", "phpsessid", "asp.net_sessionid", "connect.sid"]):
                    auth_analysis["session_cookies_likely"] = True
            
            if "authorization" in normalized_headers or "www-authenticate" in normalized_headers:
                auth_analysis["http_auth_headers_present"] = True
                auth_analysis["auth_header_details"] = normalized_headers.get("www-authenticate", normalized_headers.get("authorization"))
            
            # Check for JWT patterns in common headers
            jwt_patterns = ["bearer ", "jwt "]
            for header_name in ["authorization", "x-auth-token", "x-access-token"]:
                header_value = normalized_headers.get(header_name, "")
                if any(pattern in header_value.lower() for pattern in jwt_patterns):
                    auth_analysis["jwt_likely"] = True
                    break # Found JWT evidence
        except Exception as e:
            logger.error(f"Error analyzing headers for authentication: {e}", exc_info=True)

        logger.info(f"Authentication analysis results: {auth_analysis}")
        return auth_analysis

    def discover_api_endpoints(self, soup, base_url, page_content_str=None):
        """
        Tries to discover potential API endpoints from script tags, links, and page content.

        Args:
            soup (BeautifulSoup): The BeautifulSoup object of the page.
            base_url (str): The base URL of the website.
            page_content_str (str, optional): The raw HTML/JS content as a string for regex search.

        Returns:
            list: A list of unique, absolute potential API endpoint URLs.
        """
        logger.info(f"Discovering potential API endpoints for base URL: {base_url}")
        endpoints = set()

        if not base_url:
            logger.error("Base URL is required for API endpoint discovery.")
            return []

        # Regex patterns for API paths in JavaScript or text content
        # More comprehensive patterns can be added here
        api_regex_patterns = [
            r"([\"\\]["\"]?/api(?:/[\w\-/\.\{\}]+)+[\"\\]["\"])_?",  # /api/v1/users, /api/resource.json
            r"([\"\\]["\"]?/rest(?:/[\w\-/\.\{\}]+)+[\"\\]["\"])_?", # /rest/v2/items
            r"([\"\\]["\"]?/graphql[\"\\]["\"])_?", # /graphql
            r"(?:fetch|axios\.get|axios\.post|\$\.ajax|\$\.get|\$\.post)\s*\(\s*["\"]([^"\"]+)["\"]", # JS calls
            r"(?:apiUrl|apiBaseUrl|endpoint)\s*[:=]\s*["\"]([^"\"]+)["\"]" # JS variables
        ]

        content_to_search = ""
        if page_content_str:
            content_to_search += page_content_str
        if soup:
            # Extract script tag contents for more targeted search
            for script_tag in soup.find_all("script"):
                if script_tag.string:
                    content_to_search += script_tag.string + "\n"
        
        try:
            for pattern in api_regex_patterns:
                # Find all non-overlapping matches in the string
                found_matches = re.findall(pattern, content_to_search, re.IGNORECASE)
                for match in found_matches:
                    # If the pattern has capturing groups, re.findall returns tuples or list of strings
                    # We are interested in the captured path itself.
                    path_candidate = match if isinstance(match, str) else match[0] # Adjust based on regex group structure
                    path_candidate = path_candidate.strip("\"\\' ") # Clean quotes and spaces
                    
                    if path_candidate.startswith(("/", "http://", "https://")):
                        try:
                            abs_url = urljoin(base_url, path_candidate)
                            # Basic validation: ensure it looks like a plausible API path
                            if "api" in abs_url.lower() or "rest" in abs_url.lower() or "graphql" in abs_url.lower() or any(p_match in path_candidate for p_match in ["/v1/", "/v2/"]):
                                endpoints.add(abs_url)
                        except ValueError as ve:
                            logger.debug(f"Could not form absolute URL from candidate \"{path_candidate}\" with base \"{base_url}\": {ve}")

            # Also check <a> tags for explicit API links (e.g., API documentation)
            if soup:
                for a_tag in soup.find_all("a", href=True):
                    href = a_tag["href"].strip()
                    if "api" in href.lower() or "rest" in href.lower() or "graphql" in href.lower() or "swagger" in href.lower() or "openapi" in href.lower():
                        try:
                            abs_url = urljoin(base_url, href)
                            endpoints.add(abs_url)
                        except ValueError as ve:
                             logger.debug(f"Could not form absolute URL from <a> tag href \"{href}\" with base \"{base_url}\": {ve}")

        except Exception as e:
            logger.error(f"Error during API endpoint discovery: {e}", exc_info=True)
            # Do not raise, return what has been found so far

        logger.info(f"Discovered {len(endpoints)} potential API endpoints: {list(endpoints)}")
        return list(endpoints)

    def generate_site_structure_map(self, links, base_url):
        """
        Generates a simple textual or dictionary representation of the site structure based on internal links.

        Args:
            links (list): A list of absolute URLs found on the site.
            base_url (str): The base URL of the website to filter internal links.

        Returns:
            dict: A dictionary representing the site structure.
        """
        logger.info(f"Generating site structure map for base URL: {base_url}")
        structure = {}
        if not base_url:
            logger.error("Base URL is required for site structure mapping.")
            return structure
            
        try:
            parsed_base = urlparse(base_url)
            if not parsed_base.scheme or not parsed_base.netloc:
                logger.error(f"Invalid base_url for site structure mapping: {base_url}")
                return structure

            for link in links:
                if not link: continue
                try:
                    parsed_link = urlparse(link)
                    # Ensure it is an internal link and has a path
                    if parsed_link.netloc == parsed_base.netloc and parsed_link.path and parsed_link.path != "/":
                        # Normalize path: remove trailing slash unless it is the only slash
                        path = parsed_link.path
                        if path.endswith("/") and len(path) > 1:
                            path = path[:-1]
                        
                        path_segments = [seg for seg in path.split("/") if seg] # Filter out empty segments
                        
                        current_level = structure
                        for i, segment in enumerate(path_segments):
                            is_last_segment = (i == len(path_segments) - 1)
                            
                            if segment not in current_level:
                                current_level[segment] = "[page]" if is_last_segment else {}
                            elif not isinstance(current_level[segment], dict):
                                # If it was marked as a page but now we find sub-paths, convert to dict
                                if not is_last_segment:
                                    current_level[segment] = {"[page_marker]": True} # Mark that this path itself is also a page
                                # else, it is already a page, do nothing to overwrite
                            
                            if isinstance(current_level[segment], dict):
                                current_level = current_level[segment]
                            # If it is a page string and we are not at the last segment, it means we have a conflict
                            # e.g. /users (page) and /users/profile (sub-page). The dict conversion above handles this.
                except ValueError as ve:
                    logger.warning(f"Could not parse link {link} during site structure mapping: {ve}")
                    continue # Skip malformed links
        except Exception as e:
            logger.error(f"Error generating site structure map for {base_url}: {e}", exc_info=True)
            # Return partially built structure or empty if critical error

        logger.info(f"Site structure map generated for {base_url}. Root items: {len(structure)}")
        return structure

    def analyze_all(self, url, html_content_str, response_headers, collected_links):
        """
        Performs a comprehensive backend analysis using all available methods.

        Args:
            url (str): The primary URL of the website analyzed.
            html_content_str (str): The HTML content of the main page as a string.
            response_headers (dict): The HTTP response headers from the main page request.
            collected_links (list): A list of links collected from the website.

        Returns:
            dict: A dictionary containing all analysis results.
        Raises:
            BackendAnalysisError: If a critical part of the analysis fails.
        """
        logger.info(f"Starting comprehensive backend analysis for URL: {url}")
        analysis_results = {
            "url": url,
            "technologies": None,
            "authentication_analysis": None,
            "api_endpoints": None,
            "site_structure": None
        }

        try:
            analysis_results["technologies"] = self.identify_technologies(url)
        except BackendAnalysisError as e:
            logger.warning(f"Technology identification failed for {url}: {e}. Continuing analysis.")
            analysis_results["technologies"] = {"error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error during technology identification for {url}: {e}", exc_info=True)
            analysis_results["technologies"] = {"error": f"Unexpected error: {str(e)}"}

        soup = None
        if html_content_str:
            try:
                soup = BeautifulSoup(html_content_str, "lxml")
            except Exception as e:
                logger.error(f"Failed to parse HTML for backend analysis of {url}: {e}", exc_info=True)
                # Some analyses might still run without soup, or with partial data
        
        try:
            analysis_results["authentication_analysis"] = self.analyze_authentication(soup, response_headers or {})
        except Exception as e: # Catch any unexpected error from this specific analysis
            logger.error(f"Authentication analysis failed for {url}: {e}", exc_info=True)
            analysis_results["authentication_analysis"] = {"error": f"Unexpected error: {str(e)}"}

        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        try:
            analysis_results["api_endpoints"] = self.discover_api_endpoints(soup, base_url, page_content_str=html_content_str)
        except Exception as e:
            logger.error(f"API endpoint discovery failed for {url}: {e}", exc_info=True)
            analysis_results["api_endpoints"] = {"error": f"Unexpected error: {str(e)}"}

        try:
            analysis_results["site_structure"] = self.generate_site_structure_map(collected_links or [], base_url)
        except Exception as e:
            logger.error(f"Site structure map generation failed for {url}: {e}", exc_info=True)
            analysis_results["site_structure"] = {"error": f"Unexpected error: {str(e)}"}

        logger.info(f"Comprehensive backend analysis completed for {url}.")
        return analysis_results

# Example Usage (for testing purposes)
if __name__ == "__main__":
    # This setup should ideally be in the main application entry point
    # For standalone testing of this module, we set it up here.
    from ..utils.logger_config import setup_logging
    setup_logging(logging.DEBUG) # Set to DEBUG for detailed output

    analyzer = BackendAnalyzer()

    # Mock inputs (these would typically come from DataCollector)
    test_url = "http://example.com"
    mock_html_content = """
    <html><head><title>Test Page</title></head>
    <body>
        <h1>Welcome to Example</h1>
        <p>Some content here. Visit our <a href=\"/about-us.html\">About Us</a> page.</p>
        <form action=\"/login\" method=\"post\">
            <input type=\"text\" name=\"username\" />
            <input type=\"password\" name=\"password\" />
            <input type=\"submit\" value=\"Login\" />
        </form>
        <a href=\"/api/v1/users\">Users API</a>
        <script>
            var apiUrl = \"/api/v2/data\";
            fetch(\"/api/v1/items\");
        </script>
    </body></html>
    """
    mock_response_headers = {
        "Content-Type": "text/html; charset=UTF-8",
        "Set-Cookie": "sessionid=abcdef12345; path=/; HttpOnly",
        "X-Powered-By": "ExampleFramework/1.0"
    }
    mock_collected_links = [
        "http://example.com/about-us.html", 
        "http://example.com/contact", 
        "http://example.com/products/item1",
        "http://example.com/api/v1/users", # From an <a> tag
        "http://another-domain.com/external_link"
    ]

    logger.info(f"--- Running BackendAnalyzer Test for {test_url} ---")
    
    try:
        full_analysis = analyzer.analyze_all(test_url, mock_html_content, mock_response_headers, mock_collected_links)
        
        logger.info("\n--- Full Analysis Results ---")
        # Pretty print the JSON-like dictionary for readability in logs
        logger.info(json.dumps(full_analysis, indent=2))

        # Test with a URL that might not be easily parsed by builtwith or has no clear tech
        # test_url_simple = "https://www.iana.org"
        # logger.info(f"\n--- Running BackendAnalyzer Test for {test_url_simple} (minimal HTML) ---")
        # For this, we would need a real fetch, which DataCollector does.
        # Here, we simulate minimal data.
        # tech_simple = analyzer.identify_technologies(test_url_simple)
        # logger.info(f"Technologies for {test_url_simple}: {tech_simple}")

    except BackendAnalysisError as e:
        logger.error(f"MAIN TEST: Backend analysis failed: {e}")
    except Exception as e:
        logger.error(f"MAIN TEST: An unexpected error occurred: {e}", exc_info=True)

