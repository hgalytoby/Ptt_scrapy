import time
import asyncio
import aiohttp
import pymongo
import datetime
import ptt_tools
from bs4 import BeautifulSoup


class Ptt:
    def __init__(self, start_date, end_date, db_client):
        """
        client: mongodb 資料庫。
        start_date: 日期初。
        end_date: 日期尾。
        """
        self.client = db_client
        self.start_date = start_date
        self.end_date = end_date
        self.start_date_unix = None
        self.end_date_unix = None
        self.today_new_page = {}
        self.total_title_data = None

    def process_date_unix(self):
        """
        任務：
            將指定時間初及尾轉成 unix 時間。
        """
        self.start_date = datetime.datetime.strptime(self.start_date, '%Y-%m-%d')
        self.end_date = datetime.datetime.strptime(self.end_date, '%Y-%m-%d')
        self.start_date_unix = int(str(int(time.mktime(self.start_date.timetuple()))))
        self.end_date = self.end_date + datetime.timedelta(days=1)
        self.end_date_unix = int(str(int(time.mktime(self.end_date.timetuple()))))

    def get_ppt_title_data(self, write_title_data=False, write_today_update=False):
        """
        任務:
            獲取 Ptt 上的所有看板資料 。

        參數:
            write_title_data: 更新資料庫資料(看板)。
            write_today_update: 更新資料庫(今天的看板最新頁數資料)。

        調用自己寫的功能:
            asyncio.run(self.run())　一次取得所有看板最新的一頁。

        各定意功能:
            total: 看板數量。
        """
        if write_title_data:
            self.total_title_data = ptt_tools.ptt_class_title_data(result=[])
            self.write_mongodb_class_title()

        if write_today_update:
            self.total_title_data = ptt_tools.ptt_class_title_data(result={})

            total = len(self.total_title_data)
            while True:
                asyncio.run(self.run())
                # 因為一次向全部的看板發送請求, 可能會發生無回應, 所以獲取資料的長度沒有等於看板數量的話, 在重抓一次。
                if len(self.today_new_page) == total:
                    print(len(self.today_new_page))
                    break
            self.write_mongodb_today_page()

    def start_mission_search_page(self, ptt_class: list = ''):
        """
        任務:
            搜尋看板指定天數內的其中一頁的頁數。

        參數:
            ptt_class: 給 Ptt 看板名稱(list), 如果沒給看板名稱, 預設爬全部看板。

        調用自己寫的功能:
            ptt_tools.get_class_index_url() 搜尋看板指定天數內的其中一頁的頁數。
            self.start_mission_search_article_url() 搜尋看板指定天數所有的文章。

        各定意功能:
            db: 連到資料庫。
            collect: 指定資料庫集合。
            mission_page: 看板與指定日期其中一頁的字典。(key:看板名稱, value:頁數)
            now_total_class_new_page: Ptt_today_page 的資料庫找今天最新看板的頁數。
            mission_class: 指定看板的字典, 如果沒指定就是全部看板的字典。
            page: 切出最新看板的頁數 url 的頁數。
            data: 指定日期其中一頁的頁數。
        """
        db = self.client['Ptt_today_page']
        collect = db['Today']
        mission_page = {}
        for i in collect.find({}, {'_id': False}):
            now_total_class_new_page = i

        if len(ptt_class) is 0:
            mission_class = now_total_class_new_page
        else:
            mission_class = {}
            for i in ptt_class:
                if i in now_total_class_new_page:
                    for key in ptt_class:
                        mission_class.update({key: now_total_class_new_page[key]})

        for key, value in mission_class.items():
            page = int(value.split(f'{key}/index')[1].split('.')[0])
            data = ptt_tools.get_class_index_url(start_time=self.start_date_unix,
                                                 end_time=self.end_date_unix, key=key,
                                                 page=page, max_page=page)
            mission_page.update({key: data})

        print('爬所有看板 指定時間內的所有文章url')
        self.start_mission_search_article_url(mission_page)

    def start_mission_search_article_url(self, mission_page: dict):
        """
        任務:
            搜尋看板指定時間內所有文章的 url 寫入任務資料庫。

        參數:
            mission_page: 給看板名稱與指定時間內其中一頁頁數的字典。(Key:看板名稱, value:頁數)

        調用自己寫的功能:
            ptt_tools.mission_page_scrapy() 抓所有符合日期範圍內的文章 url。
            self.write_mongodb_mission_date_url() 寫入任務資料庫。

        各定意功能:
            data: 所有符合日期的 url 的 list。
        """
        for key, value in mission_page.items():
            if str(value).isdigit():
                print(key)
                data = ptt_tools.mission_page_scrapy(start_time=self.start_date_unix,
                                                     end_time=self.end_date_unix, key=key,
                                                     page=value)
                self.write_mongodb_mission_date_url(key=key, data=data)
            else:
                print(key, value)

    def start_mission(self, mission_list: list = ''):
        """
        任務:
            拿資料庫(任務), 寫入資料庫(文章)。

        參數:
            mission_list: 給 Ptt 看板名稱(list), 查看資料庫(任務)有沒有此看板名稱的任務, 預設執行查看資料庫(任務)全部任務。

        調用自己寫的功能:
            self.write_mongodb_class_article_content() 成功獲取文章, 寫入資料庫(文章)。
            self.write_mongodb_class_article_error() 失敗獲取文章, 寫入資料庫(錯誤)。

        各定意功能:
            View_class_name_db: 連接資料庫(看板資料)。
            View_collect: 查看看板資料。
            mission_list: 任務的 list。
            mission_db: 連接資料庫(任務)。
            get_mission_collect: 指定任務資料庫的集合。
            mission_dict: 執行任務的字典。(key:看板名稱, valse:[任務 url,])。
            error_list: 拿文章失敗的 list。
            data: 文章資料。
            process_error: 處理拿文章失敗的字典。
            error_stats: for 迴圈, 失敗的情況是什麼。
        """
        mission_dict = {}
        if len(mission_list) is 0:
            View_class_name_db = self.client['Ptt_title']
            View_collect = View_class_name_db['title']
            mission_list = []
            for i in View_collect.find({}, {'_id': False, 'url': False, 'class': False}):
                mission_list.append(i['name'])

        for key in mission_list:
            mission_db = self.client['Ptt_get_mission_url']
            get_mission_collect = mission_db[key]
            for mission in get_mission_collect.find({}, {'_id': False}):
                mission_dict.update({key: mission['mission']})

        for key, value in mission_dict.items():
            error_list = []
            for url in value:
                print(url)
                data = ptt_tools.get_article_text_data(url=url, key=key)
                if type(data) is dict:
                    self.write_mongodb_class_article_content(key=key, data=data)
                else:
                    error_list += data
            print(len(value), key, value)
            if len(error_list) > 0:
                process_error = {}
                # error_list = [{'error_1': [url1]}, {'error': [url2]}, {'error': [url3]}]
                #                                   ↓
                #  error_list = [{'error_1': [url1]}, {'error': [url2, url3]}]
                for error in error_list:
                    for error_stats in error:
                        if error_stats in process_error:
                            process_error[error_stats] += error[error_stats]
                        else:
                            process_error.update(error)
                self.write_mongodb_class_article_error(key=key, error=process_error)

    def write_mongodb_class_title(self):
        """
        任務:
            更新資料庫(看板), 已有的資料不寫入。

        各定意功能:
            db: 連接資料庫。
            collect: 指定集合。
        """
        db = self.client['Ptt_title']
        collect = db['title']
        collect.create_index([('url', pymongo.ASCENDING)], unique=True)
        for i in self.total_title_data:
            try:
                collect.insert_one(i)
                print('新增class_title')
            except pymongo.errors.DuplicateKeyError:
                print('已存在')

    def write_mongodb_class_article_error(self, key, error: dict):
        """
        任務:
            更新資料庫(錯誤), 如果已經有資料, 將新的錯誤與就的錯誤合併。

        參數:
            key: 看板名稱。
            error: 要更新的錯誤字典。(key:錯誤狀態, value: [錯誤的url,])

        各定意功能:
            db: 連接資料庫。
            collect: 指定集合。
            data: 資料庫現在錯誤的資料。
        """
        db = self.client['Ptt_article_error']
        collect = db[key]
        data = {}
        for i in collect.find({}, {'_id': False}):
            data = i
        if len(data) is 0:
            collect.insert_one(error)
        else:
            for i in data:
                if i in error:
                    error[i] += data[i]
                    error[i] = list(set(error[i]))
            collect.update_many(data, {'$set': error})

    def write_mongodb_today_page(self):
        """
        任務:
            更新資料庫(今天看板最新頁數), 如果已經有資料, 更新資料。

        各定意功能:
            db: 連接資料庫。
            collect: 指定集合。
            data: 資料庫現在錯誤的資料。
        """
        db = self.client['Ptt_today_page']
        collect = db['Today']
        data = {}
        for i in collect.find():
            data.update(i)
        if len(data) is 0:
            collect.insert_one(self.today_new_page)
        else:
            print('更新今天新頁數')
            collect.update_many(data, {'$set': self.today_new_page})

    def write_mongodb_class_article_content(self, key, data):
        """
        任務:
            更新資料庫(文章)。

        參數:
            key: 看板名稱。
            data: 任務。(key:錯誤狀態, value: [錯誤的url,])

        各定意功能:
            db: 連接資料庫。
            collect: 指定集合。
        """
        db = self.client['Ptt_class_content']
        collect = db[key]
        collect.create_index([('canonicalUrl', pymongo.ASCENDING)], unique=True)
        try:
            collect.insert_one(data)
        except pymongo.errors.DuplicateKeyError:
            print('已存在內文')

    def write_mongodb_mission_date_url(self, key, data):
        """
        任務:
            更新資料庫(任務), 如果已經有資料, 將舊的資料與新的資料合併。

        參數:
            key: 看板名稱。
            data: 任務。(key: mission, value: [url,])

        各定意功能:
            db: 連接資料庫。
            collect: 指定集合。
            mission_list: 取出現在資料庫資料(任務)。
        """
        db = self.client['Ptt_get_mission_url']
        collect = db[key]
        mission_list = {}
        for i in collect.find({}, {'id': False}):
            mission_list.update(i)
        if len(mission_list) > 0:
            data += mission_list['mission']
            data = list(set(data))
            collect.update_one(mission_list, {'$set': {'mission': data}})
        else:
            collect.insert_one({'mission': data})

    async def run(self):
        """
        任務:
            執行 tasks 的任務。

        調用自己寫的功能:
            self.request_page()。

        各定意功能:
            放任務的 list。
        """
        tasks = []
        for key, value in self.total_title_data.items():
            tasks.append(asyncio.create_task(self.request_page(key)))
        await asyncio.wait(tasks, timeout=10)
        await asyncio.sleep(0)

    async def request_page(self, class_name):
        """
        任務:
            獲取所有看板最新的網頁。

        參數:
            class_name: 看板名稱。

        各定意功能:
            url: 看板的首頁。
            header: 標投。
            cookie: 滿 18歲的 cookie。
            res: 網頁資料。
            page: 抓最新的頁數。
            page_url: 最新頁數的 url。
            self.today_new_page: 裝看板名稱跟最新 url 的字典。{key:看板名稱, value:看板最新網址}
        """
        async with aiohttp.ClientSession() as session:
            url = f'https://www.ptt.cc/bbs/{class_name}/index.html'
            header = {'User-Agent': ptt_tools.user_agent_list()}
            cookie = {'over18': '1'}
            async with session.get(url=url, headers=header, cookies=cookie) as res:
                res = await res.text(encoding='utf-8', errors='ignore')
                html = BeautifulSoup(res, 'html.parser')
                page = str(int(html.find_all('a', class_='btn wide')[1]['href'].split('index')[1].split('.')[0]) + 1)
                page_url = f'https://www.ptt.cc/bbs/{class_name}/index{page}.html'
                self.today_new_page.update({class_name: page_url})


if __name__ == '__main__':
    # 已 mongodb 為例:
    # 363 ~ 364 行是我的雲端mongodb資料庫。
    # db_client = pymongo.MongoClient(
    #     'mongodb+srv://<username>:<password>@dudulu-p5zz0.gcp.mongodb.net/test?retryWrites=true&w=majority')
    # 輸入mongodb資料庫。
    db_client = pymongo.MongoClient()

    # 輸入日期初與日期尾 YYYY-MM-DD。
    ptt = Ptt(start_date='2020-3-10', end_date='2020-3-16', db_client=db_client)

    # 將時間轉成 unix。
    ptt.process_date_unix()

    # 更新看板資料或更新今天最新日期, 如果是完全乾淨的資料庫, 請 write_title_data 和 write_today_update 都設為True。
    ptt.get_ppt_title_data(write_title_data=True, write_today_update=True)

    # 如果雲端資料庫已經有看板資料與今日看板最新頁資料, 可以不用做373行。
    # 給 Ptt 看板名稱(list), 如果沒給看板名稱, 預設爬全部看板。
    ptt.start_mission_search_page()

    # 給看板名稱與指定時間內其中一頁頁數的字典。(Key:看板名稱, value:頁數)
    ptt.start_mission()
