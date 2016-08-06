# coding=utf8

import time
from urllib import request
from bs4 import BeautifulSoup
from config import *
from logger import logger


class ItemCurrent():
    def __init__(self, tds):
        if len(tds) < 10:
            raise Exception('column count is too low: {}'.format(len(tds)))

        self.code = tds[1].a['href'][-6:].strip()
        self.name = tds[1].a.string.strip()
        self.price = int(tds[2].string.replace(',', '').strip())
        self.change = int(tds[3].span.string.strip().replace(',', ''))
        self.changerate = float(tds[4].span.string.strip().replace('%', ''))
        self.par_value = int(tds[5].string.replace(',', '').strip())
        self.market_capital = int(tds[6].string.replace(',', '').strip())
        self.number_of_stocks = int(tds[7].string.replace(',', '').strip())
        self.foreign_rate = float(tds[8].string.replace(',', '').strip())
        self.volume = int(tds[9].string.replace(',', '').strip())
        try:
            self.per = float(tds[10].string.strip().replace(',', ''))
        except:
            self.per = None
            logger.error('per parse error:{}, {}'.format(self.code, self.name))
        try:
            self.roe = float(tds[11].string.strip().replace(',', ''))
        except:
            self.roe = None
            logger.error('roe parse error:{}, {}'.format(self.code, self.name))


class StockCurrentCollector():
    """
    네이버 시총 상위 종목 리스트 페이지를 조회하여 종목별 현재가 정보를 수집한다
    """

    url = 'http://finance.naver.com/sise/sise_market_sum.nhn?sosok={}&page={}'

    def do(self):
        """
        네이버에서 종목별 현재가 정보를 가져와 db 에 저장한다.
        """
        for item in self.get_items():
            logger.info(item.code)
            # save

    def get_items(self):
        """
        모든 아이템의 현재가 정보를 반환한다.

        return: generator of ItemCurrent
        """
        for page in self.get_pages():
            for item in self.get_items_from_page(page):
                yield item

    def get_pages(self):
        """
        네이버 현재가 페이지 조회해서 스트링으로 반환

        return: generator of str
        """
        for market in markets_for_current:
            for page in pages_for_current:
                try:
                    yield request.urlopen(
                        self.__class__.url.format(market, page)).read()

                    time.sleep(request_interval)
                except Exception as e:
                    logger.error('fail to read stock current')
                    raise e

    def get_items_from_page(self, page):
        """
        네이버에서 가져온 웹페이지로 부터 종목 정보를 추출/반환

        return: generator of ItemCurrent
        """
        bs = BeautifulSoup(page, 'lxml')

        for tr in bs.body.find('div', id='wrap').find('div', id='newarea').find(
            'div', id='contentarea').find('div', class_='box_type_l').find(
                'table', class_='type_2').tbody.find_all('tr'):
            try:
                yield ItemCurrent(tr.find_all('td'))
            except Exception as e:
                logger.error('get item basic from tr failed: {}'.format(e))


def test():
    collector = StockCurrentCollector()

    logger.info(str(collector.do()))


if __name__ == '__main__':
    test()
