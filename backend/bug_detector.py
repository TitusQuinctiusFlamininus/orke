from stabilizer import stabilize_page

import uuid


async def ensure_navigation_visible(page, selector):

    locator = page.locator(selector)

    #
    # If hidden, try opening sidenav
    #

    if await locator.count() > 0:

        if not await locator.first.is_visible():

            print(f"{selector} hidden. Opening sidenav.")

            try:

                menu_button = page.locator(
                    '[aria-label="Open Sidenav"]'
                )

                if await menu_button.count() > 0:

                    await menu_button.first.click()

                    await page.wait_for_timeout(1000)

            except Exception as e:
                print(f"Sidenav recovery failed: {e}")


async def execute_action(page, action):

    selector = action["selector"]

    locator = page.locator(selector)

    #
    # If hidden, attempt sidenav recovery
    #

    if await locator.count() > 0:

        if not await locator.first.is_visible():

            try:

                menu_button = page.locator(
                    '[aria-label="Open Sidenav"]'
                )

                if await menu_button.count() > 0:

                    await menu_button.first.click()

                    await page.wait_for_timeout(1000)

            except:
                pass

    #
    # Wait for visibility
    #

    await locator.wait_for(
        state="visible",
        timeout=5000
    )

    try:

        if action["action"] == "click":

            await locator.click(
                timeout=5000
            )

        elif action["action"] == "fill":

            await locator.fill(
                action["value"]
            )

    except Exception as e:

        print(f"ACTION FAILED: {e}")

        #
        # Overlay recovery
        #

        if "intercepts pointer events" in str(e):

            await stabilize_page(page)

            if action["action"] == "click":

                await locator.click(
                    force=True,
                    timeout=5000
                )

            elif action["action"] == "fill":

                await locator.fill(
                    action["value"]
                )

        else:
            raise e

    selector = action["selector"]

    locator = page.locator(selector)

    #
    # Attempt visibility recovery
    #

    await ensure_navigation_visible(
        page,
        selector
    )

    #
    # Wait for visibility
    #

    await locator.wait_for(
        state="visible",
        timeout=5000
    )

    try:

        #
        # CLICK
        #

        if action["action"] == "click":

            await locator.click(
                timeout=5000
            )

        #
        # FILL
        #

        elif action["action"] == "fill":

            await locator.fill(
                action["value"]
            )

    except Exception as e:

        print(f"ACTION FAILED: {e}")

        #
        # Overlay recovery
        #

        if "intercepts pointer events" in str(e):

            print("Overlay detected.")

            await stabilize_page(page)

            #
            # Retry click
            #

            if action["action"] == "click":

                await locator.click(
                    force=True,
                    timeout=5000
                )

            #
            # Retry fill
            #

            elif action["action"] == "fill":

                await locator.fill(
                    action["value"]
                )

        else:
            raise e


async def execute_flow(page, flow: dict):

    console_errors = []

    page.on(
        "console",
        lambda msg: console_errors.append(msg.text)
        if msg.type == "error"
        else None,
    )

    action_log = []

    try:

        print(f"RUNNING FLOW: {flow['name']}")

        #
        # Screenshot BEFORE flow
        #

        await page.screenshot(
            path=f"runs/screenshots/pre_{uuid.uuid4()}.png",
            full_page=True
        )

        #
        # Execute actions
        #

        for action in flow["actions"]:

            print(f"Executing: {action}")

            await execute_action(
                page,
                action
            )

            action_log.append(action)

            #
            # Small pacing delay
            #

            await page.wait_for_timeout(1000)

        #
        # Final screenshot
        #

        screenshot_path = (
            f"runs/screenshots/{uuid.uuid4()}.png"
        )

        await page.screenshot(
            path=screenshot_path,
            full_page=True
        )

        #
        # Bug heuristics
        #

        bug_detected = False

        reasons = []

        #
        # Console errors only
        #

        if len(console_errors) > 0:

            bug_detected = True

            reasons.append(
                "Console errors detected"
            )

        #
        # Successful result
        #

        return {
            "flow": flow["name"],
            "bug_detected": bug_detected,
            "reasons": reasons,
            "console_errors": console_errors,
            "screenshot": screenshot_path,
            "actions": action_log,
        }

    except Exception as e:

        screenshot_path = (
            f"runs/screenshots/{uuid.uuid4()}.png"
        )

        await page.screenshot(
            path=screenshot_path,
            full_page=True
        )

        return {
            "flow": flow["name"],
            "bug_detected": True,
            "reasons": [str(e)],
            "console_errors": console_errors,
            "screenshot": screenshot_path,
            "actions": action_log,
        }