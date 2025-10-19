import re
from playwright.sync_api import sync_playwright, expect

def run_verification(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    BASE_URL = "http://127.0.0.1:5000"

    # --- Step 1: Log in as CSSD user and create two loans for different units ---
    page.goto(f"{BASE_URL}/login")
    page.get_by_label("Username").fill("cssd_user")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url(re.compile(r".*/home"))

    # Create loan for Emergency Room (Unit ID 1)
    page.goto(f"{BASE_URL}/loan/new")
    page.get_by_label("Instrument").select_option("1") # Scalpel
    page.get_by_label("Unit").select_option("1") # Emergency Room
    page.get_by_label("Patient Name").fill("Test Patient ER")
    page.get_by_role("button", name="Create Loan").click()
    expect(page).to_have_url(re.compile(r".*/qr_code/.*"))
    er_transaction_url = page.url

    # Create loan for Operating Room (Unit ID 2)
    page.goto(f"{BASE_URL}/loan/new")
    page.get_by_label("Instrument").select_option("2") # Forceps
    page.get_by_label("Unit").select_option("2") # Operating Room
    page.get_by_label("Patient Name").fill("Test Patient OR")
    page.get_by_role("button", name="Create Loan").click()
    expect(page).to_have_url(re.compile(r".*/qr_code/.*"))
    or_transaction_url = page.url

    page.goto(f"{BASE_URL}/logout")
    expect(page).to_have_url(re.compile(r".*/home"))

    # --- Step 2: Log in as Operating Room user and attempt to access ER transaction (SHOULD FAIL) ---
    page.goto(f"{BASE_URL}/login")
    page.get_by_label("Username").fill("or_user")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url(re.compile(r".*/home"))

    # Attempt to access the other unit's transaction
    page.goto(er_transaction_url)

    # Assert redirection and flash message
    expect(page).to_have_url(re.compile(r".*/home"))
    flash_message = page.locator(".alert-danger")
    expect(flash_message).to_be_visible()
    expect(flash_message).to_have_text("You are not authorized to view this transaction.")

    # Take screenshot of the failed attempt
    page.screenshot(path="jules-scratch/verification/idor_fix_verification.png")

    page.goto(f"{BASE_URL}/logout")

    # --- Step 3: Log in as Emergency Room user and access their own transaction (SHOULD PASS) ---
    page.goto(f"{BASE_URL}/login")
    page.get_by_label("Username").fill("er_user")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url(re.compile(r".*/home"))

    page.goto(er_transaction_url)
    expect(page).to_have_url(er_transaction_url)
    expect(page.get_by_text("Test Patient ER")).to_be_visible()

    page.goto(f"{BASE_URL}/logout")

    # --- Step 4: Log in as CSSD user and access both transactions (SHOULD PASS) ---
    page.goto(f"{BASE_URL}/login")
    page.get_by_label("Username").fill("cssd_user")
    page.get_by_label("Password").fill("password")
    page.get_by_role("button", name="Login").click()
    expect(page).to_have_url(re.compile(r".*/home"))

    page.goto(er_transaction_url)
    expect(page).to_have_url(er_transaction_url)
    expect(page.get_by_text("Test Patient ER")).to_be_visible()

    page.goto(or_transaction_url)
    expect(page).to_have_url(or_transaction_url)
    expect(page.get_by_text("Test Patient OR")).to_be_visible()

    print("Verification script completed successfully.")

    browser.close()

with sync_playwright() as playwright:
    run_verification(playwright)