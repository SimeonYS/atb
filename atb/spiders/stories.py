import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import AtbItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'


class StoriesSpider(scrapy.Spider):
    name = 'stories'
    start_urls = ['https://www.atb.com/company/news/stories/archive/',
                  'https://www.atb.com/company/news/stories/']
    ITEM_PIPELINES = {
        'stories.pipelines.AtbPipeline': 300,

    }

    def parse(self, response):
        post_links = response.xpath('//h4/a/@href | //div[@class="p1"]/p/a/@href').getall()
        yield from response.follow_all(post_links, self.parse_post)

    def parse_post(self, response):
        try:
            date = response.xpath('//span[@class="border"]/following-sibling::text()').get().strip()
        except AttributeError:
            date = response.xpath('//div[@class="p1"]//em/text()').get()
            date = re.findall(r'\w+\s\d+\,\s\d+', date)

        title = response.xpath('//h1/text()').get()
        content = response.xpath('//div[@class="p1"]//text()').getall()
        content = [p.strip() for p in content if p.strip()]
        content = re.sub(pattern, "", ' '.join(content))

        item = ItemLoader(item=AtbItem(), response=response)
        item.default_output_processor = TakeFirst()

        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('date', date)

        yield item.load_item()
