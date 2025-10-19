from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Register cssd_user1
    page.goto("http://127.0.0.1:5000/register")
    page.locator("#username").fill("cssduser1")
    page.locator("#password").fill("password")
    page.locator("#confirm_password").fill("password")
    page.get_by_label("Role").select_option(label='CSSD User')
    page.get_by_label("Unit").select_option(label='Emergency Room')
    page.get_by_role("button", name="Sign Up").click()

    # Login as cssd_user1
    page.goto("http://127.0.0.1:5000/login")
    page.locator("#username").fill("cssduser1")
    page.locator("#password").fill("password")
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_role("heading", name="Welcome to SiAPPMEN")).to_be_visible()

    # Create a new loan
    page.goto("http://127.0.0.1:5000/loan/new")
    page.get_by_label("Unit").select_option(label='Emergency Room')
    page.get_by_label("Instrument").select_option(label='Scalpel 2')
    page.get_by_role("button", name="Create Loan").click()
    qr_code_url = page.url
    qr_code = qr_code_url.split('/')[-1]

    # Logout
    page.goto("http://127.0.0.1:5000/logout")

    # Register cssd_user2
    page.goto("http://127.0.0.1:5000/register")
    page.locator("#username").fill("cssduser2")
    page.locator("#password").fill("password")
    page.locator("#confirm_password").fill("password")
    page.get_by_label("Role").select_option(label='CSSD User')
    page.get_by_label("Unit").select_option(label='Operating Room 1')
    page.get_by_role("button", name="Sign Up").click()

    # Login as cssd_user2
    page.goto("http://127.0.0.1:5000/login")
    page.locator("#username").fill("cssduser2")
    page.locator("#password").fill("password")
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_role("heading", name="Welcome to SiAPPMEN")).to_be_visible()

    # Attempt to access the QR code for the first user's loan
    page.goto(f"http://127.0.0.1:5000/qr_code/{qr_code}")

    # Assert that the user is able to see the page
    expect(page.get_by_role("heading", name="Transaction QR Code")).to_be_visible()

    page.screenshot(path="jules-scratch/verification/idor_test.png")

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)