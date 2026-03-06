# web-crawler


A web-crawler project that I developed when trying to learn more about XPath, which lead to crawlers and data analysis. Made with python.

## Features

- Recursive crawling with depth control
- Automatic URL normalization
- Link extraction
- Summary extraction
- Async-ready architecture

## Installation

```bash
pip install web-crawler-engine
```

### HOW TO USE
```
from web_crawler import CrawlerEngine

url = "https://en.wikipedia.org/wiki/Artificial_intelligence"

crawler = CrawlerEngine(
    depth_control=30, #controls how many pages you want to view
    url=url
)

crawler.start_crawl_bfs() #starts crawls
crawler.store_data()  #stores data in a pages.json 
crawler.generate_knowledge_graph() #generates a html of a directed graph of pages and their relations
```

### JSON example
```
  {
    "title": "Black hole",
    "url": "https://en.wikipedia.org/wiki/Black_hole",
    "summary": "A black hole is an astronomical body so compact that its gravity prevents anything, including light, from escaping. Albert Einstein's theory of general relativity, which describes gravitation as the curvature of spacetime, predicts that any sufficiently compact mass will form a black hole. The boundary of no escape is called the event horizon. In general relativity, crossing a black hole's event horizon seals an object's fate but produces no locally detectable change. General relativity also predicts that every black hole should have a central singularity, where the curvature of spacetime is infinite.",
    "links": [
      "https://en.wikipedia.org/wiki/Astronomical_body",
      "https://en.wikipedia.org/wiki/Albert_Einstein",
      "https://en.wikipedia.org/wiki/General_relativity",
      "https://en.wikipedia.org/wiki/Curved_spacetime",
      "https://en.wikipedia.org/wiki/Mass",
      "https://en.wikipedia.org/wiki/Boundary_(topology)",
      "https://en.wikipedia.org/wiki/Event_horizon",
      "https://en.wikipedia.org/wiki/Gravitational_singularity",
      "https://en.wikipedia.org/wiki/Curvature_of_spacetime",
      "https://en.wikipedia.org/wiki/Gravitational_field"
    ]
  },
```