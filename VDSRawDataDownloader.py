import requests
from tqdm import tqdm
import datetime
import sys
import os

def search_data(date):
    url = 'http://data.ex.co.kr/portal/fdwn/search'
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': '__smElapsedTime=5; __smDBTime=0; __smEstamp=20230712132536630; __smGlobalId=2b65d37b0b301d4801894858f476; __smVisitorID=5jQS2fFfPWV; JSESSIONID=IX4yWyS2r2UahrwO180pVkDnPFwF1UpXwk9M9zQR211LZUdpxcDOp1TKeE1M9bHS.tclapwas2_servlet_openoasis',
        'Origin': 'http://data.ex.co.kr',
        'Referer': 'http://data.ex.co.kr/portal/fdwn/view?type=VDS&num=16&requestfrom=dataset',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    data = {
        'dataSupplyDate': date,
        'dataSupplyYear': '',
        'dataSupplyMonth': '',
        'dataSupplyYearQ': '',
        'dataSupplyQuater': '',
        'dataSupplyYearY': '',
        'collectType': 'VDS',
        'dataType': '16',
        'collectCycle': '04',
        'supplyCycle': '01'
    }

    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        print("Search request successful.")
        return True
    else:
        print("Search request failed.")
        return False

def download_data(date):
    url = 'http://data.ex.co.kr/portal/fdwn/log'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': '__smElapsedTime=5; __smDBTime=0; __smEstamp=20230712132536630; __smGlobalId=2b65d37b0b301d4801894858f476; __smVisitorID=5jQS2fFfPWV; JSESSIONID=aKA1m3Y8L05wQMyTZtE1ujjwtPXoIlzSwRwjGm1co6vsBzEfxgTealCxOoLXfWJK.tclapwas2_servlet_openoasis',
        'Origin': 'http://data.ex.co.kr',
        'Referer': 'http://data.ex.co.kr/portal/fdwn/view?type=VDS&num=16&requestfrom=dataset',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    data = {
        'dataSupplyDate': date,
        'dataSupplyYear': 'null',
        'dataSupplyMonth': 'null',
        'dataSupplyYearQ': 'null',
        'dataSupplyQuater': 'null',
        'dataSupplyYearY': 'null',
        'collectType': 'VDS',
        'dataType': '16',
        'collectCycle': '04',
        'supplyCycle': '01',
        'outFileName': 'VDS_VDS%EC%9B%90%EC%8B%9C%EC%9E%90%EB%A3%8C_1%EC%9D%BC_1%EC%9D%BC_{}.zip'.format(date)
    }

    response = requests.post(url, headers=headers, data=data, stream=True)
    if response.status_code == 200:
        file_size = int(response.headers.get('Content-Length', 0))
        file_name = '{}.zip'.format(date)
        with open(file_name, 'wb') as file:
            with tqdm(total=file_size, unit='B', unit_scale=True, desc='{} 다운로드 중'.format(date)) as progress:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
                        progress.update(len(chunk))
        print("Download completed.")
        os.rename(file_name, '{}.zip'.format(date))
    else:
        print("Download failed.")

def main(date):
    # 현재 월의 첫 번째 날짜 구하기
    current_date = datetime.datetime.strptime(date + '01', '%Y%m%d').date()
    # 현재 월의 마지막 날짜 구하기
    next_month = current_date.replace(day=28) + datetime.timedelta(days=4)
    last_day = next_month - datetime.timedelta(days=next_month.day)

    while current_date <= last_day:
        current_date_str = current_date.strftime('%Y%m%d')
        if search_data(current_date_str):
            download_data(current_date_str)
        current_date += datetime.timedelta(days=1)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python crawl2.py <year_month>")
        sys.exit(1)

    date = sys.argv[1]
    main(date)
