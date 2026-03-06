import heapq

class Frontier:
    def __init__(self):
        self.queue = []
        self.visited = set()

    def add_url(self, url, score=0):
        if url not in self.visited:
            heapq.heappush(self.queue, (-score, url))
            self.visited.add(url)

    def get_next(self):
        if self.queue:
            return heapq.heappop(self.queue)[1]
        return None
