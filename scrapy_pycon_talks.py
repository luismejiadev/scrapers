import scrapy
import json


class TalksSpider(scrapy.Spider):
    name = "talks"

    def clean_text(self,text):
        return text.strip('\t\r\n ').replace('\n', '').replace('\u2013', '')

    def start_requests(self):
        urls = [
            'https://us.pycon.org/2018/schedule/talks/list/',
            #'https://us.pycon.org/2018/schedule/talks/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        filename = 'USPyconTalks2018.html'
        talks = response.selector.xpath('//h2')
        data = []
        for talk in talks:
            info = {
                'id': talk.xpath('a//@id').extract(),
                'title': self.clean_text(talk.xpath('a//text()').extract()[0]),
                'url': talk.root.base + talk.xpath('a//@href').extract()[0],
                'speaker': self.clean_text(talk.xpath('following-sibling::p[1]//b[1]//text()')[0].extract()),
                'schedule': self.clean_text(talk.xpath('following-sibling::p[1]//b[2]//text()')[0].extract()),
                'description': self.clean_text(talk.xpath('following-sibling::div//text()')[0].extract()),
            }
            data.append(info)

        with open(filename, 'w') as f:
            for line in data:
                f.write(json.dumps(line))
                f.write('\n')