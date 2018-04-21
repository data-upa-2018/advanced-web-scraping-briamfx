import scrapy
import json


class TekohaSpider(scrapy.Spider):
	name = "tekoha"

	def start_requests(self):
		url = 'http://www.sas.gov.py/tmpl/grillas/ProgTekoha.php'
		for i in range(1065):
	            yield scrapy.FormRequest(url=url, method='POST', formdata={'page':str(i+1),'rows':'17'}, callback=self.parse)


	def parse(self, response):
		rows=json.loads(response.body)['rows']
		for row in rows:
			yield{
					'C.I. Titular':row['cell'][1],
					'Titular':row['cell'][2],
					'C.I. Conyugue':row['cell'][3],
					'Conyugue':row['cell'][4],
					'Departamento':row['cell'][5],
					'Distrito':row['cell'][6],
					'Territorio Social':row['cell'][7],
					'Manzana':row['cell'][8],
					'Lote':row['cell'][9]
					}
		

'''	def parse(self, response):
        	for quote in response.css('div.quote'):
            		yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('small.author::text').extract_first(),
                'tags': quote.css('div.tags a.tag::text').extract(),
            }
'''