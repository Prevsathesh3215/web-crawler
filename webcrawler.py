from lxml import html
import requests as req
import aiohttp
import asyncio
import time
from urllib.parse import urljoin, urlparse, urlunparse
from collections import deque
import time
import re
import networkx as nx
import json
from pyvis.network import Network
from IPython.display import IFrame
import unicodedata
import heapq
from sentence_transformers import SentenceTransformer
import numpy as np



#BOOKS TO SCRAPE
# url = "https://books.toscrape.com/"

#WIKIPEDIA: EARTH
# url = "https://en.wikipedia.org/wiki/Earth"

#WIKIPEDIA: JESUS
url  = "https://en.wikipedia.org/wiki/Jesus"

#ATHEX GROUP STOCKS
# url = "https://www.athexgroup.gr/en"

domain = urlparse(url).netloc

article_path = "//article"
article_link = "h3/a/@href"
# all_links_xpath = "//table[contains(@class,'infobox')]//a[starts-with(@href,'/wiki/') and not(contains(@href,':'))]/@href"
all_links_xpath = """
//table[contains(@class,'infobox')]//a[starts-with(@href,'/wiki/') and not(contains(@href,':'))]
|
//*[@id='mw-content-text']//div[contains(@class,'mw-parser-output')]/p//a[starts-with(@href,'/wiki/') and not(contains(@href,':'))]
"""
all_summaries = "//p"
headers = {
    "User-Agent": "MyKnowledgeGraphBot/1.0 (prevsathesh3215@gmail.com)"
}

#PYVIS
def visualize_graph(graph):
    net = Network(
        height="750px",
        width="100%",
        directed=True,
        notebook=True,
        cdn_resources="in_line"  
    )

    for node, data in graph.nodes(data=True):
        net.add_node(
            node,
            label=node,
            title=data.get("summary", ""),
            size=20
        )

    for source, target in graph.edges():
        net.add_edge(source, target)

    net.show("knowledge_graph.html")
    IFrame("knowledge_graph.html", width=900, height=600)



#KNOWLEDGE GRAPH CLASS
class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()


    @staticmethod
    def normalize_node(text):
      text = text.replace("_", " ")
      text = text.lower()
      text = unicodedata.normalize("NFKC", text)
      text = re.sub(r"\s+", " ", text)
      return text.strip()

    def build_graph(self, pages):
        for page in pages:
            title = self.normalize_node(page["title"])

            self.graph.add_node(title)

            for link in page["links"]:
                target = self.normalize_node(link.split("/wiki/")[-1])

                self.graph.add_edge(title, target)






#CRAWLER CLASSES
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



class HttpClient:
  def fetch(self, url):
    response = req.get(url, headers=headers, timeout=2)
    response.raise_for_status()
    return response.text


class LinkExtractor:

    @staticmethod
    def extract_links(html_content, xpath_rule):
        tree = html.fromstring(html_content)
        return tree.xpath(xpath_rule)

    @staticmethod
    def extract_summary(html_content):
        tree = html.fromstring(html_content)

        paragraphs = tree.xpath("//*[@id='mw-content-text']//div[contains(@class,'mw-parser-output')]/p[not(@class)][1]")

        raw_text = " ".join([p.text_content() for p in paragraphs])

        raw_text = re.sub(r"\[\d+\]", "", raw_text)
        raw_text = re.sub(r"\s+", " ", raw_text)

        # print(raw_text)
        # print("Summary extracted", raw_text)

        return " ".join(raw_text.split()[:200])

    @staticmethod
    def extract_title(html_content):
        tree = html.fromstring(html_content)

        title = tree.xpath("//h1[@id='firstHeading']//text()")

        return title[0].strip() if title else ""


class LinkSanitizer:
    def __init__(self, domain):
        self.domain = domain

    def sanitize(self, base_url, links):
        seen = set()
        result = []

        for link in links:
            if not link or link.startswith("#"):
                continue

            absolute = urljoin(base_url, link)
            parsed = urlparse(absolute)

            if parsed.netloc != self.domain:
                continue

            final_url = parsed._replace(fragment="").geturl()

            if "/category/" in final_url:
                continue

            if final_url not in seen:
                seen.add(final_url)
                result.append(final_url)

        return result

class Page:
    def __init__(self, url, client, extractor, sanitizer):
        if not url:
            raise ValueError("URL cannot be empty")

        self.url = url
        self.client = client
        self.extractor = extractor
        self.sanitizer = sanitizer

        self.child_links = []
        self.summary = ""
        self.title = ""


    def crawl(self, each_page_data):

        html_content = self.client.fetch(self.url)

        raw_links = LinkExtractor.extract_links(
            html_content,
            "//table[contains(@class,'infobox')]//a[starts-with(@href,'/wiki/') and not(contains(@href,':'))]/@href"
        )

        self.summary = LinkExtractor.extract_summary(html_content)
        self.title = LinkExtractor.extract_title(html_content)

        self.child_links = self.sanitizer.sanitize(self.url, raw_links)

        print("Title:", self.title)
        print("Summary:", self.summary[:100])

        each_page_data.append({
            "title": self.title,
            "url": self.url,
            "summary": self.summary,
            "links": self.child_links[:10] # CHANGE NUMBER OF LINK EDGES HERE
        })

        # print(each_page_data)

        # print("Title:", self.title)
        # print("Summary:", self.summary[:100])



class CrawlerEngine:
  def __init__(self, depth_control, url, xpath):
    self.depth_control = depth_control
    self.url = url
    self.xpath = xpath
    self.accessed_sites = []
    self.each_page_data = []

    self.frontier = Frontier()
    self.frontier.add_url(url)

    self.client = HttpClient()
    self.extractor = LinkExtractor()
    self.sanitizer = LinkSanitizer(domain)

    self.cluster_centroid = None
    self.cluster_vectors = []   

    self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
    self.embedding_cache = {}

  
  @staticmethod
  def simple_link_score(url, summary=""):
      name = url.split("/wiki/")[-1]

      score = len(name)

      # Bonus if summary contains link name
      if name.lower() in summary.lower():
          score += 50

      return score

  def embed(self, text):

      if text in self.embedding_cache:
          return self.embedding_cache[text]

      if not text:
          vector = np.zeros(384)
      else:
          vector = self.embedder.encode(text)

      self.embedding_cache[text] = vector
      return vector


  def store_data(self):
    with open("pages.json", "w") as f:
      json.dump(self.each_page_data, f, indent=2)

  def start_crawl_bfs(self):

      while self.frontier.queue and len(self.each_page_data) < self.depth_control:

          current_url = self.frontier.get_next()

          if not current_url:
              continue

          print("\nAccessing site:", current_url)

          page = Page(current_url, self.client, self.extractor, self.sanitizer)
          page.crawl(self.each_page_data)

          vector = self.embed(page.summary)
          self.cluster_vectors.append(vector)

          if len(self.cluster_vectors) > 0:
              self.cluster_centroid = np.mean(
                  self.cluster_vectors,
                  axis=0
              )


          for link in page.child_links:
            score = self.simple_link_score(link, page.summary)             
            self.frontier.add_url(link, score)

          time.sleep(2)
      print(self.each_page_data)



  def start_crawl_number(self):
    for i in range(self.depth_control):
      current_url = self.frontier.get_next()
      print("\nAccessing site: ", current_url)
      self.accessed_sites.append(current_url)

      if not current_url:
        break

      page = Page(current_url, self.client, self.extractor, self.sanitizer)
      page.crawl(self.each_page_data)

      for link in page.child_links:
        self.frontier.add_url(link)
        # print(frontier)


      # print("\nGathered sites: ", len(self.frontier.visited))
      # print("\nAccessed sites: ", len(self.accessed_sites))
      # print("\nEach page data: ", self.each_page_data)

      for site in self.frontier.visited:
        print(site)

      time.sleep(3)




if __name__ == "__main__":
  depth_control = 80

  crawler = CrawlerEngine(depth_control, url, all_links_xpath)
  crawler.start_crawl_bfs()
  crawler.store_data()

  kg = KnowledgeGraph()
  kg.build_graph(crawler.each_page_data)

  visualize_graph(kg.graph)




