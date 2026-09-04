#!/usr/bin/env python3
"""Backend API tests for HR Digital Services app - Reviews, Views, Search, Custom Head"""
import requests
import json
import time
from urllib.parse import quote

# Base URL from frontend env
BASE_URL = "https://copy-manager-5.preview.emergentagent.com/api"

# Admin credentials
ADMIN_EMAIL = "admin@hrdigitalservices.in"
ADMIN_PASSWORD = "Admin@12345"

# Test results
results = {
    "passed": [],
    "failed": [],
}

def log_pass(test_name, details=""):
    print(f"✅ PASS: {test_name}")
    if details:
        print(f"   {details}")
    results["passed"].append(test_name)

def log_fail(test_name, details=""):
    print(f"❌ FAIL: {test_name}")
    if details:
        print(f"   {details}")
    results["failed"].append(test_name)

def admin_login():
    """Login as admin and return session"""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if resp.status_code == 200:
        print(f"✓ Admin login successful")
        return session
    else:
        print(f"✗ Admin login failed: {resp.status_code} - {resp.text}")
        return None

def test_vacancy_search():
    """Test 1: Vacancy search with synonyms (gds, india post, gramin dak)"""
    print("\n" + "="*80)
    print("TEST 1: VACANCY SEARCH WITH SYNONYMS")
    print("="*80)
    
    # Test search queries
    queries = [
        ("gds", "GDS search (synonym)"),
        ("india post", "India Post search"),
        ("gramin dak", "Gramin Dak search"),
    ]
    
    target_title_keywords = ["india post", "gramin dak sevak"]
    
    for query, desc in queries:
        encoded_query = quote(query)
        resp = requests.get(f"{BASE_URL}/vacancies?q={encoded_query}")
        
        if resp.status_code != 200:
            log_fail(f"Vacancy search: {desc}", f"Status {resp.status_code}")
            continue
        
        data = resp.json()
        
        # Check response structure
        if not all(k in data for k in ["items", "total", "page", "pages"]):
            log_fail(f"Vacancy search: {desc}", "Missing pagination fields")
            continue
        
        # Check if we got results
        if data["total"] == 0:
            log_fail(f"Vacancy search: {desc}", f"No results found for '{query}'")
            continue
        
        # Check if any item contains the target keywords
        found = False
        for item in data["items"]:
            title = (item.get("title") or "").lower()
            post_name = (item.get("post_name") or "").lower()
            combined = f"{title} {post_name}"
            
            # Check if it contains "gramin dak sevak" or "india post"
            if any(keyword in combined for keyword in target_title_keywords):
                found = True
                log_pass(f"Vacancy search: {desc}", 
                        f"Found matching vacancy: {item.get('title', 'N/A')[:80]}")
                break
        
        if not found:
            log_fail(f"Vacancy search: {desc}", 
                    f"No vacancy with 'India Post — Gramin Dak Sevak' found in {data['total']} results")

def test_view_counter():
    """Test 2: View counter increments on blogs and vacancies"""
    print("\n" + "="*80)
    print("TEST 2: VIEW COUNTER INCREMENT")
    print("="*80)
    
    # Test blog views
    print("\n--- Testing Blog Views ---")
    resp = requests.get(f"{BASE_URL}/blogs")
    if resp.status_code != 200:
        log_fail("Blog view counter", f"Failed to fetch blogs: {resp.status_code}")
    else:
        blogs = resp.json()
        if not blogs:
            log_fail("Blog view counter", "No blogs found to test")
        else:
            # Pick first blog
            blog = blogs[0]
            slug = blog.get("slug")
            
            if not slug:
                log_fail("Blog view counter", "Blog has no slug")
            else:
                # Get blog twice and check views increment
                resp1 = requests.get(f"{BASE_URL}/blogs/{slug}")
                if resp1.status_code != 200:
                    log_fail("Blog view counter", f"Failed to fetch blog: {resp1.status_code}")
                else:
                    data1 = resp1.json()
                    views1 = data1.get("views", 0)
                    
                    time.sleep(0.5)
                    
                    resp2 = requests.get(f"{BASE_URL}/blogs/{slug}")
                    if resp2.status_code != 200:
                        log_fail("Blog view counter", f"Failed to fetch blog second time: {resp2.status_code}")
                    else:
                        data2 = resp2.json()
                        views2 = data2.get("views", 0)
                        
                        if views2 == views1 + 1:
                            log_pass("Blog view counter", f"Views incremented: {views1} → {views2}")
                        else:
                            log_fail("Blog view counter", f"Views did not increment correctly: {views1} → {views2}")
    
    # Test vacancy views
    print("\n--- Testing Vacancy Views ---")
    resp = requests.get(f"{BASE_URL}/vacancies?per_page=5")
    if resp.status_code != 200:
        log_fail("Vacancy view counter", f"Failed to fetch vacancies: {resp.status_code}")
    else:
        data = resp.json()
        items = data.get("items", [])
        if not items:
            log_fail("Vacancy view counter", "No vacancies found to test")
        else:
            # Pick first vacancy
            vacancy = items[0]
            vac_id = vacancy.get("id")
            
            if not vac_id:
                log_fail("Vacancy view counter", "Vacancy has no id")
            else:
                # Get vacancy twice and check views increment
                resp1 = requests.get(f"{BASE_URL}/vacancies/{vac_id}")
                if resp1.status_code != 200:
                    log_fail("Vacancy view counter", f"Failed to fetch vacancy: {resp1.status_code}")
                else:
                    data1 = resp1.json()
                    views1 = data1.get("views", 0)
                    
                    time.sleep(0.5)
                    
                    resp2 = requests.get(f"{BASE_URL}/vacancies/{vac_id}")
                    if resp2.status_code != 200:
                        log_fail("Vacancy view counter", f"Failed to fetch vacancy second time: {resp2.status_code}")
                    else:
                        data2 = resp2.json()
                        views2 = data2.get("views", 0)
                        
                        if views2 == views1 + 1:
                            log_pass("Vacancy view counter", f"Views incremented: {views1} → {views2}")
                        else:
                            log_fail("Vacancy view counter", f"Views did not increment correctly: {views1} → {views2}")

def test_reviews():
    """Test 3: Reviews CRUD - public post/list, admin moderation"""
    print("\n" + "="*80)
    print("TEST 3: REVIEWS CRUD")
    print("="*80)
    
    # Get a blog and vacancy to test with
    blog_slug = None
    vacancy_id = None
    
    resp = requests.get(f"{BASE_URL}/blogs")
    if resp.status_code == 200:
        blogs = resp.json()
        if blogs:
            blog_slug = blogs[0].get("slug")
    
    resp = requests.get(f"{BASE_URL}/vacancies?per_page=5")
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("items", [])
        if items:
            vacancy_id = items[0].get("id")
    
    if not blog_slug:
        log_fail("Reviews - blog target", "No blog found to test reviews")
        return
    
    if not vacancy_id:
        log_fail("Reviews - vacancy target", "No vacancy found to test reviews")
        return
    
    # Test 3.1: POST review for blog
    print("\n--- Testing POST /api/reviews (blog) ---")
    review_blog_payload = {
        "target_type": "blog",
        "target_id": blog_slug,
        "name": "Test User",
        "rating": 5,
        "comment": "Great article!"
    }
    resp = requests.post(f"{BASE_URL}/reviews", json=review_blog_payload)
    if resp.status_code == 200:
        blog_review = resp.json()
        blog_review_id = blog_review.get("id")
        log_pass("POST review (blog)", f"Created review ID: {blog_review_id}")
    else:
        log_fail("POST review (blog)", f"Status {resp.status_code}: {resp.text}")
        blog_review_id = None
    
    # Test 3.2: POST review for vacancy
    print("\n--- Testing POST /api/reviews (vacancy) ---")
    review_vacancy_payload = {
        "target_type": "vacancy",
        "target_id": vacancy_id,
        "name": "T2",
        "rating": 4,
        "comment": "ok"
    }
    resp = requests.post(f"{BASE_URL}/reviews", json=review_vacancy_payload)
    if resp.status_code == 200:
        vacancy_review = resp.json()
        vacancy_review_id = vacancy_review.get("id")
        log_pass("POST review (vacancy)", f"Created review ID: {vacancy_review_id}")
    else:
        log_fail("POST review (vacancy)", f"Status {resp.status_code}: {resp.text}")
        vacancy_review_id = None
    
    # Test 3.3: GET reviews for blog
    print("\n--- Testing GET /api/reviews (blog) ---")
    resp = requests.get(f"{BASE_URL}/reviews?target_type=blog&target_id={blog_slug}")
    if resp.status_code == 200:
        data = resp.json()
        if all(k in data for k in ["items", "count", "average"]):
            if data["count"] >= 1:
                log_pass("GET reviews (blog)", f"Count: {data['count']}, Average: {data['average']}")
            else:
                log_fail("GET reviews (blog)", "Count is 0, expected at least 1")
        else:
            log_fail("GET reviews (blog)", "Missing required fields (items, count, average)")
    else:
        log_fail("GET reviews (blog)", f"Status {resp.status_code}: {resp.text}")
    
    # Test 3.4: Invalid target_type
    print("\n--- Testing POST /api/reviews (invalid target_type) ---")
    invalid_payload = {
        "target_type": "foo",
        "target_id": "test",
        "name": "Test",
        "rating": 3,
        "comment": "test"
    }
    resp = requests.post(f"{BASE_URL}/reviews", json=invalid_payload)
    if resp.status_code == 400:
        log_pass("POST review (invalid target_type)", "Correctly rejected with 400")
    else:
        log_fail("POST review (invalid target_type)", f"Expected 400, got {resp.status_code}")
    
    # Test 3.5: Admin endpoints
    print("\n--- Testing Admin Review Endpoints ---")
    admin_session = admin_login()
    if not admin_session:
        log_fail("Admin reviews", "Admin login failed")
        return
    
    # GET /api/admin/reviews
    resp = admin_session.get(f"{BASE_URL}/admin/reviews")
    if resp.status_code == 200:
        admin_reviews = resp.json()
        if isinstance(admin_reviews, list) and len(admin_reviews) > 0:
            # Check if target_title is present
            if "target_title" in admin_reviews[0]:
                log_pass("GET /api/admin/reviews", f"Found {len(admin_reviews)} reviews with target_title")
            else:
                log_fail("GET /api/admin/reviews", "target_title field missing")
        else:
            log_pass("GET /api/admin/reviews", "Returns list (empty or populated)")
    else:
        log_fail("GET /api/admin/reviews", f"Status {resp.status_code}: {resp.text}")
    
    # Test auth required
    resp_no_auth = requests.get(f"{BASE_URL}/admin/reviews")
    if resp_no_auth.status_code in [401, 403]:
        log_pass("Admin reviews auth", "Correctly requires authentication")
    else:
        log_fail("Admin reviews auth", f"Expected 401/403, got {resp_no_auth.status_code}")
    
    # Toggle review (hide/unhide)
    if blog_review_id:
        print("\n--- Testing PUT /api/admin/reviews/{id}/toggle ---")
        resp = admin_session.put(f"{BASE_URL}/admin/reviews/{blog_review_id}/toggle")
        if resp.status_code == 200:
            data = resp.json()
            hidden = data.get("hidden")
            log_pass("Toggle review (hide)", f"Hidden: {hidden}")
            
            # Check if hidden review is excluded from public GET
            resp_public = requests.get(f"{BASE_URL}/reviews?target_type=blog&target_id={blog_slug}")
            if resp_public.status_code == 200:
                public_data = resp_public.json()
                public_ids = [r.get("id") for r in public_data.get("items", [])]
                if blog_review_id not in public_ids:
                    log_pass("Hidden review exclusion", "Hidden review not in public list")
                else:
                    log_fail("Hidden review exclusion", "Hidden review still appears in public list")
            
            # Toggle back (unhide)
            resp = admin_session.put(f"{BASE_URL}/admin/reviews/{blog_review_id}/toggle")
            if resp.status_code == 200:
                data = resp.json()
                hidden = data.get("hidden")
                log_pass("Toggle review (unhide)", f"Hidden: {hidden}")
        else:
            log_fail("Toggle review", f"Status {resp.status_code}: {resp.text}")
    
    # Delete review
    if vacancy_review_id:
        print("\n--- Testing DELETE /api/admin/reviews/{id} ---")
        resp = admin_session.delete(f"{BASE_URL}/admin/reviews/{vacancy_review_id}")
        if resp.status_code == 200:
            log_pass("DELETE review", "Review deleted successfully")
            
            # Verify it's gone from admin list
            resp = admin_session.get(f"{BASE_URL}/admin/reviews")
            if resp.status_code == 200:
                admin_reviews = resp.json()
                review_ids = [r.get("id") for r in admin_reviews]
                if vacancy_review_id not in review_ids:
                    log_pass("DELETE review verification", "Review no longer in admin list")
                else:
                    log_fail("DELETE review verification", "Review still in admin list")
        else:
            log_fail("DELETE review", f"Status {resp.status_code}: {resp.text}")

def test_custom_head():
    """Test 4: Custom head / verification meta tags"""
    print("\n" + "="*80)
    print("TEST 4: CUSTOM HEAD / VERIFICATION META")
    print("="*80)
    
    admin_session = admin_login()
    if not admin_session:
        log_fail("Custom head", "Admin login failed")
        return
    
    # Test 4.1: Blog custom_head
    print("\n--- Testing Blog custom_head ---")
    
    # Get existing blogs
    resp = admin_session.get(f"{BASE_URL}/admin/blogs")
    if resp.status_code != 200:
        log_fail("Blog custom_head", f"Failed to fetch blogs: {resp.status_code}")
        return
    
    blogs = resp.json()
    if not blogs:
        log_fail("Blog custom_head", "No blogs found to test")
        return
    
    blog = blogs[0]
    blog_id = blog.get("id")
    blog_slug = blog.get("slug")
    
    # Update blog with custom_head
    custom_head_value = '<meta name="google-site-verification" content="abc123" />'
    
    # Prepare form data
    form_data = {
        "title": blog.get("title", "Test Blog"),
        "excerpt": blog.get("excerpt", ""),
        "content": blog.get("content", ""),
        "status": blog.get("status", "published"),
        "slug": blog_slug,
        "categories": ",".join(blog.get("categories", [])),
        "tags": ",".join(blog.get("tags", [])),
        "focus_keyword": blog.get("focus_keyword", ""),
        "seo_title": blog.get("seo_title", ""),
        "seo_description": blog.get("seo_description", ""),
        "custom_head": custom_head_value,
    }
    
    resp = admin_session.put(f"{BASE_URL}/admin/blogs/{blog_id}", data=form_data)
    if resp.status_code == 200:
        updated_blog = resp.json()
        updated_slug = updated_blog.get("slug")
        log_pass("Blog custom_head update", "Updated successfully")
        
        # Verify it's returned in GET (use updated slug from response)
        resp = requests.get(f"{BASE_URL}/blogs/{updated_slug}")
        if resp.status_code == 200:
            data = resp.json()
            returned_custom_head = data.get("custom_head", "")
            if custom_head_value in returned_custom_head or returned_custom_head == custom_head_value:
                log_pass("Blog custom_head GET", "custom_head returned correctly")
            else:
                log_fail("Blog custom_head GET", f"Expected '{custom_head_value}', got '{returned_custom_head}'")
        else:
            log_fail("Blog custom_head GET", f"Failed to fetch blog: {resp.status_code}")
    else:
        log_fail("Blog custom_head update", f"Status {resp.status_code}: {resp.text}")
    
    # Test 4.2: Vacancy custom_head
    print("\n--- Testing Vacancy custom_head ---")
    
    # Get a vacancy
    resp = requests.get(f"{BASE_URL}/vacancies?per_page=5")
    if resp.status_code != 200:
        log_fail("Vacancy custom_head", f"Failed to fetch vacancies: {resp.status_code}")
        return
    
    data = resp.json()
    items = data.get("items", [])
    if not items:
        log_fail("Vacancy custom_head", "No vacancies found to test")
        return
    
    vacancy = items[0]
    vacancy_id = vacancy.get("id")
    
    # Update vacancy SEO with custom_head
    custom_head_vacancy = '<meta name="x" content="y" />'
    seo_payload = {
        "custom_head": custom_head_vacancy
    }
    
    resp = admin_session.put(f"{BASE_URL}/admin/vacancies/{vacancy_id}/seo", json=seo_payload)
    if resp.status_code == 200:
        log_pass("Vacancy custom_head update", "Updated successfully")
        
        # Verify it's returned in GET
        resp = requests.get(f"{BASE_URL}/vacancies/{vacancy_id}")
        if resp.status_code == 200:
            data = resp.json()
            returned_custom_head = data.get("custom_head", "")
            if custom_head_vacancy in returned_custom_head or returned_custom_head == custom_head_vacancy:
                log_pass("Vacancy custom_head GET", "custom_head returned correctly")
            else:
                log_fail("Vacancy custom_head GET", f"Expected '{custom_head_vacancy}', got '{returned_custom_head}'")
        else:
            log_fail("Vacancy custom_head GET", f"Failed to fetch vacancy: {resp.status_code}")
    else:
        log_fail("Vacancy custom_head update", f"Status {resp.status_code}: {resp.text}")

def test_admin_overview():
    """Test 5: Admin overview endpoint"""
    print("\n" + "="*80)
    print("TEST 5: ADMIN OVERVIEW")
    print("="*80)
    
    # Test 5.1: Without auth - should get 401/403
    print("\n--- Testing GET /api/admin/overview (no auth) ---")
    resp = requests.get(f"{BASE_URL}/admin/overview")
    if resp.status_code in [401, 403]:
        log_pass("Admin overview (no auth)", f"Correctly rejected with {resp.status_code}")
    else:
        log_fail("Admin overview (no auth)", f"Expected 401/403, got {resp.status_code}")
    
    # Test 5.2: With admin auth - should return all required keys
    print("\n--- Testing GET /api/admin/overview (with auth) ---")
    admin_session = admin_login()
    if not admin_session:
        log_fail("Admin overview (with auth)", "Admin login failed")
        return
    
    resp = admin_session.get(f"{BASE_URL}/admin/overview")
    if resp.status_code == 200:
        data = resp.json()
        required_keys = [
            "total_vacancies", "total_views", "total_blogs", "total_reviews",
            "manual_vacancies", "vacancy_views", "blog_views", "contacts"
        ]
        
        missing_keys = [k for k in required_keys if k not in data]
        if missing_keys:
            log_fail("Admin overview (with auth)", f"Missing keys: {missing_keys}")
        else:
            # Verify all values are numbers
            non_numeric = [k for k in required_keys if not isinstance(data[k], (int, float))]
            if non_numeric:
                log_fail("Admin overview (with auth)", f"Non-numeric values for: {non_numeric}")
            else:
                log_pass("Admin overview (with auth)", 
                        f"All keys present: total_vacancies={data['total_vacancies']}, "
                        f"manual_vacancies={data['manual_vacancies']}, "
                        f"total_blogs={data['total_blogs']}, "
                        f"total_reviews={data['total_reviews']}, "
                        f"total_views={data['total_views']}")
    else:
        log_fail("Admin overview (with auth)", f"Status {resp.status_code}: {resp.text}")

def test_admin_uploads():
    """Test 6: Admin file upload endpoint"""
    print("\n" + "="*80)
    print("TEST 6: ADMIN UPLOADS")
    print("="*80)
    
    # Test 6.1: Without auth - should get 401/403
    print("\n--- Testing POST /api/admin/uploads (no auth) ---")
    
    # Create a tiny PDF
    pdf_content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Resources<<>>>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n190\n%%EOF"
    
    files = {"file": ("test.pdf", pdf_content, "application/pdf")}
    resp = requests.post(f"{BASE_URL}/admin/uploads", files=files)
    if resp.status_code in [401, 403]:
        log_pass("Admin upload (no auth)", f"Correctly rejected with {resp.status_code}")
    else:
        log_fail("Admin upload (no auth)", f"Expected 401/403, got {resp.status_code}")
    
    # Test 6.2: With admin auth - should upload successfully
    print("\n--- Testing POST /api/admin/uploads (with auth) ---")
    admin_session = admin_login()
    if not admin_session:
        log_fail("Admin upload (with auth)", "Admin login failed")
        return
    
    files = {"file": ("test_upload.pdf", pdf_content, "application/pdf")}
    resp = admin_session.post(f"{BASE_URL}/admin/uploads", files=files)
    
    if resp.status_code == 200:
        data = resp.json()
        required_keys = ["url", "name", "size", "mime"]
        missing_keys = [k for k in required_keys if k not in data]
        
        if missing_keys:
            log_fail("Admin upload (with auth)", f"Missing keys: {missing_keys}")
            return
        
        if data["mime"] != "application/pdf":
            log_fail("Admin upload (with auth)", f"Expected mime=application/pdf, got {data['mime']}")
            return
        
        log_pass("Admin upload (with auth)", 
                f"Upload successful: url={data['url']}, name={data['name']}, "
                f"size={data['size']}, mime={data['mime']}")
        
        # Test 6.3: GET the uploaded file
        print("\n--- Testing GET uploaded file ---")
        upload_url = data["url"]
        
        # The URL should be like /api/uploads/{fname}, need to prepend base
        if upload_url.startswith("/api/"):
            full_url = f"{BASE_URL.rsplit('/api', 1)[0]}{upload_url}"
        else:
            full_url = f"{BASE_URL}/{upload_url}"
        
        resp = requests.get(full_url)
        if resp.status_code == 200:
            content_type = resp.headers.get("content-type", "")
            if "application/pdf" in content_type.lower():
                log_pass("GET uploaded file", f"File retrieved with correct Content-Type: {content_type}")
            else:
                log_fail("GET uploaded file", f"Expected PDF content-type, got: {content_type}")
        else:
            log_fail("GET uploaded file", f"Status {resp.status_code}")
    else:
        log_fail("Admin upload (with auth)", f"Status {resp.status_code}: {resp.text}")

def test_manual_vacancy_tags_links():
    """Test 7: Manual vacancy tags and important_links"""
    print("\n" + "="*80)
    print("TEST 7: MANUAL VACANCY TAGS & IMPORTANT_LINKS")
    print("="*80)
    
    admin_session = admin_login()
    if not admin_session:
        log_fail("Manual vacancy tags/links", "Admin login failed")
        return
    
    # Test 7.1: POST manual vacancy with tags and important_links
    print("\n--- Testing POST /api/admin/vacancies (with tags & important_links) ---")
    
    vacancy_payload = {
        "title": "Test Manual Vacancy Links",
        "organization": "Test Org",
        "category": "other",
        "tags": ["10th pass", "haryana", "latest"],
        "important_links": [
            {
                "label": "Notification",
                "url": "https://example.com/notif.pdf",
                "type": "pdf"
            },
            {
                "label": "Apply Online",
                "url": "https://example.com/apply",
                "type": "link"
            }
        ]
    }
    
    resp = admin_session.post(f"{BASE_URL}/admin/vacancies", json=vacancy_payload)
    
    if resp.status_code != 200:
        log_fail("POST manual vacancy", f"Status {resp.status_code}: {resp.text}")
        return
    
    created_vacancy = resp.json()
    vacancy_id = created_vacancy.get("id")
    
    if not vacancy_id:
        log_fail("POST manual vacancy", "No id in response")
        return
    
    log_pass("POST manual vacancy", f"Created vacancy ID: {vacancy_id}")
    
    # Test 7.2: GET vacancy and verify tags and important_links
    print("\n--- Testing GET /api/vacancies/{id} (verify tags & important_links) ---")
    
    resp = requests.get(f"{BASE_URL}/vacancies/{vacancy_id}")
    
    if resp.status_code != 200:
        log_fail("GET manual vacancy", f"Status {resp.status_code}: {resp.text}")
        # Cleanup attempt
        admin_session.delete(f"{BASE_URL}/admin/vacancies/{vacancy_id}")
        return
    
    vacancy_data = resp.json()
    
    # Verify tags
    returned_tags = vacancy_data.get("tags", [])
    expected_tags = ["10th pass", "haryana", "latest"]
    
    if set(returned_tags) == set(expected_tags):
        log_pass("GET manual vacancy (tags)", f"Tags match: {returned_tags}")
    else:
        log_fail("GET manual vacancy (tags)", f"Expected {expected_tags}, got {returned_tags}")
    
    # Verify important_links
    returned_links = vacancy_data.get("important_links", [])
    
    if len(returned_links) != 2:
        log_fail("GET manual vacancy (important_links)", 
                f"Expected 2 links, got {len(returned_links)}")
    else:
        # Check first link (Notification PDF)
        link1 = returned_links[0]
        if (link1.get("label") == "Notification" and 
            link1.get("url") == "https://example.com/notif.pdf" and 
            link1.get("type") == "pdf"):
            log_pass("GET manual vacancy (important_links[0])", 
                    f"First link correct: {link1}")
        else:
            log_fail("GET manual vacancy (important_links[0])", 
                    f"First link mismatch: {link1}")
        
        # Check second link (Apply Online)
        link2 = returned_links[1]
        if (link2.get("label") == "Apply Online" and 
            link2.get("url") == "https://example.com/apply" and 
            link2.get("type") == "link"):
            log_pass("GET manual vacancy (important_links[1])", 
                    f"Second link correct: {link2}")
        else:
            log_fail("GET manual vacancy (important_links[1])", 
                    f"Second link mismatch: {link2}")
    
    # Test 7.3: PUT update tags and important_links
    print("\n--- Testing PUT /api/admin/vacancies/{id} (update tags & important_links) ---")
    
    update_payload = {
        "title": "Test Manual Vacancy Links",
        "organization": "Test Org",
        "category": "other",
        "tags": ["updated"],
        "important_links": [
            {
                "label": "Syllabus",
                "url": "https://example.com/s.pdf",
                "type": "pdf"
            }
        ]
    }
    
    resp = admin_session.put(f"{BASE_URL}/admin/vacancies/{vacancy_id}", json=update_payload)
    
    if resp.status_code != 200:
        log_fail("PUT manual vacancy", f"Status {resp.status_code}: {resp.text}")
        # Cleanup
        admin_session.delete(f"{BASE_URL}/admin/vacancies/{vacancy_id}")
        return
    
    log_pass("PUT manual vacancy", "Update successful")
    
    # Test 7.4: GET again to verify update persisted
    print("\n--- Testing GET /api/vacancies/{id} (verify update persisted) ---")
    
    resp = requests.get(f"{BASE_URL}/vacancies/{vacancy_id}")
    
    if resp.status_code != 200:
        log_fail("GET manual vacancy (after update)", f"Status {resp.status_code}: {resp.text}")
        # Cleanup
        admin_session.delete(f"{BASE_URL}/admin/vacancies/{vacancy_id}")
        return
    
    updated_vacancy = resp.json()
    
    # Verify updated tags
    updated_tags = updated_vacancy.get("tags", [])
    if updated_tags == ["updated"]:
        log_pass("GET manual vacancy (updated tags)", f"Tags updated correctly: {updated_tags}")
    else:
        log_fail("GET manual vacancy (updated tags)", f"Expected ['updated'], got {updated_tags}")
    
    # Verify updated important_links
    updated_links = updated_vacancy.get("important_links", [])
    
    if len(updated_links) != 1:
        log_fail("GET manual vacancy (updated important_links)", 
                f"Expected 1 link, got {len(updated_links)}")
    else:
        link = updated_links[0]
        if (link.get("label") == "Syllabus" and 
            link.get("url") == "https://example.com/s.pdf" and 
            link.get("type") == "pdf"):
            log_pass("GET manual vacancy (updated important_links)", 
                    f"Link updated correctly: {link}")
        else:
            log_fail("GET manual vacancy (updated important_links)", 
                    f"Link mismatch: {link}")
    
    # Test 7.5: DELETE cleanup
    print("\n--- Testing DELETE /api/admin/vacancies/{id} (cleanup) ---")
    
    resp = admin_session.delete(f"{BASE_URL}/admin/vacancies/{vacancy_id}")
    
    if resp.status_code == 200:
        log_pass("DELETE manual vacancy", "Cleanup successful")
    else:
        log_fail("DELETE manual vacancy", f"Status {resp.status_code}: {resp.text}")

def test_search_analytics():
    """Test 8: Search analytics - logging and admin endpoint"""
    print("\n" + "="*80)
    print("TEST 8: SEARCH ANALYTICS")
    print("="*80)
    
    # Test 8.1: Search logging - make searches that should be logged
    print("\n--- Testing Search Logging (GET /api/vacancies?q=...) ---")
    
    # Search for "police" multiple times (should have results)
    print("Searching for 'police' (3 times)...")
    for i in range(3):
        resp = requests.get(f"{BASE_URL}/vacancies?q=police&page=1")
        if resp.status_code == 200:
            data = resp.json()
            if i == 0:
                log_pass("Search logging (police)", 
                        f"Search returned {data.get('total', 0)} results, should log silently")
        else:
            log_fail("Search logging (police)", f"Search failed with status {resp.status_code}")
        time.sleep(0.3)
    
    # Search for nonsense term that returns 0 results
    print("Searching for 'zzqqxx-nomatch' (should return 0 results)...")
    resp = requests.get(f"{BASE_URL}/vacancies?q=zzqqxx-nomatch&page=1")
    if resp.status_code == 200:
        data = resp.json()
        if data.get('total', -1) == 0:
            log_pass("Search logging (zero results)", 
                    "Search for 'zzqqxx-nomatch' returned 0 results, should log silently")
        else:
            log_fail("Search logging (zero results)", 
                    f"Expected 0 results, got {data.get('total', -1)}")
    else:
        log_fail("Search logging (zero results)", f"Search failed with status {resp.status_code}")
    
    # Wait a moment for logs to be written
    time.sleep(1)
    
    # Test 8.2: GET /api/admin/search-analytics without auth
    print("\n--- Testing GET /api/admin/search-analytics (no auth) ---")
    resp = requests.get(f"{BASE_URL}/admin/search-analytics")
    if resp.status_code in [401, 403]:
        log_pass("Search analytics (no auth)", f"Correctly rejected with {resp.status_code}")
    else:
        log_fail("Search analytics (no auth)", f"Expected 401/403, got {resp.status_code}")
    
    # Test 8.3: GET /api/admin/search-analytics with admin auth
    print("\n--- Testing GET /api/admin/search-analytics (with auth) ---")
    admin_session = admin_login()
    if not admin_session:
        log_fail("Search analytics (with auth)", "Admin login failed")
        return
    
    resp = admin_session.get(f"{BASE_URL}/admin/search-analytics")
    
    if resp.status_code != 200:
        log_fail("Search analytics (with auth)", f"Status {resp.status_code}: {resp.text}")
        return
    
    data = resp.json()
    
    # Verify response structure
    required_keys = ["days", "total_searches", "unique_terms", "top", "zero_results"]
    missing_keys = [k for k in required_keys if k not in data]
    
    if missing_keys:
        log_fail("Search analytics structure", f"Missing keys: {missing_keys}")
        return
    
    log_pass("Search analytics structure", 
            f"All required keys present: days={data['days']}, "
            f"total_searches={data['total_searches']}, "
            f"unique_terms={data['unique_terms']}")
    
    # Verify data types
    if not isinstance(data['days'], int):
        log_fail("Search analytics (days type)", f"days should be int, got {type(data['days'])}")
    else:
        log_pass("Search analytics (days type)", f"days is int: {data['days']}")
    
    if not isinstance(data['total_searches'], int):
        log_fail("Search analytics (total_searches type)", 
                f"total_searches should be int, got {type(data['total_searches'])}")
    else:
        log_pass("Search analytics (total_searches type)", 
                f"total_searches is int: {data['total_searches']}")
    
    if not isinstance(data['unique_terms'], int):
        log_fail("Search analytics (unique_terms type)", 
                f"unique_terms should be int, got {type(data['unique_terms'])}")
    else:
        log_pass("Search analytics (unique_terms type)", 
                f"unique_terms is int: {data['unique_terms']}")
    
    if not isinstance(data['top'], list):
        log_fail("Search analytics (top type)", f"top should be list, got {type(data['top'])}")
        return
    else:
        log_pass("Search analytics (top type)", f"top is list with {len(data['top'])} items")
    
    if not isinstance(data['zero_results'], list):
        log_fail("Search analytics (zero_results type)", 
                f"zero_results should be list, got {type(data['zero_results'])}")
        return
    else:
        log_pass("Search analytics (zero_results type)", 
                f"zero_results is list with {len(data['zero_results'])} items")
    
    # Test 8.4: Verify "police" appears in top with count>=2
    print("\n--- Verifying 'police' in top searches ---")
    top_searches = data['top']
    
    police_found = False
    for item in top_searches:
        if 'police' in item.get('query', '').lower():
            police_found = True
            count = item.get('count', 0)
            if count >= 2:
                log_pass("Search analytics (police in top)", 
                        f"'police' found in top with count={count} (>=2): {item}")
            else:
                log_fail("Search analytics (police in top)", 
                        f"'police' found but count={count} (<2): {item}")
            break
    
    if not police_found:
        log_fail("Search analytics (police in top)", 
                "'police' not found in top searches (may need more time for logs to process)")
    
    # Test 8.5: Verify "zzqqxx-nomatch" appears in zero_results
    print("\n--- Verifying 'zzqqxx-nomatch' in zero_results ---")
    zero_results_list = data['zero_results']
    
    nomatch_found = False
    for item in zero_results_list:
        if 'zzqqxx-nomatch' in item.get('query', '').lower():
            nomatch_found = True
            avg_results = item.get('avg_results', -1)
            if avg_results == 0:
                log_pass("Search analytics (zzqqxx-nomatch in zero_results)", 
                        f"'zzqqxx-nomatch' found with avg_results=0: {item}")
            else:
                log_fail("Search analytics (zzqqxx-nomatch in zero_results)", 
                        f"'zzqqxx-nomatch' found but avg_results={avg_results} (expected 0): {item}")
            break
    
    if not nomatch_found:
        log_fail("Search analytics (zzqqxx-nomatch in zero_results)", 
                "'zzqqxx-nomatch' not found in zero_results (may need more time for logs to process)")
    
    # Test 8.6: Verify top array structure and sorting
    print("\n--- Verifying top array structure and sorting ---")
    if top_searches:
        first_item = top_searches[0]
        required_item_keys = ["query", "count", "avg_results", "last_at"]
        missing_item_keys = [k for k in required_item_keys if k not in first_item]
        
        if missing_item_keys:
            log_fail("Search analytics (top item structure)", 
                    f"Missing keys in top item: {missing_item_keys}")
        else:
            log_pass("Search analytics (top item structure)", 
                    f"Top item has all required keys: {required_item_keys}")
        
        # Verify sorting by count descending
        counts = [item.get('count', 0) for item in top_searches]
        if counts == sorted(counts, reverse=True):
            log_pass("Search analytics (top sorting)", 
                    f"Top array correctly sorted by count descending: {counts[:5]}...")
        else:
            log_fail("Search analytics (top sorting)", 
                    f"Top array not sorted correctly: {counts[:5]}...")
    
    # Test 8.7: Test days query parameter
    print("\n--- Testing days query parameter ---")
    resp = admin_session.get(f"{BASE_URL}/admin/search-analytics?days=7")
    
    if resp.status_code == 200:
        data_7days = resp.json()
        if data_7days.get('days') == 7:
            log_pass("Search analytics (days param)", 
                    f"days parameter works: requested 7, got {data_7days['days']}")
        else:
            log_fail("Search analytics (days param)", 
                    f"days parameter mismatch: requested 7, got {data_7days.get('days')}")
    else:
        log_fail("Search analytics (days param)", 
                f"Status {resp.status_code}: {resp.text}")

def main():
    print("="*80)
    print("HR DIGITAL SERVICES - BACKEND API TESTS (SEARCH ANALYTICS)")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Admin: {ADMIN_EMAIL}")
    print("="*80)
    
    # Run search analytics tests
    test_search_analytics()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✅ PASSED: {len(results['passed'])}")
    print(f"❌ FAILED: {len(results['failed'])}")
    
    if results['failed']:
        print("\nFailed tests:")
        for test in results['failed']:
            print(f"  - {test}")
    
    print("="*80)
    
    return 0 if not results['failed'] else 1

if __name__ == "__main__":
    exit(main())
