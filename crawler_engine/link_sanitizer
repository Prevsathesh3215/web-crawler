import time
from urllib.parse import urljoin, urlparse

class LinkSanitizer:
    def __init__(self, domain):
        self.domain = domain
        print(self.domain)

    def sanitize(self, base_url, links):
      seen = set()
      result = []

      for link in links:

          # Extract href safely
          if hasattr(link, "get"):
              href = link.get("href")
          else:
              href = str(link)

          if not href:
              continue

          if href.startswith("#"):
              continue

          href = str(href)

          absolute = urljoin(str(base_url), href)
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
