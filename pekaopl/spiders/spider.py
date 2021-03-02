import scrapy

from scrapy.loader import ItemLoader
from ..items import PekaoplItem
from itemloaders.processors import TakeFirst


class PekaoplSpider(scrapy.Spider):
	name = 'pekaopl'
	start_urls = ['https://www.pekao.com.pl/o-banku/aktualnosci.html']

	def parse(self, response):
		post_links = response.xpath('//li[@class="item-with-date item-with-date-featured"]')
		for post in post_links:
			url = post.xpath('.//div[@class="links-container"]/a/@href').get()
			date = post.xpath('.//div[@class="small-12 columns"]/p/text()').get()
			title = post.xpath('.//h2[@class="item-with-date-header"]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={'date': date, 'title': title})

		years_links = response.xpath('//ul[@class="swiper-wrapper"]/li//a/@href').getall()
		yield from response.follow_all(years_links, self.parse)

	def parse_post(self, response, date, title):
		description = response.xpath('//div[@class="columns small-12 medium-8 large-7 end text-left item-with-date-content"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=PekaoplItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
