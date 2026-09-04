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

def main():
    print("="*80)
    print("HR DIGITAL SERVICES - BACKEND API TESTS")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Admin: {ADMIN_EMAIL}")
    print("="*80)
    
    # Run all tests
    test_vacancy_search()
    test_view_counter()
    test_reviews()
    test_custom_head()
    
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
