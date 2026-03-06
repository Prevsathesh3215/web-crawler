import requests as req


class HttpClient:
  def fetch(self, url):
    response = req.get(url, headers=headers, timeout=5)
    response.raise_for_status()
    return response.text
