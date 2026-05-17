import hashlib


async def get_state_hash(page):

    content = await page.content()

    return hashlib.md5(
        content.encode()
    ).hexdigest()