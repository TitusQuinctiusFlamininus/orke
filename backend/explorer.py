from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


IGNORE_PATTERNS = [

    #
    # Cookie banners
    #

    "cookie",
    "dismiss",
    "close",
    "no thanks",
    "skip",
    "accept",
    "consent",

    #
    # Popup internals
    #

    "learn more",
    "wait!",
    "overlay",
    "dialog",

    #
    # Angular overlay internals
    #

    "cdk-overlay",

    #
    # Translation/browser junk
    #

    "translate",

    #
    # Repeated chrome controls
    #

    "search",
]

async def extract_elements(page):

    buttons = await page.locator(
        """
        button,
        a,
        input,
        textarea,
        [role="button"]
        """
    ).all()

    elements = []

    for idx, button in enumerate(buttons):

        try:

            text = await button.inner_text()

        except:
            text = ""

        try:

            aria = await button.get_attribute(
                "aria-label"
            )

        except:
            aria = None

        try:

            element_id = await button.get_attribute(
                "id"
            )

        except:
            element_id = None

        try:

            is_visible = await button.is_visible()

        except:
            is_visible = False

        #
        # Better selector generation
        #

        selector = None

        if element_id:

            selector = f"#{element_id}"

        elif aria:

            selector = (
                f'[aria-label="{aria}"]'
            )

        elif text:

            selector = f'text="{text}"'

        #
        # Ignore ephemeral UI controls
        #

        combined_text = (
            f"{text} {aria or ''}"
        ).lower()

        combined_selector = (
            selector or ""
        ).lower()

        should_ignore = any(
            pattern in combined_text
            or pattern in combined_selector
            for pattern in IGNORE_PATTERNS
        )

        if selector and not should_ignore:

            elements.append({
                "text": text,
                "selector": selector,
                "visible": is_visible,
            })

    return elements


async def explore_page(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
                    headless=False,
                    args=[
                        "--disable-features=Translate",
                        "--disable-popup-blocking",
                        "--disable-notifications",
                    ],
        )
        context = await browser.new_context(locale="en-US")
        page = await context.new_page()

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
            elif element.get("aria-label"):
                selector = f'[aria-label="{element.get("aria-label")}"]'
            elif text:
                selector = f'text="{text}"'
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