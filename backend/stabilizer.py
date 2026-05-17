from playwright.async_api import TimeoutError
import asyncio


async def remove_annoying_ui(page):

    await page.evaluate("""
    () => {

        const selectors = [

            //
            // Angular overlays
            //

            '.cdk-overlay-container',
            '.cdk-overlay-backdrop',
            '.cdk-overlay-pane',

            //
            // Dialogs/modals
            //

            '[role="dialog"]',
            '.modal',
            '.popup',

            //
            // Tooltips / coachmarks
            //

            '.mat-mdc-tooltip',
            '.tooltip',
            '.shepherd-element',

            //
            // Floating banners
            //

            '.cc-window',
            '.cc-banner',

            //
            // Fixed-position overlays
            //

            '.tour',
            '.introjs-overlay',
        ];

        selectors.forEach(selector => {

            document
                .querySelectorAll(selector)
                .forEach(el => {
                    el.remove();
                });

        });

        //
        // Remove suspicious fixed overlays
        //

        [...document.querySelectorAll('*')]
            .forEach(el => {

                const style = window.getComputedStyle(el);

                const z = parseInt(style.zIndex || '0');

                if (
                    style.position === 'fixed'
                    && z > 1000
                ) {

                    el.remove();

                }

            });

    }
    """)

async def try_click(page, selector):

    try:
        locator = page.locator(selector)

        if await locator.count() > 0:

            if await locator.first.is_visible():

                await locator.first.click(
                    timeout=2000,
                    force=True
                )

                await page.wait_for_timeout(500)

                print(f"Clicked: {selector}")

                return True

    except Exception as e:
        print(f"Failed: {selector} -> {e}")

    return False


async def remove_overlays(page):

    overlays = page.locator(
        ".cdk-overlay-backdrop"
    )

    count = await overlays.count()

    for i in range(count):

        try:
            await overlays.nth(i).click(force=True)
        except:
            pass

async def dismiss_random_dialogs(page):

    #
    # Common modal/dialog selectors
    #

    dialog_selectors = [
        '[role="dialog"]',
        '.cdk-overlay-pane',
        '.mat-mdc-dialog-container',
        '.modal',
        '.popup',
    ]

    #
    # Generic close button selectors
    #

    close_selectors = [
        'button[aria-label*="close" i]',
        'button[title*="close" i]',
        '[aria-label*="dismiss" i]',
        '.close',
        '.dialog-close',
        '.mat-mdc-dialog-close',
        'button:has(svg)',
        'button:has(mat-icon)',
    ]

    for dialog_selector in dialog_selectors:

        dialogs = page.locator(dialog_selector)

        count = await dialogs.count()

        for i in range(count):

            dialog = dialogs.nth(i)

            try:

                if await dialog.is_visible():

                    print(
                        f"Visible dialog detected: {dialog_selector}"
                    )

                    #
                    # Try generic close buttons
                    #

                    for close_selector in close_selectors:

                        close_buttons = dialog.locator(
                            close_selector
                        )

                        button_count = (
                            await close_buttons.count()
                        )

                        for j in range(button_count):

                            try:

                                button = close_buttons.nth(j)

                                if await button.is_visible():

                                    await button.click(
                                        force=True
                                    )

                                    await page.wait_for_timeout(
                                        500
                                    )

                                    print(
                                        "Dialog dismissed."
                                    )

                                    return

                            except:
                                pass

                    #
                    # Fallback:
                    # press Escape
                    #

                    await page.keyboard.press(
                        "Escape"
                    )

                    await page.wait_for_timeout(500)

            except:
                pass

async def stabilize_page(page):

    print("Stabilizing page...")
    
    await remove_annoying_ui(page)

    selectors = [
        'button:has-text("Dismiss")',
        'button:has-text("Skip")',
        'button:has-text("No thanks")',
        'button:has-text("Me want it!")',
        '[aria-label="Close Welcome Banner"]',
    ]

    #
    # Multiple stabilization passes
    #

    for _ in range(2):

        #
        # Try selectors repeatedly
        #

        for selector in selectors:
            await try_click(page, selector)

        #
        # Remove Angular overlays
        #

        await dismiss_random_dialogs(page)

        await remove_overlays(page)

        #
        # Escape key cleanup
        #

        try:
            await page.keyboard.press("Escape")
        except:
            pass

        #
        # Wait briefly for async dialogs
        #

        await asyncio.sleep(1)

    #
    # Final wait
    #

    try:
        await page.wait_for_load_state("networkidle")
    except:
        pass

    print("Stabilization complete.")