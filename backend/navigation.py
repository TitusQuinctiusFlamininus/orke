from bug_detector import execute_action

import asyncio


async def replay_path(
    page,
    path
):

    print(f"Replaying path: {path}")

    for action in path:

        try:

            await execute_action(page, action)

            await asyncio.sleep(1)

        except Exception as e:

            print(f"Replay failed: {e}")

            return False

    return True