from playwright.async_api import async_playwright
import uuid


async def execute_flow(url: str, flow: dict):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)

        page = await browser.new_page()

        console_errors = []

        page.on(
            "console",
            lambda msg: console_errors.append(msg.text)
            if msg.type == "error"
            else None,
        )

        await page.goto(url)

        action_log = []

        try:
            for action in flow["actions"]:
                if action["action"] == "click":
                    await page.locator(action["selector"]).click()

                elif action["action"] == "fill":
                    await page.locator(action["selector"]).fill(
                        action["value"]
                    )

                action_log.append(action)

                await page.wait_for_timeout(1000)

            body = await page.content()

            bug_detected = False
            reasons = []

            if "error" in body.lower():
                bug_detected = True
                reasons.append("Error text detected in UI")

            if len(console_errors) > 0:
                bug_detected = True
                reasons.append("Console errors detected")

            screenshot_path = (
                f"runs/screenshots/{uuid.uuid4()}.png"
            )

            await page.screenshot(path=screenshot_path)

            result = {
                "flow": flow["name"],
                "bug_detected": bug_detected,
                "reasons": reasons,
                "console_errors": console_errors,
                "screenshot": screenshot_path,
                "actions": action_log,
            }

            await browser.close()

            return result

        except Exception as e:
            screenshot_path = (
                f"runs/screenshots/{uuid.uuid4()}.png"
            )

            await page.screenshot(path=screenshot_path)

            }