import scrapy
from bs4 import BeautifulSoup



class CotizacionesSpider(scrapy.Spider):
    name = "cotizaciones"
    def start_requests(self):
        url='https://www.bcp.gov.py/webapps/web/cotizacion/monedas-mensual'

        for anho in range(2001,2019):
            for mes in range(1,13):
                yield scrapy.FormRequest(url=url,
                                     method='POST',
                                     formdata={'anho':str(anho),'mes':str(mes)}, callback=self.parse,
                                         meta={'anho':anho, 'mes':mes})

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        count = 0
        result={'Anho':response.meta['anho'],'Mes':response.meta['mes']}
        if soup.table:
            rows=soup.table.findAll('td')
            for row in rows:
                count=count+1
                if count==2:
                    result['moneda']=row.string
                if count==3:
                    result['ME/USD']=row.string
                if count==2:
                    result['G/ME']=row.string
                    yield result

