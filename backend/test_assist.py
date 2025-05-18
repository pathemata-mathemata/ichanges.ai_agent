from app.modules.assist_scraper import (
    normalize_institution_name,
    normalize_major_name,
    get_transfer_courses
)

def test_normalization():
    """Test normalization of institution and major names"""
    print("Testing normalization functions...")
    test_institutions = ["UC Berkeley", "Berkeley", "UCLA", "De Anza", "SJSU"]
    print("Institution name normalization:")
    for name in test_institutions:
        print(f"  {name} -> {normalize_institution_name(name)}")
    test_majors = ["CS", "Compsci", "Psych", "Bio", "Econ", "Applied Math"]
    print("\nMajor name normalization:")
    for name in test_majors:
        print(f"  {name} -> {normalize_major_name(name)}")
    print()

def test_transfer_courses():
    """Test getting transfer courses with completed courses (hardcoded/API fallback)"""
    print("Testing get_transfer_courses() with completed courses (hardcoded/API fallback)...")
    source_institution = "De Anza College"
    target_institution = "UC Berkeley"
    major = "Applied Math"
    completed = ['MATH 1A', 'MATH 1B']
    print(f"Getting transfer requirements for {source_institution} to {target_institution} for {major}...")
    print(f"Completed courses: {completed}")
    result = get_transfer_courses(
        source_institution_name=source_institution, 
        target_institution_name=target_institution, 
        major_name_input=major,
        completed_courses=completed,
        target_academic_year_str="2024-2025",
        run_selenium_headless=True # Default tests can run headless
    )
    if "error" in result:
        print(f"Error: {result.get('error')}")
    else:
        print(f"Origin Institution: {result.get('origin_institution')}")
        print(f"Target Institution: {result.get('target_institution')}")
        print(f"Target Major: {result.get('target_major')}")
        print(f"Target Quarter: {result.get('target_quarter')}")
        requirements = result.get('requirements', [])
        completed_list = [r for r in requirements if r.get('status') == 'completed']
        remaining_list = [r for r in requirements if r.get('status') == 'remaining']
        print(f"Completed courses: {len(completed_list)}/{len(requirements)}")
        for i, course in enumerate(completed_list):
            print(f"{i+1}. {course.get('code')}: {course.get('title')} ({course.get('units')} units) - {course.get('status')}")
        print(f"\nRemaining courses: {len(remaining_list)}/{len(requirements)}")
        for i, course in enumerate(remaining_list):
            print(f"{i+1}. {course.get('code')}: {course.get('title')} ({course.get('units')} units) - {course.get('status')}")
    print()

def test_json_format():
    """Test JSON format output for the prompt (hardcoded/API fallback)"""
    print("\nTesting JSON format output (hardcoded/API fallback)...")
    source_institution = "De Anza College"
    target_institution = "UC Berkeley"
    major = "Applied Math"
    completed_for_json = ['MATH 1A', 'MATH 1B']
    result = get_transfer_courses(
        source_institution_name=source_institution, 
        target_institution_name=target_institution, 
        major_name_input=major,
        completed_courses=completed_for_json,
        target_academic_year_str="2024-2025",
        run_selenium_headless=True # Default tests can run headless
    )
    import json
    json_str = json.dumps(result, indent=2)
    print("JSON Output:")
    print(json_str)
    print()

def test_selenium_scraper_visible():
    """Test the humanized Selenium scraper with visible browser"""
    print("\nTesting humanized Selenium scraper (VISIBLE BROWSER)... NOTE: This will open a Chrome window.")
    source_institution = "De Anza College"
    target_institution = "UC Berkeley"
    major = "Computer Science"
    completed = ['MATH 1A', 'CIS 22A']
    result = get_transfer_courses(
        source_institution_name=source_institution, 
        target_institution_name=target_institution, 
        major_name_input=major,
        completed_courses=completed,
        use_selenium=True, # Explicitly request Selenium scraper
        run_selenium_headless=False # Make browser visible
    )
    print_results(result)

def test_true_data_scraper_visible():
    """Test the true data only option with visible browser"""
    print("\nTesting true_data_only option (VISIBLE BROWSER)... NOTE: This will open a Chrome window.")
    source_institution = "Foothill College" # Different institutions for variety
    target_institution = "University of California, Davis" # Different institutions for variety
    major = "Psychology"
    completed = [] # No completed courses for this test
    result = get_transfer_courses(
        source_institution_name=source_institution, 
        target_institution_name=target_institution, 
        major_name_input=major,
        completed_courses=completed,
        true_data_only=True,
        run_selenium_headless=False
    )
    print_results(result)

def print_results(result: dict):
    """Helper to print scraper results consistently."""
    if "error" in result and result.get("error"):
        print(f"Error: {result.get('error')}")
    else:
        print(f"Origin Institution: {result.get('origin_institution')}")
        print(f"Target Institution: {result.get('target_institution')}")
        print(f"Target Major: {result.get('target_major', 'N/A')}")
        scraper_method = result.get('scraper_method', 'Unknown')
        print(f"Scraper Method: {scraper_method}")
        
        requirements = result.get('requirements', [])
        if not requirements:
            print("No requirements found or extracted.")
        else:
            completed_list = [r for r in requirements if r.get('status') == 'completed']
            remaining_list = [r for r in requirements if r.get('status') == 'remaining']
            print(f"Completed courses: {len(completed_list)}/{len(requirements)}")
            for i, course in enumerate(completed_list):
                section = course.get('section', 'N/A')
                print(f"{i+1}. {course.get('code')}: {course.get('title')} ({course.get('units')} units) - Status: {course.get('status')} - Section: {section}")
            print(f"\nRemaining courses: {len(remaining_list)}/{len(requirements)}")
            # Show only a few remaining to keep output short for testing
            for i, course in enumerate(remaining_list[:5]): 
                section = course.get('section', 'N/A')
                print(f"{i+1}. {course.get('code')}: {course.get('title')} ({course.get('units')} units) - Status: {course.get('status')} - Section: {section}")
            if len(remaining_list) > 5:
                print(f"... and {len(remaining_list) - 5} more remaining courses.")
    import json
    # Truncate JSON for brevity in test output
    json_output = json.dumps(result, indent=2)
    max_len = 1000
    if len(json_output) > max_len:
        json_output = json_output[:max_len] + "... (JSON truncated)"
    print(f"\nJSON Output (abbreviated):\n{json_output}")
    print("-" * 30)

if __name__ == "__main__":
    test_normalization()
    test_transfer_courses() 
    test_json_format()
    
    print("\n" + "="*50) 
    print("PREPARING TO RUN SELENIUM VISIBLE TESTS")
    print("A Chrome browser window should open. Please observe its behavior.")
    print("Make sure you have a stable internet connection.")
    print("If chromedriver needs to be downloaded, it will happen automatically.")
    print("="*50 + "\n")
    input("Press Enter to start the VISIBLE Selenium tests or Ctrl+C to skip...")
    
    test_selenium_scraper_visible()
    test_true_data_scraper_visible() 