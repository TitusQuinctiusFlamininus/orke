from playwright.async_api import async_playwright

from stabilizer import stabilize_page

from frontier_explorer import explore_frontier

from memory import Memory

import os


async def run_agent(url: str):

    memory = Memory()

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-features=Translate",
                "--disable-popup-blocking",
                "--disable-notifications",
            ],
        )

        storage_state = None

        if os.path.exists(
            "runs/browser_state.json"
        ):
            storage_state = (
                "runs/browser_state.json"
            )

        context = await browser.new_context(
            locale="en-US",
            storage_state=storage_state
        )

        page = await context.new_page()

        #
        # Navigate to app
        #

        await page.goto(
            url,
            wait_until="domcontentloaded"
        )

        #
        # Initial stabilization
        #

        await stabilize_page(page)

        #
        # Persist session
        #

        await context.storage_state(
            path="runs/browser_state.json"
        )

        #
        # Begin recursive exploration
        #

        await explore_frontier(
            page,
            memory
        )

        await browser.close()

    return {
    "visited_pages": list(
        memory.visited_urls
    ),
    "total_pages": len(
        memory.visited_urls
    ),
    "transitions": memory.transitions,
    "page_actions": {
        url: list(actions)
        for url, actions
        in memory.page_actions.items()
    }
}