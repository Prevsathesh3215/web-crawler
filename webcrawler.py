from lxml import html
import requests as req
import aiohttp
import asyncio
import time
from urllib.parse import urljoin, urlparse, urlunparse
from collections import deque
import time
import re

#BOOKS TO SCRAPE
# url = "https://books.toscrape.com/"

#WIKIPEDIA: EARTH
url = "https://en.wikipedia.org/wiki/Earth"

domain = urlparse(url).netloc
depth_control = 8

article_path = "//article"
article_link = "h3/a/@href"
all_links = "//table[contains(@class,'infobox')]//a[starts-with(@href,'/wiki/') and not(contains(@href,':'))]/@href"
all_summaries = "//p"
headers = {
    "User-Agent": "MyKnowledgeGraphBot/1.0 (prevsathesh3215@gmail.com)"
}

class Frontier:
  def __init__(self):
    self.queue = deque()
    self.visited = set()

  def add_url(self, url):
    if url not in self.visited:
      self.queue.append(url)
      self.visited.add(url)

  def get_next(self):
    if self.queue:
      return self.queue.popleft()
    else:
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

        paragraphs = tree.xpath("//div[@class='mw-parser-output']/p[not(@class)]")

        raw_text = " ".join([p.text_content() for p in paragraphs])

        raw_text = re.sub(r"\[\d+\]", "", raw_text)
        raw_text = re.sub(r"\s+", " ", raw_text)

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

        each_page_data.append({
            "title": self.title,
            "url": self.url,
            "summary": self.summary,
            "links": self.child_links
        })

        print("Title:", self.title)
        print("Summary:", self.summary[:100])



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


  def start_crawl(self):
    for i in range(self.depth_control):
      time.sleep(7)

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


      print("\nGathered sites: ", len(self.frontier.visited))
      # print("\nAccessed sites: ", len(self.accessed_sites))
      print("\nEach page data: ", self.each_page_data)

      for i in self.frontier.visited:
        print(i)



if __name__ == "__main__":
  crawler = CrawlerEngine(depth_control, url, all_links)
  crawler.start_crawl()
