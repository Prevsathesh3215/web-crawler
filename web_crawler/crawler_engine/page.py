# from crawler_engine.frontier import Frontier
# from crawler_engine.httpclient import HttpClient
# from crawler_engine.link_extractor import LinkExtractor
# from crawler_engine.link_sanitizer import LinkSanitizer

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

        #DEFAULT XPATH
        # raw_links = LinkExtractor.extract_links(
        #     html_content,
        #     "//table[contains(@class,'infobox')]//a[starts-with(@href,'/wiki/') and not(contains(@href,':'))]/@href"
        # )


        raw_links = self.extractor.extract_links(
            html_content,
            """
            //div[contains(@class,'mw-parser-output')]
            //p//a[starts-with(@href,'/wiki/')
            and not(contains(@href,':'))]
            """
        )

        #ALT 1
        # raw_links = LinkExtractor.extract_links(
        #     html_content,
        #     """
        #     //table[contains(@class,'infobox')]//a[
        #         starts-with(@href,'/wiki/')
        #         and not(contains(@href,':'))
        #     ]/@href
        #     |
        #     //div[@class='mw-parser-output']//p//a[
        #         starts-with(@href,'/wiki/')
        #         and not(contains(@href,':'))
        #     ]/@href
        #     |
        #     //div[@class='mw-parser-output']//li//a[
        #         starts-with(@href,'/wiki/')
        #         and not(contains(@href,':'))
        #     ]/@href
        #     """
        # )


        #ALT 2
        # raw_links = LinkExtractor.extract_links(
        #     html_content,
        #     """
        #     //table[contains(@class,'infobox')]//a[starts-with(@href,'/wiki/') and not(contains(@href,':'))]
        #     |
        # //*[@id='mw-content-text']//div[contains(@class,'mw-parser-output')]/p//a[starts-with(@href,'/wiki/') and not(contains(@href,':'))]
        #     """
        # )

        self.summary = self.extractor.extract_summary(html_content)
        self.title = self.extractor.extract_title(html_content)

        self.child_links = self.sanitizer.sanitize(self.url, raw_links)

        print("Title:", self.title)
        print("Summary:", self.summary[:100])
        print("Extracted links count:", len(self.child_links))

        each_page_data.append({
            "title": self.title,
            "url": self.url,
            "summary": self.summary,
            "links": self.child_links[:10] # CHANGE NUMBER OF LINK EDGES HERE
        })

        # print(each_page_data)

        # print("Title:", self.title)
        # print("Summary:", self.summary[:100])
