# fetches zip folders from quandl. api is too slow to load

import json
import sys
import time

api_key = 'api key here'
table = 'TICKERS'
destFileRef = 'TICKERS_download.csv.zip'
url = 'https://www.quandl.com/api/v3/datatables/SHARADAR/%s.json?qopts.export=true&api_key=%s' % (table, api_key)

def bulk_fetch(url=url, destFileRef=destFileRef):
    version = sys.version.split(' ')[0]
    if version < '3':
        import urllib2
        fn = urllib2.urlopen
    else:
        import urllib.request as urllib
        fn = urllib.urlopen

    valid = ['fresh', 'regenerating']
    invalid = ['generating']
    status = ''

    while status not in valid:
        Dict = json.loads(fn(url).read())
        last_refreshed_time = Dict['datatable_bulk_download']['datatable']['last_refreshed_time']
        status = Dict['datatable_bulk_download']['file']['status']
        link = Dict['datatable_bulk_download']['file']['link']
        print(status)
        if status not in valid:
            time.sleep(60)

    print('fetching from %s' % link)
    zipString = fn(link).read()
    f = open(destFileRef, 'wb')
    f.write(zipString)
    f.close()
    print('fetched')

if __name__ == "__main__":
    bulk_fetch()