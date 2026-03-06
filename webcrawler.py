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
from crawler_engine.frontier import Frontier
from crawler_engine.httpclient import HttpClient
from crawler_engine.link_extractor import LinkExtractor
from crawler_engine.link_sanitizer import LinkSanitizer
from crawler_engine.page import Page
from knowledge_graph.visualiser import KnowledgeGraph, visualize_graph


article_path = "//article"
article_link = "h3/a/@href"
all_links_xpath = "//table[contains(@class,'infobox')]//a[starts-with(@href,'/wiki/') and not(contains(@href,':'))]/@href"
# all_links_xpath = """
# //table[contains(@class,'infobox')]//a[starts-with(@href,'/wiki/') and not(contains(@href,':'))]
# |
# //*[@id='mw-content-text']//div[contains(@class,'mw-parser-output')]/p//a[starts-with(@href,'/wiki/') and not(contains(@href,':'))]
# """
all_summaries = "//p"
headers = {
    "User-Agent": "MyKnowledgeGraphBot/1.0 (prevsathesh3215@gmail.com)"
}

#CRAWLER CLASSES
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


  def generate_knowledge_graph(self):
    kg = KnowledgeGraph()
    kg.build_graph(self.each_page_data)

    visualize_graph(kg.graph)



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


  #BOOKS TO SCRAPE
  # url = "https://books.toscrape.com/"

  # #WIKIPEDIA: EARTH
  # url = "https://en.wikipedia.org/wiki/Earth"

  #WIKIPEDIA: JESUS
  # url  = "https://en.wikipedia.org/wiki/Jesus"

  #ATHEX GROUP STOCKS
  # url = "https://www.athexgroup.gr/en"

  #ARTIFICAL INTELLIGENCE
  # url = "https://en.wikipedia.org/wiki/Artificial_intelligence"

  # url = "https://en.wikipedia.org/wiki/Human_intelligence"

  # url = "https://en.wikipedia.org/wiki/Black_hole"

  # url = "https://en.wikipedia.org/wiki/Mary,_mother_of_Jesus"

  url = "https://en.wikipedia.org/wiki/Donoghue_v_Stevenson"

  domain = urlparse(url).netloc

  depth_control = 20

  crawler = CrawlerEngine(depth_control, url, all_links_xpath)
  crawler.start_crawl_bfs()
  crawler.store_data()

  crawler.generate_knowledge_graph()




