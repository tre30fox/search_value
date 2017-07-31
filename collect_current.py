# coding=utf8

import time
from urllib import request
from bs4 import BeautifulSoup
import config as conf
from logger import logger


class ExceptionNoCode(Exception):
    pass


class ExceptionParseError(Exception):
    pass


class ItemCurrent:
    def __init__(self, tds):
        if len(tds) < 2:
            raise ExceptionNoCode('no code: {}'.format(len(tds)))

        self.code = tds[1].a['href'][-6:].strip()

        if len(tds) < 10:
            raise ExceptionParseError(
                'column count is too low: code:{}, error: {}'.format(self.code, len(tds)))

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


class NaverItemCurrentPage:
    """
    네이버에서 가져온 시가총액 페이지로부터 종목 정보를 추출/반환
    """
    def __init__(self, page):
        """
        :param page: 읽어온 웹페이지. bs4 read stream
        """
        self.bs = BeautifulSoup(page, 'lxml')

    def iteritems(self):
        """
        웹페이지에서 한 row 마다 한 종목씩의 정보를 파싱에서 반환한다.
        :return: generator of ItemCurrent
        """
        for tr in self.bs.body.find('div', id='wrap').find('div', id='newarea').find(
            'div', id='contentarea').find('div', class_='box_type_l').find(
                'table', class_='type_2').tbody.find_all('tr'):
            try:
                yield ItemCurrent(tr.find_all('td'))
            except ExceptionNoCode:
                continue
            except ExceptionParseError as e:
                logger.error('get item basic from tr failed: Parse Error: {}'.format(e))
            except Exception as e:
                logger.error('get item basic from tr failed: Unknown: {}'.format(e))


class StockCurrentCollector:
    """
    네이버 시총 상위 종목 리스트 페이지를 조회하여 종목별 현재가 정보를 수집한다
    """

    url = 'http://finance.naver.com/sise/sise_market_sum.nhn?sosok={}&page={}'

    def do(self):
        """
        네이버에서 종목별 현재가 정보를 가져와 db 에 저장한다.
        """
        for item in self.get_items():
            logger.info(', '.join(map(str, (item.code, item.name, item.price, item.per, item.roe))))
            # save

    def get_items(self):
        """
        모든 아이템의 현재가 정보를 반환한다.

        return: generator of ItemCurrent
        """
        for page in self.get_pages():
            for item in page.iteritems():
                yield item

    def get_pages(self):
        """
        네이버 현재가 페이지 조회해서 스트링으로 반환

        return: generator of str
        """
        for market in range(*conf.markets_for_current):
            for page in range(*conf.pages_for_current):
                try:
                    yield NaverItemCurrentPage(request.urlopen(
                        self.__class__.url.format(market, page)).read())

                    time.sleep(conf.request_interval)
                except Exception as e:
                    logger.error('fail to read stock current')
                    raise e


def test():
    collector = StockCurrentCollector()
    collector.do()

    # logger.info(str(collector.do()))


if __name__ == '__main__':
    test()
