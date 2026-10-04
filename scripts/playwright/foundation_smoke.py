from pathlib import Path

from playwright.sync_api import sync_playwright


SCREENSHOT = Path("/tmp/ledgerlens-foundation.png")


def main() -> None:
    console_errors: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.on(
            "console",
            lambda message: console_errors.append(message.text)
            if message.type == "error"
            else None,
        )
        page.goto("http://127.0.0.1:5173", wait_until="networkidle")

        assert page.get_by_role("heading", name="Answers are easy. Proof is the product.").is_visible()
        assert page.get_by_text("Foundation online").is_visible()
        assert page.locator(".ledger-row").count() == 5
        assert page.locator(".status-chip.ready").count() == 1
        assert page.locator(".status-chip.planned").count() == 4
        assert page.locator(".notice").count() == 0
        page.screenshot(path=str(SCREENSHOT), full_page=True)

        page.set_viewport_size({"width": 390, "height": 844})
        page.reload(wait_until="networkidle")
        overflow = page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth")
        assert not overflow, "mobile page has horizontal overflow"
        assert page.get_by_text("Foundation online").is_visible()
        assert not console_errors, f"browser console errors: {console_errors}"
        browser.close()

    print(f"browser foundation smoke passed; screenshot: {SCREENSHOT}")


if __name__ == "__main__":
    main()

