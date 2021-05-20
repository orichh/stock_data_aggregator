# TODO create code for scraping whalewisdom daily 13d/g filings.
# TODO create code to show industry/sector changes by using etfs/indexes
# TODO create deep fundamental analysis view showing trends over the years
# TODO should i create classes? when would it make sense to do so?

import main_stocks_price_finder as mspf
import pandas as pd
import zipfile
import os

# TODO add code to check when the file was last updated. if a period of time has passed, run function to overwrite
# get most recent ticker prices. saved data to 'test_price_data.csv'
mspf.get_price_and_changes()

# get most recent 52-week high and low, business summary, and market cap. saves data to 'test_other_data.csv'
# mspf.get_other_data()

# merge the two csvs created from above to 'test_ticker_data.csv', then deletes test_price_data.csv
mspf.merge_files()

# merge all data sources: sharadar SF1 and TICKER, ticker price from scraping, other data from scraping
ticker_data = pd.read_csv('test_ticker_data.csv')
openinsider_data = pd.read_csv('openinsider_data.csv')

merged_df = pd.merge(
    left=ticker_data, right=openinsider_data,
    left_on='ticker', right_on='ticker',
    how='left'
)

with zipfile.ZipFile('SF1_download.csv.zip') as z:
    for filename in z.namelist():
        if not os.path.isdir(filename):
            with z.open(filename) as f:
                df_sf1 = pd.read_csv(f)

trailing = df_sf1[df_sf1['dimension'] == 'ART']
latest = trailing.sort_values('calendardate', ascending=False).drop_duplicates('ticker').sort_index()
sf1_latest_filtered = latest[latest['calendardate'] >= '2020-03-31']

with zipfile.ZipFile('TICKERS_download.csv.zip') as z:
    for filename in z.namelist():
        if not os.path.isdir(filename):
            with z.open(filename) as f:
                df_tickers = pd.read_csv(f)

tickers_drop_duplicates = df_tickers.drop_duplicates('ticker')

sharadar_sf1_tickers_merged = pd.merge(
    left=sf1_latest_filtered, right=tickers_drop_duplicates,
    left_on='ticker', right_on='ticker',
    how='left'
)

sharadar_sf1_tickers = sharadar_sf1_tickers_merged[(sharadar_sf1_tickers_merged['isdelisted'] == 'N') & (sharadar_sf1_tickers_merged['calendardate'] >= '2020-03-31')]

sf1_ticker_price_openinsider_merged = pd.merge(
    left=sharadar_sf1_tickers, right=merged_df,
    left_on='ticker', right_on='ticker',
    how='left'
)

# drop columns
sf1_ticker_price_openinsider_merged = sf1_ticker_price_openinsider_merged.drop(columns=[
    'dimension', 'datekey', 'reportperiod', 'lastupdated_x', 'shareswadil',
    'table', 'permaticker', 'exchange', 'isdelisted', 'category', 'cusips', 'siccode', 'sicsector',
    'sicindustry', 'famasector', 'famaindustry', 'scalemarketcap', 'scalerevenue', 'relatedtickers',
    'lastupdated_y', 'firstadded', 'firstpricedate', 'lastpricedate', 'firstquarter', 'lastquarter'
])

sf1_ticker_price_openinsider_merged.to_csv('sf1_ticker_price_openinsider_merged.csv')

testing = pd.read_csv('sf1_ticker_price_openinsider_merged.csv')

# create new columns
testing['market_cap'] = testing['price_y'] * testing['sharesbas'] * testing['sharefactor']
testing['s/p'] = testing['revenue'] / testing['market_cap']
testing['ebitda/ev'] = testing['ebitda'] / (testing['market_cap'] + testing['debt'] - testing['cashnequsd'])
testing['tb/p'] = testing['tbvps'] / testing['price_y']
testing['b/p'] = testing['bvps'] / testing['price_y']
testing['e/p'] = testing['eps'] / testing['price_y']
testing['cfo/p'] = testing['ncfo'] / testing['market_cap']
testing['sfcf/p'] = testing['fcf'] / testing['market_cap']
testing['ncf/p'] = testing['ncf'] / testing['market_cap']
testing['div/p'] = testing['dps'] / testing['price_y']
testing['cash/p'] = testing['cashneq'] / testing['market_cap']
testing['ncash/p'] = (testing['cashneq'] - testing['liabilities']) / testing['market_cap']
testing['nn/p'] = (testing['assetsc'] - testing['liabilities']) / testing['market_cap']
testing['retearn/mc'] = testing['retearn'] / testing['market_cap']
testing['revs/debt'] = testing['revenue'] / testing['debt']
testing['mc/ev'] = testing['market_cap'] / (testing['market_cap'] + testing['debt'] - testing['cashnequsd'])

# re-order columns
tracker = testing[[
    'ticker', 'name', 'sector', 'industry', 'summary', 'market_cap', 'price_y', 'change', 'one_week_num', 'one_week_sum',
    'one_month_num', 'one_month_sum', 'six_month_num', 'six_month_sum', '% to 52-week low', '% to 52-week high',
    'revenue', 's/p', 'ebitda/ev', 'tb/p', 'b/p', 'e/p', 'cfo/p', 'sfcf/p', 'ncf/p', 'div/p', 'cash/p',
    'ncash/p', 'nn/p', 'retearn/mc', 'revs/debt', 'mc/ev', 'secfilings', 'ww', 'sa'
]]

tracker.to_csv('tracker.csv')