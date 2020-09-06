# -*- coding: utf-8 -*-
import scrapy
from scrapy import Request
from scrapy.exceptions import IgnoreRequest

import json
from click import prompt
import math

from DuTracker.utils.log import log, handle_parse_exception
from DuTracker.items import ProductInfo
from DuTracker.utils.urls import get_serie_page_url as page_url
from DuTracker.utils.urls import get_headers as headers


class SerieSpider(scrapy.Spider):
	name = 'serie'
	allowed_domains = ['app.dewu.com']
	start_urls = [
		'https://app.dewu.com/api/v1/h5/commodity/fire/search/doCategoryDetail'
	]
	custom_settings = {
		'ITEM_PIPELINES': {
			'DuTracker.pipelines.SaveProductId': 300,
		}
	}

	serieIds = {}
	Ids = []
	auto = False

	def start_requests(self):
		log.info('获取系列列表')
		for url in self.start_urls:
			yield Request(url, method='POST', dont_filter=True,
										body='{"sign":"0efcd8daeaac723e588568e45424a7c3","catId":1}',
										callback=self.parse_serieList, headers=headers())

	@handle_parse_exception
	def parse_serieList(self, response):
		serieList = json.loads(response.body_as_unicode())['data']['list']
		# log.info(f'{serieList}')
		for data in serieList:
			for serie in data['seriesList']:
				unionId = serie['productSeriesId']
				name = serie['name']
				self.serieIds[unionId] = name
				log.success(f'系列：{name} 编号：{unionId}')
		if not self.auto:
			ids = prompt('输入需要爬取的系列编号', default='').strip().split(' ')
			if ids==['']: return IgnoreRequest()
		else:
			ids = self.Ids
			if not ids: return IgnoreRequest()

		log.info(f'获取 {ids} 系列包含商品')
		for unionId in ids:
			unionId = int(unionId)
			log.info(f'unionId: {unionId}')
			yield Request(page_url(unionId), callback=self.parse_serieInfo, meta={
				'unionId': unionId,
				'name': self.serieIds[unionId]
			}, headers=headers())

	@handle_parse_exception
	def parse_serieInfo(self, response):
		log.info(f'系列列表响应')
		data = json.loads(response.body_as_unicode())['data']
		unionId = response.meta.get('unionId')
		name = response.meta.get('name')

		num = data['total']
		page = math.ceil(num/20)
		log.success(f'系列：{name} 编号：{unionId} 商品总数：{num} 页面数：{page}')

		for page in range(1, page + 1):
			yield Request(page_url(unionId, page), callback=self.parse_productId, meta={
				'unionId': unionId,
				'name': self.serieIds[unionId]
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
