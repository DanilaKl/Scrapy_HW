from typing import Callable, Iterable, Any
from collections.abc import Mapping

import extruct

from scrapy.http.response import Response
from scrapy.spiders.sitemap import SitemapSpider

from ..items import BookItem


class ChitaiGorodSpider(SitemapSpider):
    name = "chitai_gorod"
    allowed_domains = ["chitai-gorod.ru"]
    sitemap_urls = ["https://www.chitai-gorod.ru/sitemap.xml"]
    # sitemap_rules = [
    #     ('product/', 'parse')
    # ]
    # sitemap_follow = ['/products']

    custom_settings = {
        "CLOSESPIDER_ITEMCOUNT": 100,
        "MONGO_URI": "mongodb://admin:admin@localhost:27017",
        "MONGO_DATABASE": "admin",
        "ITEM_PIPELINES": {
            'HW.pipelines.MongoPipeline': 301,
        }
    }

    def sitemap_filter(self, entries: Iterable[dict[str, Any]]) -> Iterable[dict[str, Any]]:
        for entry in entries:
            if "product" in entry["loc"]:
                yield entry

    def parse(self, response: Response):
        schemas = extruct.extract(response.text, syntaxes=['microdata'])
        book_schema = schemas['microdata'][6]['properties']

        title = book_schema['name'][-1]
        author = self.parse_author(book_schema)
        description = book_schema.get('description')
        price_amount = self.extract_element(
            book_schema,
            ('offers', 'properties', 'price'),
            int
        )
        price_currency = self.extract_element(
            book_schema,
            ('offers', 'properties', 'priceCurrency')
        )
        rating_value = self.extract_element(
            book_schema,
            ('aggregateRating', 'properties', 'ratingValue'),
            float
        )
        rating_count = self.extract_element(
            book_schema,
            ('aggregateRating', 'properties', 'reviewCount'),
            int
        )
        publication_year = self.extract_element(
            book_schema,
            ('datePublished',),
            int
        )
        isbn = book_schema.get('isbn')
        pages_cnt = self.extract_element(book_schema, ('numberOfPages',), int)
        publisher = response.xpath('//*[@itemprop="publisher"]/@content').get()
        book_cover = response.xpath('//picture//img/@src').get()
        source_url = response.url

        book_item = BookItem(title=title,
                             author=author,
                             description=description,
                             price_amount=price_amount,
                             price_currency=price_currency,
                             rating_value=rating_value,
                             rating_count=rating_count,
                             publication_year=publication_year,
                             isbn=isbn,
                             pages_cnt=pages_cnt,
                             publisher=publisher,
                             book_cover=book_cover,
                             source_url=source_url)

        yield book_item

    def extract_element(self, schema: dict,
                        path_to_element: Iterable[str],
                        converter: Callable[[str], Any] | None = None):
        content = schema
        for key in path_to_element:
            content = content.get(key)
            if content is None:
                return None

        if converter is not None:
            return converter(content)

        return content

    def parse_author(self, schema_content: dict):
        authors_field = schema_content.get('author')
        if authors_field is None:
            return None

        if isinstance(authors_field, Mapping):
            return authors_field['properties']['name']

        return ', '.join(
            author['properties']['name'] for author in authors_field
        )
