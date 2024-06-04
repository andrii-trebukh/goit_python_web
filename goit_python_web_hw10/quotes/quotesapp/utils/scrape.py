from pathlib import Path
import scrapy
from scrapy.crawler import CrawlerProcess


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']
    path = Path(__file__).parent.joinpath("qoutes.json").absolute()
    custom_settings = {
        'FEEDS': {path: {'format': 'json', 'overwrite': True}, }
    }

    def parse(self, response):
        for quote in response.xpath('//div[@class="quote"]'):
            yield {
                "tags": quote.xpath('div/a[@class="tag"]/text()').getall(),
                "author": quote.xpath(
                    'span/small[@class="author"]/text()'
                ).get(),
                "quote": quote.xpath('span[@class="text"]/text()').get()
            }
        next_page = response.xpath('//li[@class="next"]/a/@href').get()
        if next_page is not None:
            yield scrapy.Request(self.start_urls[0] + next_page)


class AuthorsSpider(scrapy.Spider):
    name = 'authors'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']
    path = Path(__file__).parent.joinpath("authors.json").absolute()
    custom_settings = {
        'FEEDS': {path: {'format': 'json', 'overwrite': True}, }
    }

    def parse(self, response, authors=None):
        if response.xpath(
            '//h3[@class="author-title"]/text()'
        ).get() is not None:
            yield {
                "fullname": response.xpath(
                    '//h3[@class="author-title"]/text()'
                ).get().replace("-", " "),
                "born_date": response.xpath(
                    '//span[@class="author-born-date"]/text()'
                ).get(),
                "born_location": response.xpath(
                    '//span[@class="author-born-location"]/text()'
                ).get(),
                "description": response.xpath(
                    '//div[@class="author-description"]/text()'
                ).get().strip()
            }
        else:
            if authors is None:
                authors = {}
            for quote in response.xpath('//div[@class="quote"]'):
                author = quote.xpath(
                    'span/small[@class="author"]/text()'
                ).get()
                if authors.get(author) is None:
                    authors[author] = quote.xpath('span/a/@href').get()
            next_page = response.xpath('//li[@class="next"]/a/@href').get()
            if next_page is not None:
                yield scrapy.Request(
                    self.start_urls[0] + next_page,
                    cb_kwargs={"authors": authors}
                )
            elif authors:
                for path in authors.values():
                    yield scrapy.Request(self.start_urls[0] + path)


def run_spiders():
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.crawl(AuthorsSpider)
    process.start()
