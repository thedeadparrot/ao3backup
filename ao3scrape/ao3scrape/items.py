# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WorkItem(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    summary = scrapy.Field()
    notes = scrapy.Field()
    single_chapter_text = scrapy.Field()
    multi_chapter_text = scrapy.Field()
    language = scrapy.Field()
    rating = scrapy.Field()
    warning = scrapy.Field()
    category = scrapy.Field()
    fandom = scrapy.Field()
    relationship = scrapy.Field()
    character = scrapy.Field()
    freeform = scrapy.Field()
    published = scrapy.Field()
    work_id = scrapy.Field()
    series = scrapy.Field()
    series_position = scrapy.Field()
