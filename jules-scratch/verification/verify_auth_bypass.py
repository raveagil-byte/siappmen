from playwright.sync_api import sync_playwright, expect

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Register unit_user
    page.goto("http://127.0.0.1:5000/register")
    page.locator("#username").fill("unituser")
    page.locator("#password").fill("password")
    page.locator("#confirm_password").fill("password")
    page.get_by_label("Role").select_option(label='Unit User')
    page.get_by_label("Unit").select_option(label='Emergency Room')
    page.get_by_role("button", name="Sign Up").click()

    # Login as unit_user
    page.goto("http://127.0.0.1:5000/login")
    page.locator("#username").fill("unituser")
    page.locator("#password").fill("password")
    page.get_by_role("button", name="Login").click()
    expect(page.get_by_role("heading", name="Welcome to SiAPPMEN")).to_be_visible()

    # Attempt to access /loan/new
    page.goto("http://127.0.0.1:5000/loan/new")

    # Assert that the user is redirected to the home page
    expect(page).to_have_url("http://127.0.0.1:5000/home")

    # Assert that the flash message is displayed
    expect(page.get_by_text("You do not have permission to access this page.")).to_be_visible()

    page.screenshot(path="jules-scratch/verification/auth_bypass_test.png")

    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)