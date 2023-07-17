import requests
from tqdm import tqdm
import datetime
import sys
import os
import platform
from PyQt5.QtWidgets import QApplication, QFileDialog

# Using
# 1. python VDSRawDataDownloader.py 202303(년+월) : 해당 년/월의 모든 데이터 검색 / 다운로드
# 2. python VDSRawDataDownloader.py 20230304 20230307 : 해당 20230304 ~ 20230307까지의 데이터 검색 / 다운로드

def search_data(date):
    url = 'http://data.ex.co.kr/portal/fdwn/search'
    user_agent = "Mozilla/5.0 ({}; {}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36".format(
        platform.system(), platform.release()
    )
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': '__smElapsedTime=5; __smDBTime=0; __smEstamp=20230712132536630; __smGlobalId=2b65d37b0b301d4801894858f476; __smVisitorID=5jQS2fFfPWV; JSESSIONID=IX4yWyS2r2UahrwO180pVkDnPFwF1UpXwk9M9zQR211LZUdpxcDOp1TKeE1M9bHS.tclapwas2_servlet_openoasis',
        'Origin': 'http://data.ex.co.kr',
        'Referer': 'http://data.ex.co.kr/portal/fdwn/view?type=VDS&num=16&requestfrom=dataset',
        'User-Agent': user_agent,
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

def download_data(date, download_folder):
    user_agent = "Mozilla/5.0 ({}; {}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36".format(
        platform.system(), platform.release()
    )
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
        'User-Agent': user_agent
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

    url = 'http://data.ex.co.kr/portal/fdwn/log'
    response = requests.post(url, headers=headers, data=data, stream=True)

    if response.status_code == 200:
        total_size = int(response.headers.get('Content-Length', 0))
        block_size = 1024  # 1 KB
        progress_bar = tqdm(total=total_size, unit='B', unit_scale=True)

        with open(os.path.join(download_folder, 'temp.zip'), 'wb') as file:
            for chunk in response.iter_content(chunk_size=block_size):
                progress_bar.update(len(chunk))
                file.write(chunk)

        progress_bar.close()

        # Rename the file
        file_path = os.path.join(download_folder, '{}.zip'.format(date))
        os.rename(os.path.join(download_folder, 'temp.zip'), file_path)

        print("Download completed.")
        return True
    else:
        print("Download failed.")
        return False

def main(start_date, end_date=None):
    # Case 1:  searching for all days in a month
    if len(start_date) == 6:
        start_date += '01'
    current_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()

    # Case 2: Range Serach, end_date = None 이라면 모든 일 검색
    if end_date:
        last_date = datetime.datetime.strptime(end_date, '%Y%m%d').date()
    else:
        last_date = current_date.replace(day=1) + datetime.timedelta(days=32)
        last_date = last_date - datetime.timedelta(days=last_date.day)

    # File path 다이얼로그
    app = QApplication(sys.argv)
    download_folder = QFileDialog.getExistingDirectory(
        None, "저장위치", options=QFileDialog.ShowDirsOnly)

    while current_date <= last_date:
        current_date_str = current_date.strftime('%Y%m%d')
        if search_data(current_date_str):
            download_data(current_date_str, download_folder)
        current_date += datetime.timedelta(days=1)

    app.quit()

if __name__ == '__main__':
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        sys.exit(1)

    start_date = sys.argv[1]
    end_date = sys.argv[2] if len(sys.argv) == 3 else None

    main(start_date, end_date)