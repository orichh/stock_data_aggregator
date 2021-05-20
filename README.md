# stock_data_aggregator

This is version 1 (as of 5/19/2021) of an ongoing project, and is my first large (for me) project for my personal use and for use in my portfolio while communicating with potential employers.

## What does this project accomplish?
-	Joins data from multiple sources to output a CSV file titled 'tracker.csv' that can be opened in excel and then used as a screener
-	Retrieves fundamental financials from Quandl/Sharadar (via paid subscription) by using their API to download the zip folders and using the os, zipfile, and pandas modules to create a pandas dataframe
-	Scrapes and sums individual insider purchases over 1 day, 1 week, 1 month, and 6 month periods from Openinsider.com using the requests, numpy, pandas, and datetime modules
-	Scrapes and cleans ticker price and supplementary data from Yahoo Finance by cycling through the JSON queries used to populate the client side stores by finding that ReactJS is used for the front-end
-	Scrapes and cleans ticker price and supplementary data from 4 other sites using requests, Selenium Webdriver, and BeautifulSoup for the tickers not available on Yahoo Finance
-	Uses multithreading via the concurrent.futures module to scrape 60-120 pages at a time depending on CPU usage

Note: An API key is necesssary to pull new financial data from Quandl/Sharadar.

## Instructions for use:
1. If you want to get updated pricing and daily change %, go to main.py on line 13 and check if mspf.get_price_and_changes() is commented out. Then on line 19, check if mspf.merge_files() is commented. Keep these uncommented to run the price scraping program. Run main.py and a csv file titled 'tracker.csv' will be available.

2. If you want to get updated 52-week high and low, business summary, seekingalpha and whalewisdom links, then go to main.py on line 16 and check if mspf.get_other_data() is commented out. Keep this uncommented to run the data scraping program. This takes longer than the price scraping program, a few minutes.

3. If you want both the updated pricing data and 'other' data, keep all 3 functions uncommented (mspf.get_price_and_changes() - line 13, mspf.get_other_data() - line 16, and mspf.merge_files() - line 19), then run main.py.

3. To get updated insider purchases, run the file openinsider_data.py separately (run this file first if you want to get this data along with pricing and other data). This will scrape openinsider.com and create a separate csv file. After this finishes, go back to main.py and comment out mspf.get_price_and_changes() and mspf.get_other_data() (unless you want to get updated data for these, too).


## Future capabilities:
1. Retrieve industry/sector data and pricing
2. Using sharadar data, combine data to show a timeline of financials changing over time
