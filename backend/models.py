from pydantic import BaseModel
from typing import List


class UIElement(BaseModel):
    text: str
    role: str
    selector: str


class AgentAction(BaseModel):
    action: str
    selector: str
    value: str | None = None


class BugReport(BaseModel):
    title: str
    severity: str
    steps: List[str]
    expected: str
    actual: str
    screenshot: str