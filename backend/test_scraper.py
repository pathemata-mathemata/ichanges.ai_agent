from app.modules.catalog_scraper import google_search_raw, find_institution_domain, search_catalog_urls, find_course_info

# Test the raw Google search function
print("Testing google_search_raw:")
results = google_search_raw("Stanford University Computer Science", num=3)
print(results)
print()

# Test finding institution domain
print("Testing find_institution_domain:")
domain = find_institution_domain("Stanford University")
print(f"Domain found: {domain}")
print()

# Test finding course info (if you have specific course details)
print("Testing find_course_info:")
course_info = find_course_info("CS 101", "Fall", "Stanford University")
print(course_info) 