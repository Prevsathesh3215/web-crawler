import requests as req


class HttpClient:
  def __init__(self, headers=None):
    self.headers = headers or {
        "User-Agent": "MyKnowledgeGraphBot/1.0 (prevsathesh3215@gmail.com)"}

  def fetch(self, url, headers=None):
    session = req.Session()
    session.headers.update(self.headers)

    response = session.get(url, timeout=10)
    return response.text


    
