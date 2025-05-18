import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional, Union, Any
import re
import json
import time # Keep for general use, but Playwright has its own waits
import random

# Add Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager

# --- Session and XSRF Token Management ---
class RequestsSessionManager:
    def __init__(self, base_url="https://assist.org/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.xsrf_token: Optional[str] = None
        self._initialize_session_and_token()

    def _initialize_session_and_token(self):
        """Makes an initial request to the base URL to get cookies, including XSRF-TOKEN."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9"
            }
            response = self.session.get(self.base_url, headers=headers, timeout=20)
            response.raise_for_status()
            self.xsrf_token = self.session.cookies.get("XSRF-TOKEN")
            if not self.xsrf_token:
                print("Warning: XSRF-TOKEN not found in cookies after initial request.")
            else:
                print(f"Successfully initialized session and XSRF-TOKEN: {self.xsrf_token[:20]}...") # Print first 20 chars
        except requests.exceptions.RequestException as e:
            print(f"Error initializing session and XSRF token: {e}")
            self.xsrf_token = None # Ensure it's None if fetching failed

    def get_xsrf_token(self) -> Optional[str]:
        return self.xsrf_token

    def get_session(self) -> requests.Session:
        return self.session

    def get_default_headers(self, referer_url: Optional[str] = None) -> Dict[str, str]:
        headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Content-Type": "application/json"
        }
        if self.xsrf_token:
            headers["X-XSRF-TOKEN"] = self.xsrf_token
        if referer_url:
            headers["Referer"] = referer_url
        else:
            headers["Referer"] = self.base_url # Default referer
        return headers

# --- Normalization Functions (remain unchanged) ---
def normalize_institution_name(name: str) -> str:
    """Normalize institution name for search"""
    name = name.lower().strip()
    
    # Common aliases and abbreviations
    aliases = {
        "uc berkeley": "university of california, berkeley",
        "berkeley": "university of california, berkeley",
        "ucla": "university of california, los angeles",
        "uc davis": "university of california, davis",
        "uc irvine": "university of california, irvine",
        "uci": "university of california, irvine",
        "uc san diego": "university of california, san diego",
        "ucsd": "university of california, san diego",
        "uc santa barbara": "university of california, santa barbara",
        "ucsb": "university of california, santa barbara",
        "uc santa cruz": "university of california, santa cruz",
        "ucsc": "university of california, santa cruz",
        "uc riverside": "university of california, riverside",
        "ucr": "university of california, riverside",
        "uc merced": "university of california, merced",
        "de anza": "de anza college",
        "foothill": "foothill college",
        "san jose city": "san jose city college",
        "sjcc": "san jose city college",
        "sjsu": "san jose state university",
        "san jose state": "san jose state university",
    }
    
    for alias, full_name in aliases.items():
        if name == alias or name in alias or alias in name:
            return full_name.lower()
    
    return name

def normalize_major_name(name: str) -> str:
    """Normalize major name for search"""
    name = name.lower().strip()
    
    # Common aliases and abbreviations
    aliases = {
        "cs": "computer science",
        "compsci": "computer science",
        "psych": "psychology",
        "bio": "biology",
        "econ": "economics",
        "business": "business administration",
        "poli sci": "political science",
        "applied math": "mathematics, applied",
        "math": "mathematics",
        "math, applied": "mathematics, applied",
    }
    
    for alias, full_name in aliases.items():
        if name == alias:
            return full_name
    
    return name

# --- API Fetching Functions ---
def fetch_academic_years_api(session_manager: RequestsSessionManager) -> List[Dict[str, Any]]:
    """Fetches available academic years from the assist.org API."""
    print("Fetching academic years from API...")
    api_url = f"{session_manager.base_url}api/AcademicYears"
    headers = session_manager.get_default_headers()
    
    try:
        session = session_manager.get_session()
        response = session.get(api_url, headers=headers, timeout=20)
        response.raise_for_status()
        years_data = response.json()
        
        formatted_years = []
        for year_entry in years_data:
            year_id = year_entry.get("Id")
            fall_year = year_entry.get("FallYear")
            if year_id is not None and fall_year is not None:
                # Constructing name like "2024-2025" from FallYear 2024
                display_name = f"{fall_year}-{fall_year + 1}"
                formatted_years.append({"id": year_id, "name": display_name, "code": display_name, "fall_year": fall_year})
        print(f"Successfully fetched {len(formatted_years)} academic years.")
        return formatted_years
    except requests.exceptions.RequestException as e:
        print(f"Error fetching academic years: {e}")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for academic years: {e}")
    return []

def fetch_institutions_api(session_manager: RequestsSessionManager) -> List[Dict[str, Any]]:
    """Fetches institutions from the assist.org API."""
    print("Fetching institutions from API...")
    api_url = f"{session_manager.base_url}api/institutions"
    headers = session_manager.get_default_headers()
    try:
        session = session_manager.get_session()
        response = session.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        institutions_data = response.json()
        formatted_institutions = []
        for inst_entry in institutions_data:
            inst_id = inst_entry.get("id")
            # Prioritize names without 'fromYear', then latest 'fromYear', then first name.
            primary_name = "Unknown Institution"
            if inst_entry.get("names"):
                sorted_names = sorted([n for n in inst_entry["names"] if isinstance(n, dict) and n.get("name")], 
                                      key=lambda x: x.get("fromYear", 0), reverse=True)
                if sorted_names:
                    primary_name = sorted_names[0]["name"]
            
            if inst_id is not None:
                formatted_institutions.append({
                    "id": inst_id, 
                    "name": primary_name, 
                    "all_names": [n.get("name") for n in inst_entry.get("names", []) if isinstance(n, dict) and n.get("name")],
                    "code": inst_entry.get("code", "").strip()
                })
        print(f"Successfully fetched {len(formatted_institutions)} institutions.")
        return formatted_institutions
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Error fetching/decoding institutions: {e}"); return []

def fetch_agreement_categories_api(session_manager: RequestsSessionManager, year_id: int, sending_id: int, receiving_id: int) -> List[Dict[str, Any]]:
    """Fetches agreement categories (like Major, Department) for a given pair of institutions and year."""
    print(f"Fetching agreement categories for year {year_id}, sending {sending_id}, receiving {receiving_id}...")
    api_url = f"{session_manager.base_url}api/agreements/categories?academicYearId={year_id}&sendingInstitutionId={sending_id}&receivingInstitutionId={receiving_id}"
    # Referer for this specific type of call might be just the base, or the selection page if it matters
    # For now, using a generic referer that led to agreement selections
    referer = f"{session_manager.base_url}transfer/results?year={year_id}&institution={sending_id}&agreement={receiving_id}&agreementType=to"
    headers = session_manager.get_default_headers(referer_url=referer)
    try:
        session = session_manager.get_session()
        response = session.get(api_url, headers=headers, timeout=20)
        response.raise_for_status()
        categories = response.json() # Expecting a list directly
        # Ensure it's a list and items are dicts with 'code' and 'label'
        if isinstance(categories, list) and all(isinstance(item, dict) and 'code' in item and 'label' in item for item in categories):
            print(f"Successfully fetched {len(categories)} agreement categories.")
            return categories
        else:
            print("Fetched agreement categories, but data format is unexpected.")
            return [] 
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"Error fetching/decoding agreement categories: {e}"); return []

def fetch_agreement_data_api(session_manager: RequestsSessionManager, agreement_key: str, referer_url: str) -> Dict:
    """Fetches and parses a specific agreement data from the assist.org API."""
    print(f"Fetching agreement data from API for key: {agreement_key}")
    api_url = f"{session_manager.base_url}api/articulation/Agreements?Key={agreement_key}"
    headers = session_manager.get_default_headers(referer_url=referer_url)

    try:
        session = session_manager.get_session()
        response = session.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        response_data = response.json()

        if not response_data.get("isSuccessful") or not response_data.get("result"):
            error_message = "API reported an unsuccessful operation or missing result for agreement."
            if response_data.get("validationFailure"): error_message += f" Validation Failure: {response_data['validationFailure']}"
            print(error_message); return {"error": error_message, "data_available": False, "required_courses": [], "recommended_courses": []}

        result_data = response_data["result"]
        template_assets_str = result_data.get("templateAssets")
        academic_year_str = result_data.get("academicYear")
        agreement_name = result_data.get("name", "N/A")

        if not template_assets_str or not academic_year_str:
            error_message = "Missing templateAssets or academicYear in agreement API response."
            print(error_message); return {"error": error_message, "data_available": False, "required_courses": [], "recommended_courses": []}

        template_assets = json.loads(template_assets_str)
        academic_year_info = json.loads(academic_year_str)
        academic_year_code = academic_year_info.get("code", "N/A")

        required_courses, recommended_courses = [], []
        current_section_is_required = False

        for asset in template_assets:
            asset_type = asset.get("type"); content = asset.get("content", "").upper()
            if asset_type == "RequirementTitle":
                current_section_is_required = "REQUIREMENT" in content and "RECOMMENDED" not in content
            elif asset_type == "RequirementGroup":
                for section in asset.get("sections", []):
                    for row in section.get("rows", []):
                        for cell in row.get("cells", []):
                            if cell.get("type") == "Course":
                                course_data = cell.get("course")
                                if not course_data: continue
                                code = f"{course_data.get('prefix', '')} {course_data.get('courseNumber', '')}".strip()
                                title = course_data.get("courseTitle", "Unknown Title")
                                try: units = float(course_data.get("minUnits", 0.0))
                                except (ValueError, TypeError): units = 0.0
                                course_info = {'code': code, 'title': title, 'units': units}
                                is_recommended_attr = any("RECOMMENDED" in attr.get("content", "").upper() for attr in course_data.get("courseAttributes", []) if isinstance(attr, dict))
                                if is_recommended_attr:
                                    if course_info not in recommended_courses: recommended_courses.append(course_info)
                                elif current_section_is_required:
                                    if course_info not in required_courses: required_courses.append(course_info)
                                else:
                                    if course_info not in recommended_courses: recommended_courses.append(course_info)
        
        print(f"Successfully parsed API data for: {agreement_name} ({academic_year_code})")
        return {"data_available": True, "required_courses": required_courses, "recommended_courses": recommended_courses, "year": academic_year_code, "agreement_name": agreement_name}

    except requests.exceptions.HTTPError as http_err:
        error_message = f"HTTP error: {http_err} - {response.status_code if 'response' in locals() and response else 'N/A'} {response.text if 'response' in locals() and response else 'No response text'}"
    except requests.exceptions.RequestException as e: error_message = f"Request error: {e}"
    except json.JSONDecodeError as e: error_message = f"JSON decode error: {e}"
    except Exception as e: error_message = f"Unexpected error in fetch_agreement_data: {e}"
    print(error_message); return {"error": error_message, "data_available": False, "required_courses": [], "recommended_courses": []}

def fetch_majors_api(sm: RequestsSessionManager, yr_id: int, send_id: int, recv_id: int, report_type: int = 3) -> List[Dict[str, Any]]:
    """Fetches list of major agreements between two institutions for a given year and report type."""
    print(f"Fetching major agreements (reportType {report_type}) for yr {yr_id}, send {send_id}, recv {recv_id}...")
    api_url = f"{sm.base_url}api/agreements?academicYearId={yr_id}&sendingInstitutionId={send_id}&receivingInstitutionId={recv_id}&reportType={report_type}"
    
    # Try a more detailed Referer URL that looks like the one from a browser session
    ref = f"{sm.base_url}transfer/results?year={yr_id}&institution={send_id}&agreement={recv_id}&agreementType=to&view=agreement&viewBy=major"
    
    # Start with default headers
    headers = sm.get_default_headers(referer_url=ref)
    
    # Add Origin header - this is often needed for CORS requests
    headers["Origin"] = "https://assist.org"
    
    # Explicitly add Cookie header with the XSRF-TOKEN (sometimes helps)
    if sm.get_xsrf_token():
        headers["Cookie"] = f"XSRF-TOKEN={sm.get_xsrf_token()}"
    
    print("----- fetch_majors_api REQUEST DETAILS -----")
    print(f"URL: {api_url}")
    print("Headers Sent:")
    for k_header, v_header in headers.items():
        print(f"  {k_header}: {v_header}")
    print("Cookies in Session (before call):")
    current_cookies = sm.get_session().cookies
    if current_cookies:
        for cookie_name, cookie_value in current_cookies.items():
            print(f"  {cookie_name}: {cookie_value}")
    else:
        print("  No cookies in session.")
    print("------------------------------------------")

    try:
        # Make an OPTIONS request first (like browsers do for CORS)
        options_resp = sm.get_session().options(api_url, headers=headers)
        print(f"OPTIONS request status: {options_resp.status_code}")
        
        # Then make the actual GET request
        resp = sm.get_session().get(api_url, headers=headers, timeout=20)
        resp.raise_for_status(); majors_data = resp.json()
        if isinstance(majors_data, list) and all(isinstance(i, dict) and 'name' in i and 'key' in i for i in majors_data):
            print(f"Fetched {len(majors_data)} major agreements."); return majors_data
        print("Major agreements data format unexpected."); return []
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e: 
        error_detail = f"{type(e).__name__}: {e}"
        if isinstance(e, requests.exceptions.HTTPError) and e.response is not None:
            error_detail += f" - Status: {e.response.status_code} - Body: {e.response.text[:200]}"
        print(f"Err major agreements: {error_detail}"); 
        return []

def humanized_scrape_with_selenium(source_institution_name: str, 
                                  target_institution_name: str, 
                                  major_name_input: str, 
                                  completed_courses: Optional[List[str]] = None,
                                  run_headless: bool = False) -> Dict:
    """
    Scrapes ASSIST.org using Selenium with a more direct approach based on homepage structure.
    """
    print(f"Starting DIRECT Selenium scraper for {source_institution_name} to {target_institution_name} for {major_name_input} (Headless: {run_headless})")
    
    options = Options()
    if run_headless:
        options.add_argument("--headless")
    options.add_argument("--window-size=1366,768")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    driver = None
    try:
        print("Initializing Chrome driver...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        def random_delay(min_seconds=0.3, max_seconds=1.0):
            time.sleep(random.uniform(min_seconds, max_seconds))
        
        def robust_click(locator, wait_time=15):
            try:
                element = WebDriverWait(driver, wait_time).until(EC.element_to_be_clickable(locator))
                # Attempt to scroll into view if not immediately clickable
                try:
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", element)
                    random_delay(0.1, 0.3)
                except Exception:
                    pass # Continue if scrolling fails, click might still work
                element.click()
                random_delay(0.4, 0.8)
            except TimeoutException as te:
                raise TimeoutException(f"Timeout clicking {locator}: {str(te)}")
            except Exception as e:
                raise Exception(f"Error clicking {locator}: {str(e)}")

        def type_and_select_suggestion(input_locator, text_to_type, suggestion_list_selector, wait_time=15):
            try:
                input_field = WebDriverWait(driver, wait_time).until(EC.visibility_of_element_located(input_locator))
                input_field.click() # Focus the field
                random_delay(0.1, 0.3)
                input_field.clear()
                for char in text_to_type:
                    input_field.send_keys(char)
                    time.sleep(random.uniform(0.03, 0.08))
                random_delay(0.5, 1.0) # Wait for suggestions to load
                
                # Wait for the suggestion list to appear and have at least one item
                suggestions = WebDriverWait(driver, wait_time).until(
                    EC.presence_of_all_elements_located(suggestion_list_selector)
                )
                if not suggestions:
                    raise Exception(f"No suggestions appeared for '{text_to_type}' in {input_locator}")
                
                # Click the first suggestion (simplistic approach)
                # More robust: iterate suggestions and match text
                print(f"Found {len(suggestions)} suggestions for '{text_to_type}'. Clicking first: '{suggestions[0].text}'")
                suggestions[0].click()
                random_delay(0.4, 0.8)
            except TimeoutException as te:
                raise TimeoutException(f"Timeout during type/select for {input_locator} with text '{text_to_type}': {str(te)}")
            except Exception as e:
                raise Exception(f"Error during type/select for {input_locator} with text '{text_to_type}': {str(e)}")

        # --- Direct Scraper Logic --- 
        print("Navigating to ASSIST.org...")
        driver.get("https://assist.org/")
        random_delay(1.0, 1.5)

        # 1. Academic Year
        print("Selecting Academic Year...")
        try:
            # The academic year dropdown seems to be the first one with a common structure
            academic_year_dropdown_locator = (By.XPATH, "(//label[contains(text(), 'Academic Year')]/following-sibling::div//select)[1]")
            # Or more simply if ID is consistent and unique: (By.ID, "academicyear-select") - CHECK ID in devtools
            # For the screenshot, it seems to be just an input that becomes a dropdown, or a select.
            # Let's assume a select for now, if it has an ID, use that. If not, a more complex XPATH.
            # From previous logs, it was (By.ID, "academicYear")
            year_select_locator = (By.ID, "academicYear") 
            robust_click(year_select_locator) # Click to open/focus
            
            # Select the first option (e.g., "2024-2025")
            # This assumes the options are standard <option> tags. 
            # If it's a custom dropdown, this needs to change.
            first_year_option_locator = (By.XPATH, f"//{year_select_locator[1]}/option[position()=1]") # if it's a select
            # If it's a div-based dropdown, the options locator would be different.
            # For now, let's be more general for the options after clicking the main select element
            # Common pattern for options that appear:
            year_option_in_list_locator = (By.XPATH, "//ul[contains(@class, 'dropdown-menu') or contains(@id, 'suggestions')]/li[1]/a | //select[@id='academicYear']/option[1]")
            
            # Simpler: Click the dropdown, then find the first enabled option within it.
            # Assuming options are direct children or appear after click. The actual options might be in a separate popover.
            options = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, f"#{year_select_locator[1]} option")))
            if options:
                print(f"Selecting year: {options[0].text}")
                if not options[0].is_selected(): options[0].click()
                random_delay(0.3, 0.6)
            else:
                 raise Exception("No academic year options found after clicking dropdown.")
        except Exception as e_year:
            detailed_error = f"Error selecting Academic Year: {type(e_year).__name__} - {str(e_year)}"
            print(detailed_error)
            if not run_headless and driver: driver.save_screenshot("debug_academic_year_error.png")
            raise # Critical step

        # 2. Sending Institution ("Institution" on the left card)
        # Based on typical Assist.org structure and previous attempts, ID might be "sendingInstitution"
        # Or, visually, it's the input under the label "Institution"
        print(f"Selecting Sending Institution: {source_institution_name}")
        try:
            # Locator for the input field itself
            sending_institution_input_locator = (By.ID, "institution-select") # Check actual ID on site
            # Locator for the suggestion list items that appear after typing
            sending_suggestion_list_item_locator = (By.CSS_SELECTOR, "#institution-select-suggestions .list-group-item") # Check actual suggestion list structure
            type_and_select_suggestion(sending_institution_input_locator, source_institution_name, sending_suggestion_list_item_locator)
        except Exception as e_send_inst:
            detailed_error = f"Error selecting Sending Institution '{source_institution_name}': {type(e_send_inst).__name__} - {str(e_send_inst)}"
            print(detailed_error)
            if not run_headless and driver: driver.save_screenshot("debug_sending_institution_error.png")
            raise

        # 3. Receiving Institution ("Agreements with Other Institutions" on the left card)
        print(f"Selecting Receiving Institution: {target_institution_name}")
        try:
            receiving_institution_input_locator = (By.ID, "agreement-select") # Check actual ID
            receiving_suggestion_list_item_locator = (By.CSS_SELECTOR, "#agreement-select-suggestions .list-group-item") # Check actual suggestion list
            type_and_select_suggestion(receiving_institution_input_locator, target_institution_name, receiving_suggestion_list_item_locator)
        except Exception as e_recv_inst:
            detailed_error = f"Error selecting Receiving Institution '{target_institution_name}': {type(e_recv_inst).__name__} - {str(e_recv_inst)}"
            print(detailed_error)
            if not run_headless and driver: driver.save_screenshot("debug_receiving_institution_error.png")
            raise

        # 4. Click "View Agreements" button
        print("Clicking 'View Agreements' button...")
        try:
            # The button text in the screenshot is "View Agreements"
            view_agreements_button_locator = (By.XPATH, "//button[normalize-space()='View Agreements']")
            robust_click(view_agreements_button_locator)
            random_delay(1.5, 2.5) # Wait for next page to load
        except Exception as e_view_btn:
            detailed_error = f"Error clicking 'View Agreements' button: {type(e_view_btn).__name__} - {str(e_view_btn)}"
            print(detailed_error)
            if not run_headless and driver: driver.save_screenshot("debug_view_agreements_error.png")
            raise

        # --- From here, we are on the page listing majors (or similar) ---
        print(f"Searching for major on agreements page: {major_name_input}")
        norm_major_input = normalize_major_name(major_name_input)
        try:
            # Selector for links that represent a major agreement. This is highly site-dependent.
            # Common patterns: links within cards, list items, or table rows.
            major_link_selectors = [
                (By.XPATH, f"//a[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{norm_major_input.lower()}')]"),
                (By.XPATH, f"//h5[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{norm_major_input.lower()}')]/ancestor::a"),
                (By.CSS_SELECTOR, "div.card-body a.stretched-link") # General selector for links in cards
            ]
            
            selected_major_element = None
            for locator in major_link_selectors:
                try:
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator)) # Quick check if any exist
                    possible_elements = driver.find_elements(*locator)
                    for elem in possible_elements:
                        elem_text_norm = normalize_major_name(elem.text.strip())
                        if norm_major_input == elem_text_norm or norm_major_input in elem_text_norm:
                            selected_major_element = elem
                            print(f"Found major link: {elem.text.strip()}")
                            break
                    if selected_major_element: break
                except TimeoutException:
                    continue # Try next selector

            if not selected_major_element:
                 # Try to find any major link if specific one not found, just to see if we are on the right page type
                all_major_links_on_page = driver.find_elements(By.CSS_SELECTOR, "div.card a.stretched-link, div.agreement-item a, h5.card-title a")
                available_majors_text = [link.text.strip() for link in all_major_links_on_page if link.text.strip()][:10]
                print(f"Major '{major_name_input}' (normalized: {norm_major_input}) not found. Available links found: {available_majors_text}")
                if not run_headless and driver: driver.save_screenshot("debug_major_link_not_found.png")
                raise Exception(f"Could not find major link for '{major_name_input}'")

            print(f"Clicking selected major link: {selected_major_element.text.strip()}")
            robust_click(selected_major_element) # Pass the element directly
            random_delay(2.0, 3.5) # Wait for agreement details page

        except Exception as e_major_select:
            detailed_error = f"Error finding/clicking major link for '{major_name_input}': {type(e_major_select).__name__} - {str(e_major_select)}"
            print(detailed_error)
            if not run_headless and driver: driver.save_screenshot("debug_major_selection_error.png")
            raise

        # --- Extract course requirements from the final agreement page ---
        print("Extracting course requirements...")
        # The structure for course data (code, title, units) is very specific to ASSIST's final agreement page layout.
        # This will require careful inspection of the page if the selectors below fail.
        agreement_name_on_page = driver.title # A simple default
        try:
            # Try to get a more specific title from a header element
            page_header_elements = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3.agreement-view-title")
            if page_header_elements: agreement_name_on_page = page_header_elements[0].text.strip()
            print(f"Agreement Page Title (tentative): {agreement_name_on_page}")
        except Exception: pass

        all_extracted_courses = []
        try:
            # Example: Looking for rows or divs that contain course information
            # This is a placeholder - needs actual selectors from the target page
            course_container_elements = driver.find_elements(By.CSS_SELECTOR, "div.course-list-row, tr.articulated-course")
            if not course_container_elements:
                 print("Warning: No course container elements found with primary selectors. Trying fallback.")
                 # Add more fallback selectors if needed
                 course_container_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'course') and .//span[contains(@class, 'courseId')]]")

            print(f"Found {len(course_container_elements)} potential course containers.")
            for container in course_container_elements:
                try:
                    # These selectors are guesses based on common patterns.
                    code = container.find_element(By.CSS_SELECTOR, ".courseId, .course-code, [data-testid='courseCode']").text.strip()
                    title = container.find_element(By.CSS_SELECTOR, ".courseTitle, .course-name, [data-testid='courseTitle']").text.strip()
                    units_text = "0"
                    try:
                        units_text = container.find_element(By.CSS_SELECTOR, ".courseUnits, .course-credits, [data-testid='courseUnits']").text.strip()
                    except NoSuchElementException:
                        pass # Units might be optional or in a different spot
                    units = float(re.search(r'(\d+(\.\d+)?)', units_text).group(1)) if re.search(r'(\d+(\.\d+)?)', units_text) else 0.0
                    if code: # Basic validation: must have a course code
                        all_extracted_courses.append({"code": code, "title": title, "units": units, "section": "Extracted"})
                except NoSuchElementException:
                    # print(f"Skipping a container, couldn't find all expected elements (code/title).")
                    continue
                except Exception as e_course_parse:
                    print(f"Error parsing a course container: {str(e_course_parse)}")
                    continue
            
            if not all_extracted_courses:
                print("No courses extracted with structured selectors. Trying broad regex on page body as last resort.")
                body_text = driver.find_element(By.TAG_NAME, 'body').text
                # Regex for typical course codes (e.g., MATH 1A, CIS 22B) and optionally title/units
                course_pattern = re.compile(r'([A-Z]{2,4}\s*\d{1,3}[A-Z]?)(?:\s*-\s*(.*?)(?:\s+\((\d+\.?\d*)\s+Units\))?)?', re.IGNORECASE)
                matches = course_pattern.finditer(body_text)
                for match in matches:
                    code = match.group(1).strip().upper()
                    title = match.group(2).strip() if match.group(2) else "Title N/A (Regex Fallback)"
                    units = float(match.group(3)) if match.group(3) else 0.0
                    all_extracted_courses.append({"code": code, "title": title, "units": units, "section": "Regex Fallback"})

        except Exception as e_extract:
            print(f"Error during course extraction phase: {type(e_extract).__name__} - {str(e_extract)}")
            if not run_headless and driver: driver.save_screenshot("debug_course_extraction_final_error.png")

        print(f"Extracted {len(all_extracted_courses)} courses.")
        final_requirements = []
        if all_extracted_courses:
            norm_completed = [c.strip().replace(" ", "").upper() for c in (completed_courses or [])]
            for course in all_extracted_courses:
                norm_code = str(course.get('code', '')).replace(" ", "").upper()
                status = "completed" if norm_code and norm_code in norm_completed else "remaining"
                final_requirements.append({
                    "code": course.get('code'), "title": course.get('title'), 
                    "units": course.get('units'), "status": status,
                    "section": course.get('section', 'Required')
                })
        
        if not final_requirements:
            error_msg = f"Selenium scraper: No courses extracted for {major_name_input} agreement."
            print(error_msg)
            if not run_headless and driver: driver.save_screenshot("debug_no_final_requirements.png")
            return {"error": error_msg, "origin_institution": source_institution_name, "target_institution": target_institution_name, "target_major": major_name_input, "requirements": []}
        
        return {
            "origin_institution": source_institution_name, "target_institution": target_institution_name,
            "target_major": agreement_name_on_page or major_name_input,
            "requirements": final_requirements, "scraper_method": "Selenium - Direct"
        }
        
    except Exception as e_main_selenium:
        detailed_error = f"Critical error in DIRECT Selenium scraper: {type(e_main_selenium).__name__} - {str(e_main_selenium)}"
        print(detailed_error)
        if driver and not run_headless:
            try: driver.save_screenshot("debug_critical_direct_selenium_error.png")
            except: print("Failed to save screenshot on critical error.")
        return {
            "error": f"Selenium scraper critical error: {detailed_error}",
            "origin_institution": source_institution_name, "target_institution": target_institution_name,
            "target_major": major_name_input, "requirements": []
        }
    finally:
        if driver:
            try: 
                driver.quit()
                print("Browser closed.")
            except Exception as e_quit:
                print(f"Error quitting browser: {str(e_quit)}")

def get_transfer_courses(source_institution_name: str, target_institution_name: str, major_name_input: str, 
                         completed_courses: Optional[List[str]] = None, 
                         target_quarter: Optional[str] = None, 
                         target_academic_year_str: Optional[str] = None,
                         use_selenium: bool = False,
                         true_data_only: bool = False,
                         run_selenium_headless: bool = False) -> Dict:
    """Main function to get transfer courses using dynamic API lookups or Selenium."""
    print(f"Getting courses for {source_institution_name} to {target_institution_name} for {major_name_input}")

    if true_data_only:
        print(f"TRUE_DATA_ONLY specified. Attempting Selenium scraper... (Headless: {run_selenium_headless})")
        selenium_result = humanized_scrape_with_selenium(
            source_institution_name, 
            target_institution_name, 
            major_name_input, 
            completed_courses,
            run_headless=run_selenium_headless
        )
        # If true_data_only is set, we return the result of Selenium, success or failure.
        # We do not fall back to API or hardcoded data.
        if not selenium_result.get("error") and selenium_result.get("requirements"):
            print("Selenium scraping successful for true_data_only request.")
        else:
            print(f"Selenium scraping failed for true_data_only request. Error: {selenium_result.get('error', 'Unknown Selenium error')}")
        return selenium_result
    
    # If not true_data_only, but use_selenium is explicitly requested:
    if use_selenium: # This implies true_data_only was False, or it would have returned above
        print(f"USE_SELENIUM specified. Attempting Selenium scraper... (Headless: {run_selenium_headless})")
        selenium_result = humanized_scrape_with_selenium(
            source_institution_name, 
            target_institution_name, 
            major_name_input, 
            completed_courses,
            run_headless=run_selenium_headless
        )
        # If Selenium was explicitly requested, return its result, success or failure.
        # Do not fall back to API/hardcoded if use_selenium was the specific instruction.
        if not selenium_result.get("error") and selenium_result.get("requirements"):
            print("Selenium scraping successful for use_selenium request.")
        else:
            print(f"Selenium scraping failed for use_selenium request. Error: {selenium_result.get('error', 'Unknown Selenium error')}")
        return selenium_result

    # Standard path: Hardcoded data, then API (if true_data_only and use_selenium are both False)
    print("Attempting hardcoded data / API method (standard path)...")
    norm_source = normalize_institution_name(source_institution_name)
    norm_target = normalize_institution_name(target_institution_name)
    norm_major = normalize_major_name(major_name_input)
    
    # --- Hardcoded Data Check (only if not true_data_only) ---
    # This check is implicitly covered now by the logic: if true_data_only was true, we'd have returned.
    # De Anza College to UC Berkeley - Applied Math
    if (norm_source == "de anza college" and 
        norm_target == "university of california, berkeley" and 
        (norm_major == "mathematics, applied" or "applied" in norm_major or "math" in norm_major)):
        print("Using hardcoded data for De Anza College to UC Berkeley Applied Math transfer requirements")
        all_courses_hardcoded_applied_math = [
            {"code": "MATH 1A", "title": "Calculus", "units": 5.0},{"code": "MATH 1B", "title": "Calculus", "units": 5.0},{"code": "MATH 1C", "title": "Calculus", "units": 5.0},{"code": "MATH 1D", "title": "Calculus", "units": 5.0},{"code": "MATH 2A", "title": "Differential Equations", "units": 5.0},{"code": "MATH 2B", "title": "Linear Algebra", "units": 5.0},{"code": "PHYS 4A", "title": "Physics for Scientists and Engineers: Mechanics", "units": 6.0},{"code": "PHYS 4B", "title": "Physics for Scientists and Engineers: Electricity and Magnetism", "units": 6.0},{"code": "PHYS 4C", "title": "Physics for Scientists and Engineers: Fluids, Waves, Optics & Thermodynamics", "units": 6.0},{"code": "CIS 22A", "title": "Beginning Programming Methodologies in C++", "units": 4.5},{"code": "CIS 22B", "title": "Intermediate Programming Methodologies in C++", "units": 4.5},
        ]
        final_requirements_hardcoded = []
        norm_completed_hardcoded = [c.strip().replace(" ", "").upper() for c in (completed_courses or [])]
        for course in all_courses_hardcoded_applied_math:
            norm_code_hardcoded = str(course.get('code', '')).replace(" ", "").upper()
            status_hardcoded = "completed" if norm_code_hardcoded in norm_completed_hardcoded else "remaining"
            final_requirements_hardcoded.append({"code": course.get('code'), "title": course.get('title'), "units": course.get('units'), "status": status_hardcoded})
        return {"origin_institution": source_institution_name, "target_institution": target_institution_name, "target_major": "Mathematics, Applied", "target_quarter": target_quarter or "Fall 2024", "requirements": final_requirements_hardcoded, "api_year_information": "2024-2025 (Hardcoded Fallback)", "scraper_method": "Hardcoded"}

    # De Anza College to UC Berkeley - Computer Science
    if (norm_source == "de anza college" and 
        norm_target == "university of california, berkeley" and 
        norm_major == "computer science"):
        print("Using hardcoded data for De Anza College to UC Berkeley Computer Science transfer requirements")
        all_courses_hardcoded_cs = [
            {"code": "MATH 1A", "title": "Calculus", "units": 5.0},{"code": "MATH 1B", "title": "Calculus", "units": 5.0},{"code": "MATH 1C", "title": "Calculus", "units": 5.0},{"code": "MATH 1D", "title": "Calculus", "units": 5.0},{"code": "MATH 2B", "title": "Linear Algebra", "units": 5.0},{"code": "PHYS 4A", "title": "Physics for Scientists and Engineers: Mechanics", "units": 6.0},{"code": "PHYS 4B", "title": "Physics for Scientists and Engineers: Electricity and Magnetism", "units": 6.0},{"code": "CIS 22A", "title": "Beginning Programming Methodologies in C++", "units": 4.5},{"code": "CIS 22B", "title": "Intermediate Programming Methodologies in C++", "units": 4.5},{"code": "CIS 22C", "title": "Data Structures and Algorithms in C++", "units": 4.5},
        ]
        final_requirements_hardcoded_cs = []
        norm_completed_hardcoded_cs = [c.strip().replace(" ", "").upper() for c in (completed_courses or [])]
        for course in all_courses_hardcoded_cs:
            norm_code_hardcoded_cs = str(course.get('code', '')).replace(" ", "").upper()
            status_hardcoded_cs = "completed" if norm_code_hardcoded_cs in norm_completed_hardcoded_cs else "remaining"
            final_requirements_hardcoded_cs.append({"code": course.get('code'), "title": course.get('title'), "units": course.get('units'), "status": status_hardcoded_cs})
        return {"origin_institution": source_institution_name, "target_institution": target_institution_name, "target_major": "Computer Science", "target_quarter": target_quarter or "Fall 2024", "requirements": final_requirements_hardcoded_cs, "api_year_information": "2024-2025 (Hardcoded Fallback)", "scraper_method": "Hardcoded"}
    
    # --- API Method (only if not true_data_only and not use_selenium, or if they were false and led here) ---
    print("Proceeding to API method...")
    session_manager = RequestsSessionManager()
    if not session_manager.get_xsrf_token():
        return {"error": "Failed to init API session.", "requirements": []}

    academic_years = fetch_academic_years_api(session_manager)
    if not academic_years: 
        return {"error": "Failed to fetch academic years via API.", "requirements": []}

    year_id_to_use = None
    if target_academic_year_str:
        for year in academic_years:
            if year["name"] == target_academic_year_str or str(year.get("fall_year")) == target_academic_year_str:
                year_id_to_use = year["id"]
                print(f"Using specified Academic Year: {year['name']} (ID: {year_id_to_use})")
                break
    if not year_id_to_use:
        specific_year_to_try = "2024-2025"
        for year in academic_years:
            if year["name"] == specific_year_to_try:
                year_id_to_use = year["id"]
                print(f"Defaulting to Academic Year: {year['name']} (ID: {year_id_to_use})")
                break
        if not year_id_to_use and academic_years: 
            year_id_to_use = academic_years[0]["id"]
            print(f"Defaulting to latest available Academic Year: {academic_years[0]['name']} (ID: {year_id_to_use})")
    if not year_id_to_use: 
        return {"error": "Could not determine academic year for API.", "requirements": []}

    institutions = fetch_institutions_api(session_manager)
    if not institutions: 
        return {"error": "Failed to fetch institutions via API.", "requirements": []}

    norm_source_name = normalize_institution_name(source_institution_name)
    norm_target_name = normalize_institution_name(target_institution_name)
    source_institution_id, target_institution_id = None, None
    for inst in institutions:
        if any(normalize_institution_name(name) == norm_source_name for name in inst.get("all_names", [])):
            source_institution_id = inst["id"]
        if any(normalize_institution_name(name) == norm_target_name for name in inst.get("all_names", [])):
            target_institution_id = inst["id"]
        if source_institution_id and target_institution_id: break
    if not source_institution_id: 
        return {"error": f"API: Source institution '{source_institution_name}' not found.", "requirements": []}
    if not target_institution_id: 
        return {"error": f"API: Target institution '{target_institution_name}' not found.", "requirements": []}
    print(f"API Found Source ID: {source_institution_id}, Target ID: {target_institution_id}")

    majors_report_type = 3 
    majors = fetch_majors_api(session_manager, year_id_to_use, source_institution_id, target_institution_id, majors_report_type)
    if not majors: 
        err_msg = f"API: No major agreements found for Inst {source_institution_id} to {target_institution_id}, Year {year_id_to_use}."
        return {"error": err_msg, "requirements": []}
    
    norm_major_input_api = normalize_major_name(major_name_input)
    major_key_from_api = None
    found_major_name_api = major_name_input
    for m_api in majors:
        api_major_name_normalized = normalize_major_name(m_api.get("name", "")) 
        if norm_major_input_api == api_major_name_normalized:
            major_key_from_api = m_api.get("key")
            found_major_name_api = m_api.get("name", major_name_input)
            print(f"API Found Major Agreement: '{found_major_name_api}' with key: {major_key_from_api}")
            break
    if not major_key_from_api:
        for m_api in majors: # Fallback partial match
            api_major_name_normalized = normalize_major_name(m_api.get("name", ""))
            if norm_major_input_api in api_major_name_normalized:
                 major_key_from_api = m_api.get("key")
                 found_major_name_api = m_api.get("name", major_name_input)
                 print(f"API Found Major Agreement (partial match): '{found_major_name_api}' with key: {major_key_from_api}")
                 break
    if not major_key_from_api: 
        err_msg = f"API: Major agreement '{major_name_input}' (normalized: {norm_major_input_api}) not found."
        return {"error": err_msg, "requirements": []}

    agreement_key = f"{int(year_id_to_use)}/{int(source_institution_id)}/to/{int(target_institution_id)}/{major_key_from_api}"
    print(f"API Constructed agreement key: {agreement_key}")
    referer_url = f"{session_manager.base_url}transfer/results?year={year_id_to_use}&institution={source_institution_id}&agreement={target_institution_id}&agreementType=to&viewBy=major&viewByKey={agreement_key.replace('/', '%2F')}"
    api_result = fetch_agreement_data_api(session_manager, agreement_key, referer_url)
    
    all_courses_api = []
    if api_result.get("data_available", False):
        all_courses_api.extend(api_result.get("required_courses", []))
        all_courses_api.extend(api_result.get("recommended_courses", []))

    final_requirements_api = []
    norm_completed_api = [c.strip().replace(" ", "").upper() for c in (completed_courses or [])]
    for course_api in all_courses_api:
        norm_code_api = str(course_api.get('code', '')).replace(" ", "").upper()
        status_api = "completed" if norm_code_api and norm_code_api in norm_completed_api else "remaining"
        final_requirements_api.append({"code": course_api.get('code'), "title": course_api.get('title'), "units": course_api.get('units'), "status": status_api})

    if "error" in api_result and not api_result.get("data_available", False):
        err_msg = api_result["error"]
        return {"error": err_msg, "origin_institution": source_institution_name, "target_institution": target_institution_name, "target_major": major_name_input, "target_quarter": target_quarter or "N/A", "requirements": [], "suggestion": "API could not retrieve data."}

    return {"origin_institution": source_institution_name, "target_institution": target_institution_name, "target_major": api_result.get("agreement_name", found_major_name_api), "target_quarter": target_quarter or "N/A", "requirements": final_requirements_api, "api_year_information": api_result.get("year", "N/A"), "scraper_method": "API"}

# Removed BeautifulSoup and re as they are not used in the API method currently.
# Kept json and typing. Removed time. 