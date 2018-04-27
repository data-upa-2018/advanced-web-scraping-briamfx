from json import JSONDecodeError

import scrapy
import json
import requests


class TsjeSpider(scrapy.Spider):
    name = "tsje"

    def __init__(self, session_id=''):
        self.session_id = session_id
        departamentos_response = requests.get('https://resultados.tsje.gov.py/publicacion/statics/json/departamentos.json')
        departamentos = json.loads(departamentos_response.text.split('=')[1])["18"]
        self.geo = {}
        for i, d in enumerate(departamentos):
            self.geo[i] = {'Departamento': d}

        distritos_response = requests.get('https://resultados.tsje.gov.py/publicacion/statics/json/distritos.json')
        distritos = TsjeSpider.list_to_dict(json.loads(distritos_response.text.split("=")[1])["18"], 2)

        for k1, v1 in distritos.items():
            self.geo[k1]['Distritos'] = v1
            for k2, v2 in self.geo[k1]['Distritos'].items():
                self.geo[k1]['Distritos'][k2] = {'Distrito': v2}

        zonas_response = requests.get('https://resultados.tsje.gov.py/publicacion/statics/json/zonas.json')
        zonas = TsjeSpider.list_to_dict(json.loads(zonas_response.text.split("=")[1])["18"], 3)

        for k1, v1 in zonas.items():
            for k2, v2 in v1.items():
                self.geo[k1]['Distritos'][k2]['Zonas'] = v2
                for k3, v3 in self.geo[k1]['Distritos'][k2]['Zonas'].items():
                    self.geo[k1]['Distritos'][k2]['Zonas'][k3] = {'Zona': v3}

        locales_response = requests.get('https://resultados.tsje.gov.py/publicacion/statics/json/locales.json')
        locales = TsjeSpider.list_to_dict(json.loads(locales_response.text.split("=")[1])["18"], 4)

        for k1, v1 in locales.items():
            for k2, v2 in v1.items():
                for k3, v3 in v2.items():
                    self.geo[k1]['Distritos'][k2]['Zonas'][k3]['Locales'] = v3
                    for k4, v4 in self.geo[k1]['Distritos'][k2]['Zonas'][k3]['Locales'].items():
                        self.geo[k1]['Distritos'][k2]['Zonas'][k3]['Locales'][k4] = {'Local': v4}

        mesas_response = requests.get('https://resultados.tsje.gov.py/publicacion/statics/json/mesas.json')
        mesas = TsjeSpider.list_to_dict(json.loads(mesas_response.text.split("=")[1])["18"]["presidente"], 5)
        #

        for k1, v1 in mesas.items():
            for k2, v2 in v1.items():
                for k3, v3 in v2.items():
                    for k4, v4 in v3.items():
                        self.geo[int(k1)]['Distritos'][int(k2)]['Zonas'][int(k3)]['Locales'][int(k4)]['Mesas'] = int(v4[0])


    @staticmethod
    def list_to_dict(l, level, level_acc=0):

        if level_acc == level:
            return l

        acc = {}
        if isinstance(l, (list,)) and level_acc <= level:
            for i, elem in enumerate(l):
                acc[i] = TsjeSpider.list_to_dict(elem, level, level_acc+1)
        if isinstance(l, (dict,)) and level_acc <= level:
            for k, v in l.items():
                acc[int(k)] = TsjeSpider.list_to_dict(v, level, level_acc+1)
        if isinstance(l, (str,)) and level_acc <= level:
            acc[0] = l
        return acc

    def start_requests(self):
        for k1, departamento in self.geo.items():
            if not k1==1:
                continue
            for k2, distrito in departamento['Distritos'].items():
                for k3, zona in distrito['Zonas'].items():
                    for k4, local in zona['Locales'].items():
                        for mesa in range(local['Mesas']):
                            url = "https://resultados.tsje.gov.py/publicacion/dinamics/certificado.ajax.php?eleccion=18&candidatura=presidente&departamento={}&distrito={}&zona={}&local={}&mesa={}".format(k1, k2, k3, k4, mesa)

                            yield scrapy.Request(url=url, cookies={'PHPSESSID': self.session_id}, callback=self.parse)

    def parse(self, response):
        try:
            result = json.loads(response.body_as_unicode())
            cabecera = result['cabecera']
            detalles = result['detalle']
            for detalle in detalles:
                yield {**cabecera, **detalle}
        except JSONDecodeError:
            input("Captcha expired, please re-enter and press ENTER")
