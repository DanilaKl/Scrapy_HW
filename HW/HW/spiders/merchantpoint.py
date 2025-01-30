from typing import Iterable, Any

from scrapy.http.request import Request
from scrapy.http.response import Response
from scrapy.spiders.sitemap import SitemapSpider

from ..items import MerchantItem


class MerchantpointSpider(SitemapSpider):
    name = "merchantpoint"
    allowed_domains = ["merchantpoint.ru"]
    sitemap_urls = ['https://merchantpoint.ru/sitemap/brands.xml']

    def sitemap_filter(
        self, entries: Iterable[dict[str, Any]]
    ) -> Iterable[dict[str, Any]]:
        for entry in entries:
            entry['loc'] = entry['loc'].replace('mcc/', '')
            yield entry

    def parse(self, response: Response):
        org_name = response.xpath('//h1/text()').get()
        if not org_name:
            return

        org_description = response.xpath(
            '//div[contains(@class, "form-group")]//p[not(@*)]/text()'
        ).get()
        if not org_description:
            return

        terminals_hrefs = response.xpath(
            '//div[@id="terminals"]//tbody/tr/td[2]/a/@href'
        ).getall()
        if terminals_hrefs:
            organiztion_info = {
                'org_name': org_name, 'org_description': org_description
            }
        for terminal_href in terminals_hrefs:
            yield Request(url=response.urljoin(terminal_href),
                          cb_kwargs=organiztion_info,
                          callback=self.parse_merchant)

    def parse_merchant(self,
                       response: Response,
                       org_name='',
                       org_description=''):
        merchant_name = response.xpath(
            '//b[text()="MerchantName"]/parent::p/text()'
        ).get()
        if not merchant_name:
            return
        merchant_name = merchant_name.replace('\u2014', '').lstrip()

        mcc = response.xpath(
            '//b[contains(text(), "MCC")]/following-sibling::a/text()'
        ).get()
        if not mcc:
            return

        address = response.xpath(
            '//b[contains(text(), "Адрес")]/parent::p/text()'
        ).get()
        if address:
            address = address.replace('\u2014', '').lstrip()

        geo_coordinates = response.xpath(
            '//b[contains(text(), "Геокоординаты")]/parent::p/text()'
        ).get()
        if geo_coordinates:
            geo_coordinates = tuple(float(x) for x in geo_coordinates.split(', '))

        merchant = MerchantItem(
            merchant_name=merchant_name,
            mcc=mcc,
            address=address,
            geo_coordinates=geo_coordinates,
            org_name=org_name,
            org_description=org_description,
            source_url=response.url
        )

        yield merchant
