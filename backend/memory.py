from collections import defaultdict


class Memory:
    def __init__(self):
        self.pages = {}
        self.transitions = defaultdict(list)
        self.failures = []
        self.successful_flows = []

    def remember_page(self, url, elements):
        self.pages[url] = {
            "elements": elements,
        }

    def remember_transition(self, from_page, action, to_page):
        self.transitions[from_page].append({
            "action": action,
            "to": to_page,
        })

    def remember_failure(self, failure):
        self.failures.append(failure)

    def remember_successful_flow(self, flow):
        self.successful_flows.append(flow)

    def get_known_pages(self):
        return list(self.pages.keys())