# -*- coding: utf-8 -*-

import scrapy
from scrapy import Request
from scrapy.exceptions import IgnoreRequest
import json
import math
from click import prompt

from DuTracker.utils.log import log, handle_parse_exception
from DuTracker.items import ProductInfo
from DuTracker.utils.urls import get_brand_page_url as page_url
from DuTracker.utils.urls import get_headers as headers


class BrandSpider(scrapy.Spider):
	name = 'brand'
	allowed_domains = ['app.dewu.com']
	start_urls = [
		'https://app.dewu.com/api/v1/h5/commodity/fire/search/doCategoryDetail'
	]
	custom_settings = {
		'ITEM_PIPELINES': {
			'DuTracker.pipelines.SaveProductId': 300,
		}
	}
	brandIds = {}
	Ids = []
	auto = False

	def start_requests(self):
		log.info('获取品牌列表')
		for url in self.start_urls:
			yield Request(url, dont_filter=True,
										method='POST',
										body='{"sign":"4ff93b98af1253fe192ff1328ed09081","catId":0}',
										callback=self.parse_brandList,
										meta={'dont_retry': True},
										headers=headers())

	@handle_parse_exception
	def parse_brandList(self, response):
		brandList = json.loads(response.body_as_unicode())['data']['list']
		for brand in brandList:
			unionId = brand['brand']['goodsBrandId']
			name = brand['brand']['brandName']
			self.brandIds[unionId] = name
			log.success(f'品牌：{name} 编号：{unionId}')

		if not self.auto:
			ids = prompt('输入需要爬取的品牌编号', default='').strip().split(' ')
			if ids==['']: return IgnoreRequest()
		else:
			ids = self.Ids
			if not ids: return IgnoreRequest()

		# log.info(f'品牌列表 {self.brandIds}')
		# log.info(f'获取 {ids} 品牌包含商品')
		for unionId in ids:
			log.info(f'unionId: {unionId}')
			unionId = int(unionId)
			yield Request(page_url(unionId), callback=self.parse_brandInfo, meta={
				'unionId': unionId,
				'name': self.brandIds[unionId]
			}, headers=headers())

	@handle_parse_exception
	def parse_brandInfo(self, response):
		data = json.loads(response.body_as_unicode())['data']
		unionId = response.meta.get('unionId')
		name = response.meta.get('name')

		num = data['total']
		page = math.ceil(num/20)
		log.success(f'品牌：{name} 编号：{unionId} 商品总数：{num} 页面数：{page}')

		for page in range(1, page + 1):
			yield Request(page_url(unionId, page), callback=self.parse_productId, meta={
				'unionId': unionId,
				'name': self.brandIds[unionId]
			}, headers=headers())

	@handle_parse_exception
	def parse_productId(self, response):
		productList = json.loads(response.body_as_unicode())['data']['productList']
		for product in productList:
			name = response.meta.get('name')
			pid = product['productId']
			title = product['title']
			yield ProductInfo(
				id=pid,
				title=title,
				name=name,
			)
