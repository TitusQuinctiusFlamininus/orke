from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


async def explore_page(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        page = await browser.new_page()

        await page.goto(url)

        await page.wait_for_timeout(2000)

        html = await page.content()

        soup = BeautifulSoup(html, "html.parser")

        elements = []

        buttons = soup.find_all(["button", "a", "input"])

        for idx, element in enumerate(buttons):
            text = element.get_text(strip=True)

            selector = None

            if element.get("id"):
                selector = f"#{element.get('id')}"
            elif element.get("name"):
                selector = f"[name='{element.get('name')}']"
            else:
                selector = f"nth={idx}"

            elements.append({
                "text": text,
                "tag": element.name,
                "selector": selector,
            })

        screenshot = "runs/screenshots/home.png"
        await page.screenshot(path=screenshot)

        await browser.close()

        return {
            "elements": elements,
            "screenshot": screenshot,
        }