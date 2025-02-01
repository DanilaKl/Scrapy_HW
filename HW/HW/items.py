# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MerchantItem(scrapy.Item):
    merchant_name = scrapy.Field()
    mcc = scrapy.Field()
    address = scrapy.Field()
    geo_coordinates = scrapy.Field()
    org_name = scrapy.Field()
    org_description = scrapy.Field()
    source_url = scrapy.Field()


class BookItem(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    description = scrapy.Field()
    price_amount = scrapy.Field()
    price_currency = scrapy.Field()
    rating_value = scrapy.Field()
    rating_count = scrapy.Field()
    publication_year = scrapy.Field()
    isbn = scrapy.Field()
    pages_cnt = scrapy.Field()
    publisher = scrapy.Field()
    book_cover = scrapy.Field()
    source_url = scrapy.Field()
