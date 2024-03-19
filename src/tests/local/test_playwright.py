from axe_playwright_python.sync_playwright import Axe
from playwright.sync_api import Page, expect


def check_for_violations(page: Page):
    results = Axe().run(page)
    assert results.violations_count == 0, results.generate_report()


def test_home(page: Page, live_server_url: str):
    """Test that the home page loads"""
    page.goto(live_server_url)
    expect(page).to_have_title("Polonius - AI Summarization and Classification of critical patient data")
    check_for_violations(page)
