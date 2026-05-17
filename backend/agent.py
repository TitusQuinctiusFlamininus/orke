from explorer import explore_page
from planner import generate_test_plan
from bug_detector import execute_flow


async def run_agent(url: str):
    exploration = await explore_page(url)

    elements = exploration["elements"]

    plan = await generate_test_plan(elements)

    results = []

    for flow in plan.get("flows", []):
        result = await execute_flow(url, flow)
        results.append(result)

    return {
        "exploration": exploration,
        "results": results,
    }