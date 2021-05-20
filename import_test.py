# returns a list of all tickers active from sharadar data. about 6,000 tickers

import zipfile
import os
import pandas as pd

with zipfile.ZipFile('SF1_download.csv.zip') as z:
    for filename in z.namelist():
        if not os.path.isdir(filename):
            with z.open(filename) as f:
                sf1_table = pd.read_csv(f).drop_duplicates(subset='ticker')

with zipfile.ZipFile('TICKERS_download.csv.zip') as z:
    for filename in z.namelist():
        if not os.path.isdir(filename):
            with z.open(filename) as f:
                tickers_table = pd.read_csv(f).drop_duplicates(subset='ticker')
                tickers_table = tickers_table[tickers_table['isdelisted'] == 'N']

# inner merge ticker_data table and fundamental data table using the ticker symbol as the key
sf1_and_tickers_merged = pd.merge(left=sf1_table, right=tickers_table, left_on='ticker', right_on='ticker')
tickers = sf1_and_tickers_merged['ticker']

all_tickers = []
for index, ticker in tickers.iteritems():
    if ticker not in all_tickers:
        all_tickers.append(ticker)
