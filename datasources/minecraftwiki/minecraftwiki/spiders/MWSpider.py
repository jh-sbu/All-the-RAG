import scrapy
import random
from scrapy.http.request import Request
from scrapy.http.response import Response
from scrapy.spiders.sitemap import SitemapSpider
from typing import Any, Iterable


class MWSpider(SitemapSpider):
    name = "mw_wiki_index_spider"
    allowed_urls = ["minecraft.wiki"]
    sitemap_urls = ["https://minecraft.wiki/robots.txt"]

    def __init__(self, *a: Any, **kw: Any):
        super().__init__(*a, **kw)
        self.max_urls = 1

    def start_requests(self) -> Iterable[Request]:
        requests = list(super(MWSpider, self).start_requests())

        return [requests[0]]

    def sitemap_filter(
        self, entries: Iterable[dict[str, Any]]
    ) -> Iterable[dict[str, Any]]:
        entries = list(entries)

        random.shuffle(entries)

        for entry in entries[0 : self.max_urls]:
            yield entry

    def parse(self, response: Response):
        print(response.status)
        title = response.css("title::text").get()

        print(f"Title: {title}")

        yield {"body": response.body}
