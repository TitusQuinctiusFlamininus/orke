from explorer import extract_elements
from bug_detector import execute_action
from stabilizer import stabilize_page

import asyncio
import random


MAX_DEPTH = 6


TEST_INPUTS = [
    "test",
    "admin",
    "' OR 1=1 --",
    "<script>alert(1)</script>",
    "🔥🔥🔥",
]


async def recursive_explore(
    page,
    memory,
    depth=0
):

    if depth > MAX_DEPTH:
        return

    #
    # Stabilize current state
    #

    await stabilize_page(page)

    current_url = page.url

    print(f"\nCURRENT URL: {current_url}")

    #
    # First visit?
    #

    is_new_page = (
        not memory.has_seen_url(current_url)
    )

    if is_new_page:

        print(f"NEW PAGE: {current_url}")

        memory.remember_url(current_url)

    else:

        print(
            f"Known page: {current_url}"
        )

    #
    # Extract visible elements
    #

    elements = await extract_elements(page)

    #
    # Randomize traversal
    #

    random.shuffle(elements)

    #
    # Explore local actions
    #

    for element in elements:

        selector = element.get("selector")

        if not selector:
            continue

        #
        # Skip already explored actions
        # ON THIS PAGE
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

        print(f"Trying selector: {selector}")

        try:

            previous_url = page.url

            #
            # INPUTS
            #

            if "input" in selector.lower():

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
            # CLICK ACTION
            #

            await execute_action(page, {
                "action": "click",
                "selector": selector,
                "value": None,
            })

            await asyncio.sleep(1)

            new_url = page.url

            #
            # Save transition
            #

            memory.remember_transition(
                previous_url,
                new_url,
                selector
            )

            #
            # Detect page change
            #

            page_changed = (
                new_url != previous_url
            )

            #
            # NEW PAGE
            #

            if page_changed:

                if not memory.has_seen_url(
                    new_url
                ):

                    print(
                        f"DISCOVERED: {new_url}"
                    )

                    #
                    # Explore NEW page deeply
                    #

                    await recursive_explore(
                        page,
                        memory,
                        depth + 1
                    )

                else:

                    print(
                        f"Already explored: {new_url}"
                    )

                #
                # Return ONE level
                #

                try:

                    await page.go_back()

                    await asyncio.sleep(1)

                    await stabilize_page(page)

                except Exception as back_error:

                    print(
                        f"Back navigation failed: {back_error}"
                    )

            #
            # Same-page interactions
            #

            else:

                #
                # Recurse shallowly
                # because local UI state changed
                #

                await recursive_explore(
                    page,
                    memory,
                    depth + 1
                )

        except Exception as e:

            print(f"Exploration failed: {e}")

            #
            # Local recovery only
            #

            try:

                await stabilize_page(page)

            except Exception as recovery_error:

                print(
                    f"Recovery failed: {recovery_error}"
                )