# coding=utf8

from __future__ import unicode_literals

import urllib2
import time
import html5lib
from bs4 import BeautifulSoup


class ItemInfo(object):
    """종목의 각종 데이터 : 가격, 가치 정보 등"""
    def __init__(self):
        self.value = False, -100.0  # 가치 기본 값. (대상여부, 가치 수치)


class SettleInfo(object):
    """종목의 결산 기간 별 가치 데이터 : 2014년 3월의 - EPS, PER, 배당금 etc"""
    pass


def get_item_list_pages():
    list_pages = []
    url = 'http://finance.naver.com/sise/sise_market_sum.nhn?sosok=%d&page=%d'
    for market in xrange(0, 2):  # for test (0, 2)
        for page in xrange(1, 30):  # for test (1,30)
            try:
                list_pages.append(urllib2.urlopen(url % (market, page)).read())
                time.sleep(0.5)
            except Exception as e:
                print '[ERROR] GetItemListPages : market({}), page({})'.format(market, page)
                raise e
    return list_pages


def get_items_in_page(page):
    bs = BeautifulSoup(page, 'html5lib')
    trs = bs.body.find('div', id='wrap').find('div', id='newarea').find('div', id='contentarea').find(
        'div', class_='box_type_l').find('table', class_='type_2').tbody.find_all('tr')
    return map(get_item_from_tr, trs)


def get_item_basics_in_page(page):
    bs = BeautifulSoup(page, 'html5lib')
    trs = bs.body.find('div', id='wrap').find('div', id='newarea').find('div', id='contentarea').find(
        'div', class_='box_type_l').find('table', class_='type_2').tbody.find_all('tr')
    datas = [('P', tr) for tr in trs]
    return map(get_item_from_tr, trs)


def get_item_basic_from_tr(tr):
    try:
        col_count_min = 10
        tds = tr.find_all('td')
        if len(tds) < col_count_min:
            raise Exception('column count is below %d : %d' % (col_count_min, len(tds)))
        item = ItemInfo()
        item.code = tds[1].a['href'][-6:].strip()
        item.name = tds[1].a.string.strip()
        # item.price = int(tds[2].string.replace(',', '').strip())
        # item.change = int(tds[3].span.string.strip().replace(',', ''))
        # item.changerate = float(tds[4].span.string.strip().replace('%', ''))
        item.par_value = int(tds[5].string.replace(',', '').strip())
        # item.market_capital = int(tds[6].string.replace(',', '').strip())
        item.number_of_stocks = int(tds[7].string.replace(',', '').strip())
        # item.foreign_rate = float(tds[8].string.replace(',', '').strip())
        # item.volume = int(tds[9].string.replace(',', '').strip())
#         try:
#             item.per = float(tds[10].string.strip().replace(',', ''))
#         except:
#             item.per = None
#             #print item.name, item.code, 'per parse error'
#         try:
#             item.roe = float(tds[11].string.strip().replace(',', ''))
#         except:
#             item.roe = None
#             #print item.name, item.code, 'roe parse error'

        return item
    except Exception as e:
        print 'ERROR: get item basic from tr failed:', e
        return None


def get_item_from_tr(tr):
    try:
        col_count_min = 10
        tds = tr.find_all('td')
        if len(tds) < col_count_min:
            raise Exception('column count is below %d : %d' % (col_count_min, len(tds)))
        item = ItemInfo()
        item.code = tds[1].a['href'][-6:].strip()
        name = tds[1].a.string.strip()
        print type(name), name
        item.name = tds[1].a.string.strip()  # .encode('utf8')
        try:
            item.price = int(tds[2].string.replace(',', '').strip())
            item.change = int(tds[3].span.string.strip().replace(',', ''))
            item.changerate = float(tds[4].span.string.strip().replace('%', ''))
            item.par_value = int(tds[5].string.replace(',', '').strip())
            item.market_capital = int(tds[6].string.replace(',', '').strip())
            item.stock_count = int(tds[7].string.replace(',', '').strip())
            item.foreign_rate = float(tds[8].string.replace(',', '').strip())
            item.volume = int(tds[9].string.replace(',', '').strip())
            try:
                item.per = float(tds[10].string.strip().replace(',', ''))
            except Exception as e:
                item.per = None
                print 'ERROR: get item basic per failed:', e, ':', item.code, item.name
            try:
                item.roe = float(tds[11].string.strip().replace(',', ''))
            except Exception as e:
                item.roe = None
                print 'ERROR: get item basic roe failed:', e, ':', item.code, item.name

            return item
        except Exception as e:
            print 'ERROR: get item basic failed:', e, ':', item.code, item.name
    except Exception as e:
        print 'ERROR: get item basic failed:', e

    return None


def get_item_basics():
    items = []
    for page in get_item_list_pages():
        items.extend(get_items_in_page(page))
    items = filter(None, items)
    return items


def get_item_analysis():
    items = get_item_basics()
    for item in items:
        get_itooza_item_info(item)
        print 'itooza analysis completed : {}, {}'.format(item.name, item.code)

    return items


def get_itooza_item_info(item):
    bs = BeautifulSoup(
        urllib2.urlopen(
            'http://search.itooza.com/index.htm?seName=%s&x=17&y=13' % item.code).read(), 'html5lib')
    table_name_list = ['indexTable1', 'indexTable2', 'indexTable3']
    index_table = bs.body.find('div', id='wrap').find('div', id='container').find('div', id='indexTable')
    if index_table:
        try:
            item.settle_month = int(filter(lambda x: x.isdigit(), bs.body.find(
                'div', id='wrap').find('div', id='container').find('div', id='content').find(
                'div', id='stockItem').find('div', {'class': 'item-body'}).find('div', {'class': 'ar'}).find(
                'div', {'class': 'item-detail'}).find('div', {'class': 'detail-data'}).ul.find(
                'li', {'class': 'i-12'}).span.string.strip()))
        except Exception as e:
            item.settle_month = None
            print 'ERROR: get settle month failed:', e, ':', item.code, item.name
        item.settle_info = []  # 결산기별 데이터, 0 - 연환산, 1 - 연간, 2 - 분기별
        for each_table in table_name_list:
            table = index_table.find('div', id=each_table).table
            get_itooza_item_table(item.settle_info, table)


def get_itooza_item_table(target_table, bs_table):
    try:
        settle_info_list = []  # 결산기별 데이터 : 항목당 하나의 결산기
        # 년/월 데이터
        for each in bs_table.tr.find_all('th')[1:]:
            settle_info = SettleInfo()
            try:
                period = each.string.strip().split('.')
                settle_info.settle_period = (int(period[0]), int(period[1][:2]))
            except Exception as e:
                settle_info.settle_period = None
                print 'ERROR: get year/month failed:', e

            settle_info_list.append(settle_info)

        # 나머지 가치 데이터
        datas = bs_table.tbody.find_all('tr')
        td_index = 0

        # eps, 연결지배
        for index, each in enumerate(datas[td_index].find_all('td')):
            try:
                settle_info_list[index].eps_cont = int(each.string.strip().replace(',', ''))
            except Exception as e:
                settle_info_list[index].eps_cont = None
                print 'ERROR: get eps failed:', e
        td_index += 1

        # eps, 개별
        for index, each in enumerate(datas[td_index].find_all('td')):
            try:
                settle_info_list[index].eps_isol = int(each.string.strip().replace(',', ''))
            except Exception as e:
                settle_info_list[index].eps_isol = None
                print 'ERROR: get eps failed:', e
        td_index += 1

        # PER
        for index, each in enumerate(datas[td_index].find_all('td')):
            try:
                settle_info_list[index].per = float(each.string.strip().replace(',', ''))
            except Exception as e:
                settle_info_list[index].per = None
                print 'ERROR: get per failed:', e
        td_index += 1

        for index, each in enumerate(datas[td_index].find_all('td')):
            try:
                settle_info_list[index].capital = int(each.string.strip().replace(',', ''))
            except Exception as e:
                settle_info_list[index].capital = None
                print 'ERROR: get capital failed:', e
        td_index += 1

        for index, each in enumerate(datas[td_index].find_all('td')):
            try:
                settle_info_list[index].pbr = float(each.string.strip().replace(',', ''))
            except Exception as e:
                settle_info_list[index].pbr = None
                print 'ERROR: get pbr failed:', e
        td_index += 1

        # 배당
        for index, each in enumerate(datas[td_index].find_all('td')):
            try:
                settle_info_list[index].div = int(each.string.strip().replace(',', ''))
            except Exception as e:
                settle_info_list[index].div = 0
                print 'ERROR: get div failed:', e
        td_index += 1

        # 시가배당률
        for index, each in enumerate(datas[td_index].find_all('td')):
            try:
                settle_info_list[index].div_rate = float(each.string.strip().replace(',', ''))
            except Exception as e:
                settle_info_list[index].div_rate = None
                print 'ERROR: get div rate failed:', e
        td_index += 1

        # ROE
        for index, each in enumerate(datas[td_index].find_all('td')):
            try:
                settle_info_list[index].roe = float(each.string.strip().replace(',', ''))
            except Exception as e:
                settle_info_list[index].roe = None
                print 'ERROR: get roe failed:', e
        td_index += 1

        # 순이익률
        for index, each in enumerate(datas[td_index].find_all('td')):
            try:
                settle_info_list[index].profit_rate = float(each.string.strip().replace(',', ''))
            except Exception as e:
                settle_info_list[index].profit_rate = None
                print 'ERROR: get profit rate failed:', e
        td_index += 1

        # 영업이익률
        for index, each in enumerate(datas[td_index].find_all('td')):
            try:
                settle_info_list[index].biz_profit_rate = float(each.string.strip().replace(',', ''))
            except Exception as e:
                settle_info_list[index].biz_profit_rate = None
                print 'ERROR: get biz profit failed:', e
        td_index += 1

        target_table.append(settle_info_list)
    except Exception as e:
        print 'ERROR: get itooza item info failed:', e


def calculate_value(item):
    # value = (eps + div * 4) /price # 연간
    settle_year = item.settle_info[1]
    year_count = 4
    eps = []
    div = []
    modifier = 1.0
    qualified = True
    for settle in settle_year:
        if item.settle_month is None:
            return False, -100
        if settle.settle_period is not None and settle.settle_period[1] == item.settle_month:
            if settle.eps_cont:
                eps.append(settle.eps_cont)
                div.append(settle.div)
            if settle.eps_cont < 0:
                qualified = False
        year_count -= 1
        if year_count <= 0:
            break

    if len(eps) == 0 or len(div) == 0:
        return False, -100

    eps = reduce(lambda x, y: x + y, eps, 0) / len(eps)
    div = reduce(lambda x, y: x + y, div, 0) / len(div)

    return qualified, modifier * (eps + div * 4) / item.price


def calculate_value_by_div(item):
    settle_year = item.settle_info[1]
    year_count = 4
    div = []
    qualified = True
    for settle in settle_year:
        if item.settle_month is None:
            return False, -100
        if settle.settle_period is not None and settle.settle_period[1] == item.settle_month:
            if settle.eps_cont:
                div.append(settle.div)
            if settle.eps_cont < 0:
                qualified = False
        year_count -= 1
        if year_count <= 0:
            break

    if len(div) == 0:
        return False, -100

    div_sum = reduce(lambda x, y: x + y, div, 0) / len(div)

    return qualified, 1.0 * div_sum / item.price


def analysis(*evaluate_funcs):
    print 'analysis start : time {}'.format(time.time())

    items = get_item_analysis()
    print 'GetItemAnalysis completed : time {}, item count {}'.format(time.time(), len(items))

    for func in evaluate_funcs:
        print '-'*10
        print 'value function : ', func
        for item in items:
            try:
                item.value = func(item)
            except Exception as e:
                item.value = False, 0.0
                print 'ERROR: calculate value failed:', e, ':', item.code, ',', item.name
        print 'calculate value completed : time {}'.format(time.time())

        # items = filter(lambda x : x.value[0], items)
        items.sort(key=lambda x: x.value[1], reverse=True)
        print 'sort completed : time {}'.format(time.time())
        print '-' * 80

        for item in items:
            try:
                if item.value[0]:
                    print ','.join(map(lambda x: unicode(x), (
                        item.name, item.code, item.value[1], item.price, item.market_capital,
                        item.par_value)))
            except Exception as e:
                if item.value[0]:
                    print ','.join(map(lambda x: unicode(x), (
                        '', item.code, item.value[1], item.price, item.market_capital, item.par_value)))


def main():
    analysis(calculate_value_by_div, calculate_value)


if __name__ == '__main__':
    main()
