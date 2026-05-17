from explorer import extract_elements
from bug_detector import execute_action
from stabilizer import stabilize_page

from urllib.parse import urlparse

import asyncio
import random


HOME_URL = "http://localhost:3000"

MAX_VISITS_PER_PAGE = 2


TEST_INPUTS = [
    "test",
    "admin",
    "hello",
    "' OR 1=1 --",
    "<script>alert(1)</script>",
    "🔥🔥🔥",
    "AAAAAAAAAAAAAAAAAAAA",
]


LOGIN_EMAIL = "admin@juice-sh.op"
LOGIN_PASSWORD = "admin123"


def is_local_url(url):

    try:

        parsed = urlparse(url)

        hostname = parsed.hostname

        return (
            hostname == "localhost"
            or hostname == "127.0.0.1"
        )

    except:
        return False


async def safe_back(page):

    try:

        await page.go_back()

        await asyncio.sleep(1)

        current_url = page.url

        #
        # Still external?
        #

        if not is_local_url(current_url):

            raise Exception(
                "Still external after go_back()"
            )

        return True

    except Exception as e:

        print(f"Back navigation failed: {e}")

        #
        # Hard reset
        #

        try:

            await page.goto(
                HOME_URL,
                wait_until="domcontentloaded"
            )

            await asyncio.sleep(1)

            await stabilize_page(page)

            return True

        except Exception as recovery_error:

            print(
                f"Homepage recovery failed: {recovery_error}"
            )

            return False


async def explore_frontier(
    page,
    memory
):

    #
    # Frontier queue:
    # list of urls to explore
    #

    frontier = [HOME_URL]

    #
    # Page visit counts
    #

    page_visit_counts = {}

    #
    # Main exploration loop
    #

    while frontier:

        current_url = frontier.pop(0)

        #
        # Avoid excessive revisits
        #

        visits = page_visit_counts.get(
            current_url,
            0
        )

        if visits >= MAX_VISITS_PER_PAGE:

            continue

        page_visit_counts[current_url] = (
            visits + 1
        )

        print(f"\nEXPLORING: {current_url}")

        #
        # Navigate to page
        #

        try:

            await page.goto(
                current_url,
                wait_until="domcontentloaded"
            )

            await asyncio.sleep(1)

            await stabilize_page(page)

        except Exception as e:

            print(
                f"Navigation failed: {e}"
            )

            continue

        #
        # Ignore external pages
        #

        if not is_local_url(page.url):

            print(
                f"External page detected: {page.url}"
            )

            await safe_back(page)

            continue

        #
        # Remember page
        #

        memory.remember_url(current_url)

        #
        # Extract visible elements
        #

        elements = await extract_elements(page)

        #
        # Randomize traversal
        #

        random.shuffle(elements)

        #
        # Explore elements
        #

        for element in elements:

            selector = element.get("selector")

            if not selector:
                continue

            #
            # Skip repeated page actions
            #

            if memory.has_seen_page_action(
                current_url,
                selector
            ):

                continue

            #
            # Mark action explored
            #

            memory.remember_page_action(
                current_url,
                selector
            )

            #
            # Skip selectors that already
            # lead to explored destinations
            #

            known_target = (
                memory.get_navigation_target(
                    selector
                )
            )

            if known_target:

                if memory.has_seen_url(
                    known_target
                ):

                    print(
                        f"Skipping known route: "
                        f"{selector} -> {known_target}"
                    )

                    continue

            print(f"Trying selector: {selector}")

            try:

                lower_selector = (
                    selector.lower()
                )

                #
                # EMAIL FIELDS
                #

                if (
                    "email" in lower_selector
                    or "mail" in lower_selector
                ):

                    await execute_action(page, {
                        "action": "fill",
                        "selector": selector,
                        "value": LOGIN_EMAIL,
                    })

                    await asyncio.sleep(1)

                    continue

                #
                # PASSWORD FIELDS
                #

                if (
                    "password" in lower_selector
                    or "passwd" in lower_selector
                ):

                    await execute_action(page, {
                        "action": "fill",
                        "selector": selector,
                        "value": LOGIN_PASSWORD,
                    })

                    await asyncio.sleep(1)

                    continue

                #
                # GENERIC INPUTS
                #

                if (
                    "input" in lower_selector
                    or "textarea" in lower_selector
                ):

                    value = random.choice(
                        TEST_INPUTS
                    )

                    await execute_action(page, {
                        "action": "fill",
                        "selector": selector,
                        "value": value,
                    })

                    await asyncio.sleep(1)

                    continue

                #
                # CLICK ACTIONS
                #

                previous_url = page.url

                await execute_action(page, {
                    "action": "click",
                    "selector": selector,
                    "value": None,
                })

                await asyncio.sleep(1)

                new_url = page.url

                #
                # Learn navigation result
                #

                if new_url != previous_url:

                    memory.remember_navigation_target(
                        selector,
                        new_url
                    )

                #
                # External navigation recovery
                #

                if not is_local_url(new_url):

                    print(
                        f"EXTERNAL URL: {new_url}"
                    )

                    await safe_back(page)

                    continue

                #
                # Track transition
                #

                memory.remember_transition(
                    previous_url,
                    new_url,
                    selector
                )

                #
                # New territory discovered
                #

                if (
                    new_url != previous_url
                    and not memory.has_seen_url(
                        new_url
                    )
                ):

                    print(
                        f"NEW TERRITORY: {new_url}"
                    )

                    frontier.append(new_url)

                #
                # Stabilize after actions
                #

                await stabilize_page(page)

            except Exception as e:

                print(
                    f"Exploration failed: {e}"
                )

                #
                # Local recovery
                #

                try:

                    await stabilize_page(page)

                except Exception as recovery_error:

                    print(
                        f"Recovery failed: {recovery_error}"
                    )

        print(
            f"FRONTIER SIZE: {len(frontier)}"
        )

    print("\nExploration complete.")