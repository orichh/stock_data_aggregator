# finds ticker prices and other supplementary data. prices retrieves faster than the supplementary data.
# 90-95% retrieve from yahoo finance as they use reactjs, so can query client db directly


# TODO delete nasdaq stuff. no longer need
# download the most recent csv from the nasdaq site containing stock details
def download_nasdaq_csv():
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    from selenium import webdriver
    import time

    # check if nasdaq csv already exists
    import glob
    import os
    download_path = os.getcwd()
    list_of_files = glob.glob("{}\*.csv".format(download_path))  # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    if latest_file.split("\\")[-1].startswith("nasdaq_screener"):
        print("csv already downloaded")

    else:
        user_agent = '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'''
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('user-agent={0}'.format(user_agent))
        capa = DesiredCapabilities.CHROME
        capa["pageLoadStrategy"] = "none"
        driver = webdriver.Chrome(options=options, desired_capabilities=capa)
        download_path = os.getcwd()
        params = {'behavior': 'allow', 'downloadPath': download_path}
        driver.execute_cdp_cmd('Page.setDownloadBehavior', params)
        driver.set_window_size(1440, 900)

        driver.get("https://www.nasdaq.com/market-activity/stocks/screener")
        driver.implicitly_wait(5)

        link = driver.find_element_by_class_name("nasdaq-screener__download")
        link.click()
        time.sleep(5)
        driver.quit()

def get_latest_nasdaq_csv():
    import glob
    import os
    download_path = os.getcwd()
    list_of_files = glob.glob("{}\*.csv".format(download_path))  # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    if latest_file.split("\\")[-1].startswith("nasdaq_screener"):
        print("good to go")
        # file_name = latest_file.split("\\")[-1]
        with open(latest_file) as f:
            latest_file_all_rows = f.readlines()
            latest_file_first_row = latest_file_all_rows[0]
            latest_file_other_rows = latest_file_all_rows[1:]
            latest_file_total_num_rows = len(latest_file_other_rows)

        nasdaq_stock_data_dict = dict()

        for x in latest_file_other_rows:
            x_split = x.split(',')

            # remove dollar sign from price
            text_price = x_split[2][1:]

            # filter out market caps that are zero or an empty string
            if x_split[5] != '' and float(x_split[5]) > 0:
                symbol = x_split[0]
                price = float(text_price)
                market_cap = int(float(x_split[5]))
                shares = int(market_cap / price)
                sector = x_split[9]
                industry = x_split[10].replace('\n', '')
                insert_dict = {'price': price,
                               'market cap': market_cap,
                               'shares': shares,
                               'sector': sector,
                               'industry': industry
                               }
                nasdaq_stock_data_dict[symbol] = insert_dict

        return nasdaq_stock_data_dict
    else:
        print("error")


def delete_latest_nasdaq_csv():
    import glob
    import os
    download_path = os.getcwd()
    list_of_files = glob.glob("{}\*.csv".format(download_path))  # * means all if need specific format then *.csv
    latest_file = max(list_of_files, key=os.path.getctime)
    if latest_file.split("\\")[-1].startswith("nasdaq_screener"):
        try:
            os.remove(latest_file)
        except OSError as e:
            pass
    else:
        print("error")


def find_price_nasdaq(t):
    from bs4 import BeautifulSoup as bs
    from bs4 import SoupStrainer as ss
    from selenium import webdriver
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    import time
    from fake_useragent import UserAgent

    ua = UserAgent()
    user_agent = ua.random
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('user-agent={0}'.format(user_agent))
    capa = DesiredCapabilities.CHROME
    capa["pageLoadStrategy"] = "none"
    driver = webdriver.Chrome(options=options, desired_capabilities=capa)
    driver.set_window_size(1440, 900)
    driver.get('https://www.nasdaq.com/market-activity/stocks/{}'.format(t))
    time.sleep(4)
    plain_text = driver.page_source
    driver.quit()
    only_class = ss(class_='symbol-page-header__pricing-price')
    soup = bs(plain_text, 'html.parser', parse_only=only_class)
    prices_found = []
    for result in soup:
        if result.text != '':
            price = result.text
            prices_found.append(price)
    price = float(max(prices_found).replace('$', ''))
    return {'price': price}


# can't use as the site now requires a captcha
# def find_price_seekingalpha(t):
#     from bs4 import BeautifulSoup as bs
#     from bs4 import SoupStrainer as ss
#     from selenium import webdriver
#     from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#     import time
#
#     user_agent = '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'''
#     options = webdriver.ChromeOptions()
#     options.add_argument('headless')
#     options.add_argument('user-agent={0}'.format(user_agent))
#     capa = DesiredCapabilities.CHROME
#     capa["pageLoadStrategy"] = "none"
#     driver = webdriver.Chrome(options=options, desired_capabilities=capa)
#     driver.set_window_size(1440, 900)
#     driver.get('https://seekingalpha.com/symbol/{}?source%3Dcontent_type%3Areact%7Csource%3Asearch-basic'.format(t))
#     time.sleep(4)
#     only_class = ss(class_='__0e5d9-3vmRj _ae984-2mMGD _ae984-2S5bj _ae984-31a8l _ae984-1AeRq _ae984-1qVOE _ae984-3sLCv _ae984-38BKy _ae984-Cvk77')
#     plain_text = driver.page_source
#     driver.quit()
#     soup = bs(plain_text, 'html.parser', parse_only=only_class)
#     price = float(soup.text)
#     return {'price': price}


def find_price_yfinance(t):
    import requests
    import time
    import json
    from fake_useragent import UserAgent

    ua = UserAgent()
    user_agent = ua.random
    header = {'user-agent': user_agent}

    # get price
    url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/{}?modules=price'
    f = requests.get(url.format(t), headers=header)
    time.sleep(1/100)
    html_content = f.content
    s = str(html_content,'utf-8')
    data = json.loads(s)
    price = data['quoteSummary']['result'][0]['price']['regularMarketPrice']['raw']
    change = data['quoteSummary']['result'][0]['price']['regularMarketChangePercent']['fmt']

    return {'price': price, 'change': change}


def find_price_marketwatch(t):
    import requests
    from bs4 import BeautifulSoup as bs
    from bs4 import SoupStrainer as ss
    import time
    from fake_useragent import UserAgent

    ua = UserAgent()
    user_agent = ua.random

    header = {'user-agent': user_agent}
    url = 'https://www.marketwatch.com/investing/stock/{}?mod=over_search'
    f = requests.get(url.format(t, t), headers=header)
    time.sleep(2)
    only_class = ss(class_='intraday__data')
    soup = bs(f.content, 'html.parser', parse_only=only_class)
    price = float(soup.find(class_='value').text)
    return {'price': price}


def find_price_barrons(t):
    import requests
    from bs4 import BeautifulSoup as bs
    from bs4 import SoupStrainer as ss
    import time
    from fake_useragent import UserAgent

    ua = UserAgent()
    user_agent = ua.random

    header = {'user-agent': user_agent}
    url = 'https://www.barrons.com/quote/stock/{}'
    f = requests.get(url.format(t), headers=header)
    time.sleep(2)

    html_test = f.content
    price_class = ss(class_='market__price bgLast')
    price = float(bs(html_test, 'html.parser', parse_only=price_class).text)
    return {'price': price}


def find_price_tradingview(t):
    from bs4 import BeautifulSoup as bs
    from bs4 import SoupStrainer as ss
    from selenium import webdriver
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    import time
    from fake_useragent import UserAgent

    ua = UserAgent()
    user_agent = ua.random

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('user-agent={0}'.format(user_agent))
    capa = DesiredCapabilities.CHROME
    capa["pageLoadStrategy"] = "none"
    driver = webdriver.Chrome(options=options, desired_capabilities=capa)
    driver.set_window_size(1440, 900)
    driver.get('https://www.tradingview.com/symbols/{}/'.format(t))
    time.sleep(4)
    plain_text = driver.page_source
    driver.quit()

    only_class = ss(class_='tv-symbol-price-quote__value js-symbol-last')
    price = float(bs(plain_text, 'html.parser', parse_only=only_class).text)
    return {'price': price}


def yfinance_other_data(t):
    import requests
    import time
    import json
    from fake_useragent import UserAgent

    ua = UserAgent()
    user_agent = ua.random

    # get market cap and 52 week range from table
    header = {'user-agent': user_agent}
    url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/{}?modules=summaryDetail'
    f = requests.get(url.format(t), headers=header)
    time.sleep(1/100)
    html_content = f.content
    s = str(html_content,'utf-8')
    data = json.loads(s)
    market_cap = data['quoteSummary']['result'][0]['summaryDetail']['marketCap']['raw']
    fifty_two_week_low = data['quoteSummary']['result'][0]['summaryDetail']['fiftyTwoWeekLow']['raw']
    fifty_two_week_high = data['quoteSummary']['result'][0]['summaryDetail']['fiftyTwoWeekHigh']['raw']

    # get business summary
    url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/{}?modules=summaryProfile'
    f = requests.get(url.format(t), headers=header)
    time.sleep(1 / 100)
    html_content = f.content
    s = str(html_content, 'utf-8')
    data = json.loads(s)
    business_summary = data['quoteSummary']['result'][0]['summaryProfile']['longBusinessSummary']

    data = {
        'market_cap': market_cap,
        'fifty_two_week_low': fifty_two_week_low,
        'fifty_two_week_high': fifty_two_week_high,
        'business_summary': business_summary
    }
    return data


def marketwatch_other_data(t):
    import requests
    from bs4 import BeautifulSoup as bs
    from bs4 import SoupStrainer as ss
    import time
    from fake_useragent import UserAgent

    ua = UserAgent()
    user_agent = ua.random

    # get market cap and 52 week range from table
    header = {'user-agent': user_agent}
    url = 'https://www.marketwatch.com/investing/stock/{}?mod=over_search'
    f = requests.get(url.format(t, t), headers=header)
    time.sleep(4)
    only_class = ss(class_='list list--kv list--col50')
    soup = bs(f.content, 'html.parser', parse_only=only_class)
    mlist = soup.find_all(class_='primary')

    fifty_two_week_range = mlist[2].text.split(' - ')
    fifty_two_week_low = float(fifty_two_week_range[0])
    fifty_two_week_high = float(fifty_two_week_range[1])

    market_cap_string = mlist[3].text.replace('$', '')

    if market_cap_string[-1] == 'T':
        split = market_cap_string.split('.')
        first = int(split[0]) * (10 ** 12)
        second = int(split[1].replace('T', '')) * (10 ** 9)
        market_cap = first + second

    if market_cap_string[-1] == 'B':
        split = market_cap_string.split('.')
        first = int(split[0]) * (10 ** 9)
        second = int(split[1].replace('B', '')) * (10 ** 6)
        market_cap = first + second

    elif market_cap_string[-1] == 'M':
        split = market_cap_string.split('.')
        first = int(split[0]) * (10 ** 6)
        second = int(split[1].replace('M', '')) * (10 ** 3)
        market_cap = first + second

    data = {
        'market_cap': market_cap,
        'fifty_two_week_low': fifty_two_week_low,
        'fifty_two_week_high': fifty_two_week_high
    }
    return data


# can't use as the site now requires a captcha
# def seekingalpha_other_data(t):
#     from bs4 import BeautifulSoup as bs
#     from bs4 import SoupStrainer as ss
#     from selenium import webdriver
#     from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
#     import time
#
#     user_agent = '''Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'''
#     options = webdriver.ChromeOptions()
#     options.add_argument('headless')
#     options.add_argument('user-agent={0}'.format(user_agent))
#     capa = DesiredCapabilities.CHROME
#     capa["pageLoadStrategy"] = "none"
#     driver = webdriver.Chrome(options=options, desired_capabilities=capa)
#     driver.set_window_size(1440, 900)
#     driver.get('https://seekingalpha.com/symbol/{}?source%3Dcontent_type%3Areact%7Csource%3Asearch-basic'.format(t))
#     time.sleep(4)
#     plain_text = driver.page_source
#     driver.quit()
#
#     # find 52-week low
#     only_class_52_week_low = ss(class_='_de433-2yNuD _ae984-2BHuS')
#     low = bs(plain_text, 'html.parser', parse_only=only_class_52_week_low)
#     low_list = []
#     for x in low:
#         low_list.append(x.text)
#     fifty_two_week_low = float(low_list[0])
#
#     # find 52-week high
#     only_class_52_week_low = ss(class_='_de433-3kOlG _ae984-P6mcd')
#     high = bs(plain_text, 'html.parser', parse_only=only_class_52_week_low)
#     high_list = []
#     for x in high:
#         high_list.append(x.text)
#     fifty_two_week_high = float(high_list[0])
#
#     # find market-cap
#     only_class_market_cap = ss(
#         class_='__01285-27GgL __01285-32N8X _ae984-2mMGD _ae984-2S5bj _ae984-2sNIT _ae984-1izsF _ae984-i4vRV _ae984-2cU_s __01285-1FkLo _ae984-2mMGD _ae984-2S5bj _ae984-2mut4 _ae984-10rrJ _ae984-11HiX')
#     mc = bs(plain_text, 'html.parser', parse_only=only_class_market_cap)
#     mc_list = []
#     for x in mc:
#         mc_list.append(x.text)
#     market_cap_string = mc_list[5].replace('$', '')
#
#     if market_cap_string[-1] == 'T':
#         split = market_cap_string.split('.')
#         first = int(split[0]) * (10 ** 12)
#         second = int(split[1].replace('T', '')) * (10 ** 9)
#         market_cap = first + second
#
#     if market_cap_string[-1] == 'B':
#         split = market_cap_string.split('.')
#         first = int(split[0]) * (10 ** 9)
#         second = int(split[1].replace('B', '')) * (10 ** 6)
#         market_cap = first + second
#
#     elif market_cap_string[-1] == 'M':
#         split = market_cap_string.split('.')
#         first = int(split[0]) * (10 ** 6)
#         second = int(split[1].replace('M', '')) * (10 ** 3)
#         market_cap = first + second
#
#     elif market_cap_string[-1] == 'K':
#         split = market_cap_string.split('.')
#         first = int(split[0]) * (10 ** 3)
#         second = int(split[1].replace('K', '')) * (10 ** 0)
#         market_cap = first + second
#
#     return {
#         'fifty_two_week_low': fifty_two_week_low,
#         'fifty_two_week_high': fifty_two_week_high,
#         'market_cap': market_cap
#     }

def barrons_other_data(t):
    import requests
    import time
    import pandas as pd
    from fake_useragent import UserAgent

    ua = UserAgent()
    user_agent = ua.random

    header = {'user-agent': user_agent}
    url = 'https://www.barrons.com/quote/stock/{}'
    f = requests.get(url.format(t), headers=header)
    time.sleep(2)

    html_test = f.content
    df_list_test = pd.read_html(html_test)

    fifty_two_week_low = float(df_list_test[0][1][4].split(' - ')[0].replace('$', ''))
    fifty_two_week_high = float(df_list_test[0][1][4].split(' - ')[1].replace('$', ''))
    market_cap_string = df_list_test[0][1][5].replace('$', '')

    if market_cap_string[-1] == 'T':
        split = market_cap_string.split('.')
        first = int(split[0]) * (10 ** 12)
        second = int(split[1].replace('T', '')) * (10 ** 9)
        market_cap = first + second

    if market_cap_string[-1] == 'B':
        split = market_cap_string.split('.')
        first = int(split[0]) * (10 ** 9)
        second = int(split[1].replace('B', '')) * (10 ** 6)
        market_cap = first + second

    elif market_cap_string[-1] == 'M':
        split = market_cap_string.split('.')
        first = int(split[0]) * (10 ** 6)
        second = int(split[1].replace('M', '')) * (10 ** 3)
        market_cap = first + second

    elif market_cap_string[-1] == 'K':
        split = market_cap_string.split('.')
        first = int(split[0]) * (10 ** 3)
        second = int(split[1].replace('K', '')) * (10 ** 0)
        market_cap = first + second

    data = {
        'market_cap': market_cap,
        'fifty_two_week_low': fifty_two_week_low,
        'fifty_two_week_high': fifty_two_week_high
    }

    return data


def nasdaq_other_data(t):
    from bs4 import BeautifulSoup as bs
    from bs4 import SoupStrainer as ss
    from selenium import webdriver
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    import time
    from fake_useragent import UserAgent

    ua = UserAgent()
    user_agent = ua.random
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('user-agent={0}'.format(user_agent))
    capa = DesiredCapabilities.CHROME
    capa["pageLoadStrategy"] = "none"
    driver = webdriver.Chrome(options=options, desired_capabilities=capa)
    driver.set_window_size(1440, 900)
    driver.get('https://www.nasdaq.com/market-activity/stocks/{}'.format(t))
    time.sleep(2)
    driver.execute_script("window.scrollTo(0, 800)")
    time.sleep(4)
    plain_text = driver.page_source
    driver.quit()

    # find table
    only_table_class = ss(class_="summary-data__cell")
    table = bs(plain_text, 'html.parser', parse_only=only_table_class)

    cell_list = []

    for x in table:
        cell_list.append(x.text)

    fifty_two_week_high_low = cell_list[8].split('/')

    # find 52-week low
    fifty_two_week_low = float(fifty_two_week_high_low[1].replace('$', ''))

    # find 52-week high
    fifty_two_week_high = float(fifty_two_week_high_low[0].replace('$', ''))

    # market cap
    market_cap = int(cell_list[9].replace(',', ''))

    return {
        'fifty_two_week_low': fifty_two_week_low,
        'fifty_two_week_high': fifty_two_week_high,
        'market_cap': market_cap
    }


def tradingview_other_data(t):
    from bs4 import BeautifulSoup as bs
    from bs4 import SoupStrainer as ss
    from selenium import webdriver
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    import time
    from fake_useragent import UserAgent

    ua = UserAgent()
    user_agent = ua.random
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('user-agent={0}'.format(user_agent))
    capa = DesiredCapabilities.CHROME
    capa["pageLoadStrategy"] = "none"
    driver = webdriver.Chrome(options=options, desired_capabilities=capa)
    driver.set_window_size(1440, 900)
    driver.get('https://www.tradingview.com/symbols/{}/'.format(t))
    time.sleep(4)
    plain_text = driver.page_source
    driver.quit()

    only_class = ss(class_='tv-widget-fundamentals__value apply-overflow-tooltip')
    found = bs(plain_text, 'html.parser', parse_only=only_class)
    found_list = []
    for x in found:
        found_list.append(x.text)

    # market_cap
    market_cap_string = found_list[0].strip()

    # find 52-week low
    fifty_two_week_low = float(found_list[23].strip())

    # find 52-week high
    fifty_two_week_high = float(found_list[22].strip())

    split = market_cap_string.split('.')

    if len(market_cap_string) > 1:
        if market_cap_string[-1] == 'T':
            first = int(split[0]) * (10 ** 12)
            second = int(split[1].replace('T', '')) * (10 ** 9)
            market_cap = first + second

        elif market_cap_string[-1] == 'B':
            first = int(split[0]) * (10 ** 9)
            second = int(split[1].replace('B', '')) * (10 ** 6)
            market_cap = first + second

        elif market_cap_string[-1] == 'M':
            first = int(split[0]) * (10 ** 6)
            second = int(split[1].replace('M', '')) * (10 ** 3)
            market_cap = first + second

        elif market_cap_string[-1] == 'K':
            first = int(split[0]) * (10 ** 3)
            second = int(split[1].replace('K', '')) * (10 ** 0)
            market_cap = first + second

        data = {
            'market_cap': market_cap,
            'fifty_two_week_low': fifty_two_week_low,
            'fifty_two_week_high': fifty_two_week_high
        }
    else:
        data = {
            'fifty_two_week_low': fifty_two_week_low,
            'fifty_two_week_high': fifty_two_week_high
        }
    return data


def find_ticker_prices_from_all(lst):
    from datetime import datetime
    print("start to find ticker prices")
    print(datetime.now().strftime("%H:%M:%S"))

    stocks_prices_dict = {}
    for ticker in lst:
        try:
            price_and_change = find_price_yfinance(ticker)
            stocks_prices_dict[ticker] = price_and_change
        except:
            try:
                price = find_price_marketwatch(ticker)
                stocks_prices_dict[ticker] = price
            except:
                try:
                    price = find_price_nasdaq(ticker)
                    stocks_prices_dict[ticker] = price
                except:
                    try:
                        price = find_price_barrons(ticker)
                        stocks_prices_dict[ticker] = price
                    except:
                        try:
                            price = find_price_tradingview(ticker)
                            stocks_prices_dict[ticker] = price
                        except:
                            pass
        print("still working!")
    print("finished: " + datetime.now().strftime("%H:%M:%S"))
    return stocks_prices_dict


def find_all_other_data(tickers_list):
    from datetime import datetime
    print("start to find all other data")
    print(datetime.now().strftime("%H:%M:%S"))

    other_stocks_data_dict = {}
    for ticker in tickers_list:
        try:
            data = yfinance_other_data(ticker)
            other_stocks_data_dict[ticker] = {
                'market_cap': data['market_cap'],
                'fifty_two_week_low': data['fifty_two_week_low'],
                'fifty_two_week_high': data['fifty_two_week_high'],
                'business_summary': data['business_summary']
            }
        except:
            try:
                data = marketwatch_other_data(ticker)
                other_stocks_data_dict[ticker] = {
                    'market_cap': data['market_cap'],
                    'fifty_two_week_low': data['fifty_two_week_low'],
                    'fifty_two_week_high': data['fifty_two_week_high']
                }
            except:
                try:
                    data = nasdaq_other_data(ticker)
                    other_stocks_data_dict[ticker] = {
                        'market_cap': data['market_cap'],
                        'fifty_two_week_low': data['fifty_two_week_low'],
                        'fifty_two_week_high': data['fifty_two_week_high']
                    }
                except:
                    try:
                        data = barrons_other_data(ticker)
                        other_stocks_data_dict[ticker] = {
                            'market_cap': data['market_cap'],
                            'fifty_two_week_low': data['fifty_two_week_low'],
                            'fifty_two_week_high': data['fifty_two_week_high']
                        }
                    except:
                        try:
                            data = tradingview_other_data(ticker)
                            other_stocks_data_dict[ticker] = {
                                'market_cap': data['market_cap'],
                                'fifty_two_week_low': data['fifty_two_week_low'],
                                'fifty_two_week_high': data['fifty_two_week_high']
                            }
                        except:
                            pass
        print("still working!")
    print("finished: " + datetime.now().strftime("%H:%M:%S"))
    return other_stocks_data_dict


# Multithreading
def multithreader(agg_function, stock_list, threads=60):
    import concurrent.futures
    import numpy as np

    # shuffle the tickers around to make sure the split arrays to hopefully have an even amount of
    # tickers that go through the javascript/CPU heavy seekingalpha and nasdaq scraping processes
    tickers_shuffled = np.array(stock_list)
    np.random.shuffle(tickers_shuffled)
    list_list = np.array_split(tickers_shuffled, threads)

    # if __name__ == "__main__":
    # set the number of threads
    num_threads = min(threads, len(stock_list))

    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        prices_list_of_dict = list(executor.map(agg_function, list_list))

    return prices_list_of_dict


def delete_test_csv_file(file_name):
    import glob
    import os
    # download_path = os.getcwd()
    # list_of_files = glob.glob("{}\*.csv".format(download_path))  # * means all if need specific format then *.csv
    # for file in list_of_files:
    # latest_file = max(list_of_files, key=os.path.getctime)
    # if latest_file.split("\\")[-1].startswith(file_name):
    try:
        os.remove(file_name)
    except OSError as e:
        print("error")
        pass


# get updated ticker prices and daily percent changes
def get_price_and_changes():
    from import_test import all_tickers
    import csv

    hope_to_god = multithreader(find_ticker_prices_from_all, all_tickers, threads=120)
    with open('test_price_data.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(['ticker', 'price', 'change'])
        for dictionary in hope_to_god:
            for ticker, price_and_change in dictionary.items():
                try:
                    price = price_and_change['price']
                    change = price_and_change['change']
                    csv_writer.writerow([ticker, price, change])
                except KeyError:
                    price = price_and_change['price']
                    csv_writer.writerow([ticker, price])

# get other data
def get_other_data():
    from import_test import all_tickers
    import csv
    all_other_stock_data = multithreader(find_all_other_data, all_tickers, 120)
    with open('test_other_data.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',')
        csv_writer.writerow(['ticker', 'market_cap', 'fifty_two_week_low', 'fifty_two_week_high', 'sa', 'ww', 'summary'])
        for dictionary in all_other_stock_data:
            for ticker, data in dictionary.items():
                try:
                    market_cap = data['market_cap']
                    low = data['fifty_two_week_low']
                    high = data['fifty_two_week_high']
                    seekingalpha_link = 'https://seekingalpha.com/symbol/{}?source%3Dcontent_type%3Areact%7Csource%3Asearch-basic'.format(ticker)
                    whalewisdom_link = 'https://whalewisdom.com/stock/{}'.format(ticker)
                    summary = data['business_summary']
                    csv_writer.writerow([ticker, market_cap, low, high, seekingalpha_link, whalewisdom_link, summary])
                except (KeyError, UnicodeEncodeError):
                    market_cap = data['market_cap']
                    low = data['fifty_two_week_low']
                    high = data['fifty_two_week_high']
                    seekingalpha_link = 'https://seekingalpha.com/symbol/{}?source%3Dcontent_type%3Areact%7Csource%3Asearch-basic'.format(ticker)
                    whalewisdom_link = 'https://whalewisdom.com/stock/{}'.format(ticker)
                    csv_writer.writerow([ticker, market_cap, low, high, seekingalpha_link, whalewisdom_link])
# get_other_data()


# merge into one csv file
def merge_files():
    import pandas as pd
    df1 = pd.read_csv('test_price_data.csv')
    df2 = pd.read_csv('test_other_data.csv')
    df3 = pd.merge(left=df1, right=df2, left_on='ticker', right_on='ticker', how='left')
    df3.set_index('ticker', inplace=True)
    df3['% to 52-week low'] = df3['price'] / df3['fifty_two_week_low']
    df3['% to 52-week high'] = df3['price'] / df3['fifty_two_week_high']
    df3.to_csv('test_ticker_data.csv')

    # delete csvs that are no longer needed
    delete_test_csv_file('test_price_data.csv')
    # delete_test_csv_file('test_other_data.csv')
