# retrieves insider purchases from openinsider.com then sends to csv. takes a few minutes

# TODO convert to function to call from main.py

import concurrent.futures
import numpy as np
import pandas as pd
from datetime import datetime

# start time for the process
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

# split the tickers list into smaller lists for multithreading
from import_test import all_tickers
list_list = np.array_split(all_tickers, 500)

# openinsider scraper. scrapes all individual trades to account for same person buying over same period
def openinsider_scrape(tickers):
    import requests
    import pandas as pd
    from fake_useragent import UserAgent

    ua = UserAgent()
    user_agent = ua.random

    header = {'user-agent': user_agent}

    # latest 6 months openinsider webpage url
    url_test = 'http://openinsider.com/screener?s={}&o=&pl=&ph=&ll=&lh=&fd=730&fdr=&td=180&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=1&cnt=1000&page=1'

    # url_list collects tables for each ticker
    url_list = list()

    for ticker in tickers:
        url_loop = url_test.format(ticker)
        html_test = requests.get(url_loop, headers=header).content
        df_list_test = pd.read_html(html_test)
        table = df_list_test[-3]

        # test to see if the table with trades exists by checking the type and comparing against expected value
        page_type = str(type(df_list_test[-3].columns))
        correct_type = "<class 'pandas.core.indexes.base.Index'>"
        if page_type == correct_type:
            url_list.append(table)
        # print("still working!")
    return url_list

# multithreading scraping data from openinsider.com. takes about 3 minutes
# if __name__ == "__main__":

# set the number of threads
threads = min(500, len(list_list))

# multithreader
with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
    openinsider_list_list = list(executor.map(openinsider_scrape, list_list))

# append all non-empty lists into one list of list
openinsider_data_list = []
for x in openinsider_list_list:
    if len(x) > 0:
        openinsider_data_list.append(x[0])

# combine list of list into one pandas dataframe
openinsider_data = pd.concat(openinsider_data_list, axis=0)

# replace the spaces in the column names with underscores
openinsider_data.rename(columns=lambda x: x.replace(u'\xa0', u'_'), inplace=True)

# remove and replace special characters and convert column values to integer/float types
chars_to_remove = '|'.join(['\$', '\+', ','])
openinsider_data['Value'] = openinsider_data['Value'].str.replace(chars_to_remove, '', regex=True).astype(int)
openinsider_data['Qty'] = openinsider_data['Qty'].str.replace(chars_to_remove, '', regex=True).astype(float)
openinsider_data['Price'] = openinsider_data['Price'].str.replace(chars_to_remove, '', regex=True).astype(float)

# export data to csv
openinsider_data.to_csv('openinsider_data.csv', sep=',')

now = datetime.now()
current_time = now.strftime("%H:%M:%S")
print("Current Time =", current_time)

import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta

file = openinsider_data

six_months = str(date.today() + relativedelta(months=-6))
one_month = str(date.today() + relativedelta(months=-1))
one_week = str(date.today() + relativedelta(weeks=-1))
one_day = str(date.today() + relativedelta(days=-1))

openinsider_6month_trades = dict()

tickers = file['Ticker']
for ticker in tickers:

    one_day_insiders = list()
    one_day_value = list()

    one_week_insiders = list()
    one_week_value = list()

    one_month_insiders = list()
    one_month_value = list()

    six_month_insiders = list()
    six_month_value = list()

    for index, trade in file[file['Ticker'] == ticker].iterrows():

        trade_date = trade['Trade_Date']
        insider_name = trade['Insider_Name']
        price = trade['Price']
        number_of_shares_traded = trade['Qty']
        value_of_trade = trade['Value']

        # variables to use for later....
        # ticker = trade['Ticker']
        # shares_owned = trade['Owned']
        # trade_type = trade['Trade_Type']

        if trade_date >= one_day:
            if insider_name not in one_day_insiders:
                one_day_insiders.append(insider_name)
            one_day_value.append(value_of_trade)

        if trade_date >= one_week:
            if insider_name not in one_week_insiders:
                one_week_insiders.append(insider_name)
            one_week_value.append(value_of_trade)

        if trade_date >= one_month:
            if insider_name not in one_month_insiders:
                one_month_insiders.append(insider_name)
            one_month_value.append(value_of_trade)

        if trade_date >= six_months:
            if insider_name not in six_month_insiders:
                six_month_insiders.append(insider_name)
            six_month_value.append(value_of_trade)

    if len(one_day_insiders) > 0:
        one_day_num = len(one_day_insiders)
        one_day_sum = sum(one_day_value)
    else:
        one_day_num = 0
        one_day_sum = 0

    if len(one_week_insiders) > 0:
        one_week_num = len(one_week_insiders)
        one_week_sum = sum(one_week_value)
    else:
        one_week_num = 0
        one_week_sum = 0

    if len(one_month_insiders) > 0:
        one_month_num = len(one_month_insiders)
        one_month_sum = sum(one_month_value)
    else:
        one_month_num = 0
        one_month_sum = 0

    if len(six_month_insiders) > 0:
        six_month_num = len(six_month_insiders)
        six_month_sum = sum(six_month_value)
    else:
        six_month_num = 0
        six_month_sum = 0

    # put all of the above into this
    temp_dict = {
        'one_day_num': one_day_num,
        'one_day_sum': one_day_sum,
        'one_week_num': one_week_num,
        'one_week_sum': one_week_sum,
        'one_month_num': one_month_num,
        'one_month_sum': one_month_sum,
        'six_month_num': six_month_num,
        'six_month_sum': six_month_sum
    }

    openinsider_6month_trades[ticker] = temp_dict

import csv

with open('openinsider_data.csv', 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',')
    csv_writer.writerow([
        'ticker',
        'one_day_num',
        'one_day_sum',
        'one_week_num',
        'one_week_sum',
        'one_month_num',
        'one_month_sum',
        'six_month_num',
        'six_month_sum'
    ])
    for ticker, data in openinsider_6month_trades.items():
        one_day_num = data['one_day_num']
        one_day_sum = data['one_day_sum']
        one_week_num = data['one_week_num']
        one_week_sum = data['one_week_sum']
        one_month_num = data['one_month_num']
        one_month_sum = data['one_month_sum']
        six_month_num = data['six_month_num']
        six_month_sum = data['six_month_sum']

        csv_writer.writerow([
            ticker,
            one_day_num,
            one_day_sum,
            one_week_num,
            one_week_sum,
            one_month_num,
            one_month_sum,
            six_month_num,
            six_month_sum
        ])
