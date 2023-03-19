""" Spider that combs a list of stories on AO3. """
import re

import scrapy
from urllib.parse import urlparse

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from ao3scrape import settings
from ao3scrape.items import WorkItem


def view_complete(value):
    """ Append necessary request values onto the url. """
    return "{}?view_adult=true&view_full_work=true".format(value)


class WorkListSpider(CrawlSpider):
    """
    For parsing tag list pages on AO3 and scraping the data of individual works.
    """
    name = "ao3"
    allowed_domains = ["archiveofourown.org"]

    start_urls = settings.WORK_LIST_URLS

    rules = [
        Rule(LinkExtractor(allow=(r'works/[0-9]+\?view_adult=true&view_full_work=true'), process_value=view_complete), callback='parse_item')
    ]

    def parse_start_url(self, response):
        """Find the next page we reach the end."""
        next_page = response.xpath('//a[@rel="next"]/@href').get()
        if next_page is not None:
            yield scrapy.Request(response.urljoin(next_page))

    def strip_and_join(self, list_text, separator=" "):
        """ Strips out HTML tags and joins all the paragraphs into a single string. """
        text = separator.join(list_text).strip()
        stripped_text = re.sub("<.*?>", "", text)
        return stripped_text

    def parse_tags(self, response, item, tag_category):
        """ Parse the category's tags and save them to the item."""
        xpath = '//dd[@class="{} tags"]/ul/li/a/text()'.format(tag_category)
        item[tag_category] = response.xpath(xpath).getall()

    def parse_item(self, response):
        """ On the individual story pages, parse the page and save relevant data. """
        item = WorkItem()
        parsed_url = urlparse(response.url)
        # Pull the work id from the url.
        item['work_id'] = re.search('/works/(\d+)$', parsed_url.path).group(1)
        item['title'] = response.xpath('//h2/text()').get().strip()
        item['author'] = response.xpath('//h3[@class="byline heading"]/a[@rel="author"]/text()').getall()
        item['published'] = response.xpath('//dd[@class="published"]/text()').get().strip()
        item['summary'] = ''.join(response.xpath('//div[@class="preface group"]/div[@class="summary module"]/blockquote/*').getall()).strip()
        item['notes'] = ''.join(response.xpath('//div[@class="preface group"]/div[@class="notes module"]/blockquote/*').getall()).strip()
        # handle tags
        for category in ["rating", "warning", "category", "fandom", "relationship", "character", "freeform"]:
            self.parse_tags(response, item, category)

        item['language'] = response.xpath('//dd[@class="language"]/text()').get().strip()
        if response.xpath('//span[@class="position"]/a/text()'):
            item['series'] = response.xpath('//dd[@class="series"]/span[@class="series"]/span[@class="position"]/a/text()').getall()
            # The position shows up in the form of 'Part X of' within the position span.
            # Hugo can only handle a single value for weight, so unfortunately  ¯\_(ツ)_/¯ we take the first one.
            position_text = response.xpath('//span[@class="position"]/text()').get()
            item['series_position'] = re.search('Part (\d+) of', position_text).group(1)

        if response.xpath('//div[@class="chapter"]'):
            # handle multi-chapter story
            # Stores the data as a list instead of a single string.
            item['multi_chapter_text'] = response.xpath('//div[@id="chapters"]/*').getall()
        else:
            # single-chapter story
            item['single_chapter_text'] = "".join(response.xpath('//div[@id="chapters"]/div[@class="userstuff"]/*').getall()).strip()

        return item
