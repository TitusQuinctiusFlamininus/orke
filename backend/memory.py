class Memory:

    def __init__(self):

        #
        # Visited pages
        #

        self.visited_urls = set()

        #
        # Explored actions per URL
        #

        self.page_actions = {}

        #
        # Navigation transitions
        #

        self.transitions = []

        #
        # Path memory
        #

        self.paths = {}

        #
        # Navigation outcomes
        #

        self.navigation_targets = {}


    def remember_navigation_target(
        self,
        selector,
        url
        ):

        self.navigation_targets[
            selector
        ] = url


    def get_navigation_target(
        self,
        selector
        ):

        return self.navigation_targets.get(
            selector
        )


    #
    # URL MEMORY
    #

    def remember_url(self, url):

        self.visited_urls.add(url)

    def has_seen_url(self, url):

        return url in self.visited_urls

    #
    # PAGE ACTION MEMORY
    #

    def remember_page_action(
        self,
        url,
        selector
    ):

        if url not in self.page_actions:

            self.page_actions[url] = set()

        self.page_actions[url].add(selector)

    def has_seen_page_action(
        self,
        url,
        selector
    ):

        if url not in self.page_actions:
            return False

        return (
            selector
            in self.page_actions[url]
        )

    #
    # TRANSITIONS
    #

    def remember_transition(
        self,
        from_url,
        to_url,
        selector
    ):

        self.transitions.append({
            "from": from_url,
            "to": to_url,
            "action": selector,
        })

    #
    # PATH MEMORY
    #

    def remember_path(
        self,
        url,
        path
    ):

        self.paths[url] = path

    def get_path(self, url):

        return self.paths.get(url)