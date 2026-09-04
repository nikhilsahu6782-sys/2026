#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  Add to the HR Digital Services app (blogs + vacancies):
  1) Per-post Verification code / custom <head> meta tag option (blogs + vacancies).
  2) Public reviews (star rating + comment) on posts; reviews show immediately; admin can hide/delete.
  3) View counter per post (blogs + vacancies) shown on the public page and in admin.
  4) Fix the Vacancies search bar — searching "gds", "india post" or "gramin dak" did not surface the
     "India Post — Gramin Dak Sevak – 23757 Posts" vacancy. Root cause: q was never sent to the server
     (client-side filtered only the 20 loaded rows). Added debounced server-side search + acronym synonyms.

backend:
  - task: "Vacancy search server-side + acronym synonyms (gds→gramin dak sevak)"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "GET /api/vacancies?q=... — added SEARCH_SYNONYMS expansion so 'gds' matches 'Gramin Dak Sevak'. Verify q=gds, q=india post, q=gramin dak all return the India Post GDS vacancy."
        -working: true
        -agent: "testing"
        -comment: "✅ VERIFIED: All 3 search queries (gds, india post, gramin dak) successfully return the 'India Post — Gramin Dak Sevak – 23757 Posts' vacancy. Synonym expansion working correctly. Response includes proper pagination (items, total, page, pages)."
  - task: "View counter increment on blog + vacancy detail GET"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "GET /api/blogs/{slug} and GET /api/vacancies/{id} now $inc views and return views. Verify views increments on repeated GETs."
        -working: true
        -agent: "testing"
        -comment: "✅ VERIFIED: Both blog and vacancy view counters increment correctly. Blog views: 4→5, Vacancy views: 8→9. Views field is returned in response and persists across requests."
  - task: "Reviews CRUD (public post/list, admin list/toggle/delete)"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "POST /api/reviews (public), GET /api/reviews?target_type=&target_id=, GET /api/admin/reviews, PUT /api/admin/reviews/{id}/toggle, DELETE /api/admin/reviews/{id}. Admin endpoints require admin auth. Verify average/count, hidden filtering, and admin moderation."
        -working: true
        -agent: "testing"
        -comment: "✅ VERIFIED: All review endpoints working correctly. POST creates reviews for both blog and vacancy. GET returns {items, count, average} with correct calculations. Invalid target_type correctly rejected with 400. Admin endpoints: GET returns reviews with target_title, toggle hides/unhides reviews (hidden reviews excluded from public GET), DELETE removes reviews. Auth correctly enforced (401/403 without credentials)."
  - task: "Custom head / verification meta per post (blogs via form, vacancies via /seo)"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "Blog create/update accept custom_head form field; PUT /api/admin/vacancies/{id}/seo accepts custom_head. Verify persisted + returned in GET."
        -working: true
        -agent: "testing"
        -comment: "✅ VERIFIED: Custom head functionality working for both blogs and vacancies. Blog: PUT /api/admin/blogs/{id} with custom_head form field persists and returns in GET /api/blogs/{slug}. Vacancy: PUT /api/admin/vacancies/{id}/seo with custom_head JSON field persists and returns in GET /api/vacancies/{id}. Tested with Google site verification meta tag."

frontend:
  - task: "Vacancies search box triggers debounced server search"
    implemented: true
    working: "NA"
    file: "frontend/src/pages/Vacancies.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "Needs user permission before automated frontend testing."
  - task: "Reviews UI + views on BlogDetail/VacancyDetail; admin Reviews page; custom_head admin fields"
    implemented: true
    working: "NA"
    file: "frontend/src/components/Reviews.jsx"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "Needs user permission before automated frontend testing."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "Vacancy search server-side + acronym synonyms (gds→gramin dak sevak)"
    - "View counter increment on blog + vacancy detail GET"
    - "Reviews CRUD (public post/list, admin list/toggle/delete)"
    - "Custom head / verification meta per post (blogs via form, vacancies via /seo)"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
    -agent: "main"
    -message: |
      Please test the new backend endpoints. Admin auth: login via POST /api/auth/login (or admin login) with
      ADMIN_EMAIL=admin@hrdigitalservices.in / ADMIN_PASSWORD=Admin@12345 (cookie-based). Focus on:
      1) Search: GET /api/vacancies?q=gds , q=india%20post , q=gramin%20dak — each must include the vacancy titled
         "India Post — Gramin Dak Sevak – 23757 Posts".
      2) Views: GET a blog slug / vacancy id twice; views should increment and be returned.
      3) Reviews: POST /api/reviews for a blog and a vacancy, GET /api/reviews returns them with count+average;
         admin GET/toggle(hide)/delete work and hidden ones are excluded from public GET.
      4) custom_head: set via blog update + vacancy /seo, confirm persisted in GET responses.
    -agent: "testing"
    -message: |
      ✅ ALL BACKEND TESTS PASSED (20/20)
      
      Comprehensive testing completed for all 4 backend tasks:
      
      1. VACANCY SEARCH (3/3 tests passed):
         - GET /api/vacancies?q=gds ✅
         - GET /api/vacancies?q=india%20post ✅
         - GET /api/vacancies?q=gramin%20dak ✅
         All queries correctly return "India Post — Gramin Dak Sevak – 23757 Posts" vacancy.
         Synonym expansion (gds → gramin dak sevak) working perfectly.
      
      2. VIEW COUNTER (2/2 tests passed):
         - Blog view counter: increments correctly (4→5) ✅
         - Vacancy view counter: increments correctly (8→9) ✅
         Views persist and are returned in GET responses.
      
      3. REVIEWS CRUD (10/10 tests passed):
         - POST /api/reviews (blog) ✅
         - POST /api/reviews (vacancy) ✅
         - GET /api/reviews with count & average ✅
         - Invalid target_type rejection (400) ✅
         - GET /api/admin/reviews with target_title ✅
         - Admin auth enforcement (401/403) ✅
         - PUT /api/admin/reviews/{id}/toggle (hide) ✅
         - Hidden review exclusion from public GET ✅
         - PUT /api/admin/reviews/{id}/toggle (unhide) ✅
         - DELETE /api/admin/reviews/{id} ✅
      
      4. CUSTOM HEAD (4/4 tests passed):
         - Blog custom_head update via PUT /api/admin/blogs/{id} ✅
         - Blog custom_head returned in GET /api/blogs/{slug} ✅
         - Vacancy custom_head update via PUT /api/admin/vacancies/{id}/seo ✅
         - Vacancy custom_head returned in GET /api/vacancies/{id} ✅
      
      All endpoints functioning correctly with proper validation, authentication, and data persistence.