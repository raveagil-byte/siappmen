from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Register cssd_user
    page.goto("http://127.0.0.1:5000/register")
    page.locator("#username").fill("cssduser")
    page.locator("#password").fill("password")
    page.locator("#confirm_password").fill("password")
    page.get_by_label("Role").select_option(label='CSSD User')
    page.get_by_label("Unit").select_option(label='Emergency Room')
    page.get_by_role("button", name="Sign Up").click()

    # Login as cssd_user
    page.goto("http://127.0.0.1:5000/login")
    page.locator("#username").fill("cssduser")
    page.locator("#password").fill("password")
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_role("heading", name="Welcome to SiAPPMEN")).to_be_visible()

    # Create a new loan with a malicious script in the notes field
    page.goto("http://127.0.0.1:5000/loan/new")
    page.get_by_label("Unit").select_option(label='Emergency Room')
    page.get_by_label("Instrument").select_option(label='Scalpel 1')
    page.get_by_label("Notes").fill("<script>alert('XSS')</script>")
    page.get_by_role("button", name="Create Loan").click()

    # Check if the script is executed
    page.on("dialog", lambda dialog: dialog.accept())

    # Assert that the script is not executed and is instead displayed as text
    expect(page.get_by_text("<script>alert('XSS')</script>")).to_be_visible()

    page.screenshot(path="jules-scratch/verification/xss_test.png")

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)