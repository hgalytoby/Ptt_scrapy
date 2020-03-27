import time
import random
import datetime
import requests
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta


def user_agent_list():
    """
    任務：
        隨機拿header的 User-Agent。

    各定意功能:
        user_list: 各個 User-Agent的資料。
        result: 隨機抓出一個 User-Agent。

    回傳:
        User-Agent。(str)
    """
    user_list = [
        "Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19",
        "Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
        "Mozilla/5.0 (Linux; U; Android 2.2; en-gb; GT-P1000 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
        "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0",
        "Mozilla/5.0 (Android; Mobile; rv:14.0) Gecko/14.0 Firefox/14.0",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"
    ]
    result = random.choice(user_list)
    return result


def ptt_class_title_data(result: list or dict):
    """
    任務:
        取得各看板最新頁數。

    參數:
        result: 判斷是 list 還是 dict, 如果是 list 增加資料得用 append, 如果是 dict 增加資料得用 update。

    各定意功能:
        url: Ptt 所有看板的 rul。
        header: 標頭。
        res: 取得網址資料。
        html: 將 res 轉成 BeautifulSoup型態。
        board: 看板資料區塊。

    回傳:
        所有看板的最新頁數的資料。(dict or list)
    """
    url = 'https://www.ptt.cc/bbs/hotboards.html'
    header = {'User-Agent': user_agent_list()}
    res = requests.get(url=url, headers=header).text
    html = BeautifulSoup(res, features='lxml')
    board = html.find_all('a', class_='board')
    for i in board:
        for board_name in i.find('div', class_='board-name'):
            name = board_name
        for board_class in i.find('div', class_='board-class'):
            class_ = board_class
        total_title_data = {
            'url': f'https://www.ptt.cc/bbs/{name}/index.html',
            'name': name,
            'class': class_,
        }
        if type(result) is dict:
            result.update({name: total_title_data})
        else:
            result.append(total_title_data)
    return result


def get_article_text_data(url: str, key: str):
    """
    任務:
        抓大部分正常的文章內文。

    參數:
        url: Ptt文章的網址。
        key: 看板名稱。

    調用其他方法:
        process_authorName() 處理無 authorName時的問題
        process_comment() 抓回文人資料。

    各定意功能:
        cookie: 滿 18歲的 cookie。
        header: 標頭。
        res: 網頁資料。
        html: 轉成 BeautifulSoup 型態。
        title: 取得文章標題。
        get_content: 切割 html 只拿作者內容的網頁資料。
        conect: 取得內文。
        pubishedTime: 取得 unix 時間。
        get_text_data: 放資料的字典。
        commentContent: 抓回文人的區塊資料。
        error: 錯誤訊息

    問題:
        1.https://www.ptt.cc/bbs/Stock/M.1583828728.A.656.html, 此網頁作者只有 authorld, 沒有 authorName, 所以要空著還是用 authorld 補?

    回傳:
        此文頁所有需要的資料(dict)。
        發生 error 的資料。(list)
    """
    try:
        cookie = {'over18': '1'}
        header = {'User-Agent': user_agent_list()}
        res = requests.get(url=url, headers=header, cookies=cookie).text
        html = BeautifulSoup(res, features='lxml')
        title = html.find_all('span', class_='article-meta-value')
        get_content = html.find('div', id='main-content')
        # 切割文章作者內文, 如果※ 發信站: 批踢踢實業坊(ptt.cc)不在網頁裡面, 代表此網頁不一般。
        if '※ 發信站: 批踢踢實業坊(ptt.cc)' in get_content.text:
            # 如果這裡發生錯誤, 可能是作者發文後有做編輯, 需另外處理。
            try:
                conect = '\n'.join(str(get_content.text).split('--\n※ 發信站: 批踢踢實業坊(ptt.cc)')[0].split('\n')[1:])
                commentContent = str(get_content).split('※ 發信站: 批踢踢實業坊(ptt.cc)')[1]
                commentContent = BeautifulSoup(commentContent, features='lxml')
                pubishedTime = int(url.split(key)[1].split('.')[1])
                get_text_data = {
                    'authorld': title[0].text.split('(')[0].strip(),
                    'authorName': process_author_name(title[0].text),
                    'title:': title[2].text,
                    'publishedTime': pubishedTime,
                    'conent': conect,
                    'canonicalUrl': url,
                    'createdTime': datetime.datetime.today(),
                    'updataTime': datetime.datetime.today(),
                    'comment': process_comment(html=commentContent, commentTime=pubishedTime)
                }
                return get_text_data
            # 返回錯誤的網站與錯誤訊息
            except IndexError as error:
                print(url, error, '---------此網頁有問題-------')
                return [{'list_out': [url]}]
        print(url, '---------此網頁有問題-------')
        # 返回錯誤的網站與錯誤訊息
        return [{'未定義error': [url]}]
    except:
        print(url, '---------此網頁有問題-------')
        # 返回錯誤的網站與錯誤訊息
        return [{'未定義error': [url]}]



def process_author_name(authorName):
    """
    任務:
        處理文章作者名字, 確認作者是否只有 authorld, 沒有 authorName。

    參數:
        authorName: 作者名字資料。

    回傳:
        沒有 authorName 返回空字串, 有 authorName 返回 authorName。
    """
    if authorName[-1] is ')' and '(' in authorName:
        return authorName.split('(')[-1].replace(')', '')
    return ''


def process_comment(html: BeautifulSoup, commentTime: int):
    """
    任務：
        抓內文回文的資料, 回傳字典。

    參數:
        html: 回文人的區塊網頁資料。
        commentTime: 文章 unix 時間。

    調用其他方法:
        process_time() 因網頁回文沒有年份, 所以我抓文章的網址的年份再丟進 process_time 方法處理時間。

    各定意功能:
        comment: 只抓回文人的資料。
        comment_data:  儲存資料字典。
        commentTime: 處理回文人的時間。
        pending_time: 抓出回文人的日期。
        people: 因要知道這篇文章多少個人回應, 記住斷樓次數。
        for i, m in enumerate(comment):  i = 第幾個人, m = 資料。

    回傳:
        全部回文人的資料。(dict)
        comment_data: {
                        commentId:　回文人 ID,
                        commentContent:　回文人內容,
                        commentTime:　回文人時間
                      }
    """

    comment = html.find_all('div', class_='push')
    comment_data = {}
    people = 0
    for i, m in enumerate(comment):
        pending_time = m.find('span', class_='push-ipdatetime')
        # 因抓取區塊的該層樓, 沒有日期
        if pending_time is None:
            people += 1
            continue
        # tag = m.find('span', class_='push-tag').text  # <---- 抓 (推 →) 暫時用不到。
        pending_time = ' '.join(m.find('span', class_='push-ipdatetime').text.split(' ')[-2:]).replace('\n', '')
        commentTime = process_time(now_time=commentTime, pending_time=pending_time)
        comment_data.update(
            {
                str(i + 1 - people): {
                    'commentId': str(m.find('span', class_='f3 hl push-userid').text).strip(),
                    'commentContent': m.find('span', class_='push-content').text[2:],
                    'commentTime': commentTime
                }
            }
        )
    return comment_data


def process_time(now_time, pending_time):
    """
    任務：
        處理內文回文人的時間。

    參數:
        now: 文章時間。
        pending_time: 回文人的日期。

    各定意功能:
        now_time: 將 unix 時間轉成 年/月/日。
        comment_Time: 將回文人的時間補上年後 -> 轉成 datetime 型態後 -> 轉成 unix 時間。

    問題:
        1.
        因考慮到發文者是 2020/12/31 23:59:59, 回文人是2021/1/1 00:00:00。
        如果不做處理會變成 2020/01/01, 所以要判斷月份, 如果小於發文者年要 +1。
        但如果回文者是兩年後, 現在想不出方法解決,  所以存在此BUG。

        2.
        https://www.ptt.cc/bbs/Stock/M.1583936450.A.05C.html, 此頁回文五樓回文者的時間因作者回應沒顯示
        https://www.ptt.cc/bbs/WomenTalk/M.1584281773.A.C86.html, 推 kissung: 哈哈哈 03/16 00：5", 這樓時間的分鐘出問題。
                                                                  → a27647535: 不就一直糾纏人家不想理你還把人家講得這麼難聽 03/ ,這樓只剩下月份。
                                                                  噓 palmpeas: 要發幾次啦 D03/16 20:0 這樓時間的有英文且分鐘出問題。
        當時間形態有問題, 先暫時逞裡成 抓上一層樓回文人的時間, 如果第一樓出問題就抓發文人的時間。

    回傳:
        unix時間。(int)
    """
    now_time = datetime.datetime.fromtimestamp(now_time)
    comment_Time = f'{now_time.year} {pending_time}'  # 第一次將文章的年補進去, 之後都是抓上一個人的年。
    # 判斷時間格式。
    try:
        comment_Time = datetime.datetime.strptime(comment_Time, '%Y %m/%d %H:%M')

    except ValueError:
        # 將此人時間改成上一人時間。
        comment_Time = str(now_time)
        comment_Time = datetime.datetime.strptime(comment_Time, '%Y-%m-%d %H:%M:%S')
    # 判斷是否在 12/31 ~ 隔年 1/1。
    if now_time.month > comment_Time.month:
        comment_Time += relativedelta(years=+1)
    comment_Time = int(time.mktime(datetime.datetime.timetuple(comment_Time)))
    return comment_Time


def get_popularity(html):
    """
    任務：
        抓人氣值。

    參數:
        html: 進版後的網頁資料。

    回傳:
        人氣值, 如果都沒有人氣, 返回0。(str)
    """
    for nrec in html.find('div', class_='nrec'):
        if len(nrec) is not 0:
            return nrec.text
    return '0'


def get_class_index_url(start_time=None, end_time=None, key=None, page=None, max_page=None):
    """
    任務:
        抓指定日期內的頁數。

    參數:
        start_time: 指定日期初 unix 時間。
        end_time: 指定日期尾 unix 時間。
        key: 看板名稱。
        page: 從哪一頁開始。
        max_page: 限制最高頁數。

    調用其他方法:
        get_html() 抓網頁資料。

    各定意功能:
        m_page: 變數的最大頁數值,用來限制每次往前推頁數後, 往後爬太久以及更新最大頁數。
        html :取得網頁資料。
        unix_data: 佔存網頁所有文章的unix時間的list。
        tmp_page: 上一頁。
        tmp_html: 取得上一頁資料。
        tmp_unix_data: 放unix的list。

    回傳:
        如果指定日期有資料回傳 url。(list)
        如果沒有資料回傳狀況。(str)
    """
    print('start_time =', start_time, 'end_time =', end_time, 'max_page =', max_page, 'now_page =', page, 'key =', key)
    m_page = max_page
    html = get_html(key=key, page=page)
    unix_data = []
    for i in html:  # 抓出所有文章 unix 存到unix_data裡。
        if i.find('a') is not None:
            unix = int(str(i.find('a')['href']).split(key)[1].split('.')[1])
            unix_data.append(unix)

    for unix in unix_data:  # 當發現 unix_data 裡的時間 再指定日期內 回傳 頁數。
        if start_time < unix < end_time:
            print('出來了', 'page', page, 'key', key)
            return page

    if max_page <= 1 or page <= 1:  # 跑到看板第一頁了 指定日期內 沒有任何文章。
        return '日期到最第一頁沒範圍內文章'

    # 避免發生 整頁無 url 例如:本頁只有版規, 或者 整頁都已刪文。
    # 為了避免這個問題發生,  page-1 從上一頁開始, max_page-1 不要再爬這一頁。
    # 如果直接 max_page-1, 可能會在尋找指定日期時發生問題。
    # 例如 max_page=3000, page=1500, 指定日期的文章只有在2999頁才有其餘都沒有。
    # 1500頁發生全刪文, 沒資料所以 page 與 max_pag e都-1, 現在 page=1499, max_page=2999。
    # 1499頁也是全刪文, 沒資料所以 page 與 max_page 都-1, 現在 page=1499, max_page=2998。
    # 這樣爬蟲爬下去遲早會顯示沒有這日期的文章, 為了避免亂扣 max_page 導致有文章變成沒文章。
    # 所以在扣 max_page 時, 得先檢查上一頁的文章有沒有小於 end_time, 如果有就-1, 如果沒有就不減。
    if len(unix_data) is 0:
        tmp_page = max_page - 1
        tmp_html = get_html(key, tmp_page)
        tmp_unix_data = []
        # 將該網頁所有 url 的 unix 放入 tmp_unix_data 。
        for i in tmp_html:
            if i.find('a') is not None:
                tmp_unix_data.append(int(str(i.find('a')['href']).split(key)[1].split('.')[1]))

        # 判斷 tmp_unix_data 是否有值, 如果有值且在指定範圍內, 回傳 tmp_page, 如果沒有 max_page-1。
        if len(tmp_unix_data) > 0:
            for i in tmp_unix_data:
                if start_time < i < end_time:
                    return tmp_page
            max_page -= 1
        return get_class_index_url(start_time=start_time, end_time=end_time, key=key, page=page - 1,
                                   max_page=max_page)  # 再叫自己方法, 在搜索。

    # 抓unix_data第一個值 判斷 是否在範圍日期內。
    for unix in unix_data:
        # 如果 unix 大於 end_time, m_page=更新最高頁數。
        if unix > end_time:
            m_page = page
            # 往前推頁數, 如看板最新頁page太高, 扣掉page的1成, 如果太少就除2去尾數。
            if page * 0.1 > 10:
                page -= int(page * 0.1)
            else:
                page -= page // 2
            return get_class_index_url(start_time=start_time, end_time=end_time, key=key, page=page,
                                       max_page=m_page)  # 再叫自己方法, 在搜索。
        # 如果 unix 小於 start_time, p_page = 經處理後的往後推的頁數, p = 要加的頁數。
        # 如果頁數太大, 在往後推的頁數時會發生頁數大於最大頁數時, 將要加的數字在除2, 值到不超過最大頁數。
        # 例子:
        # 最大頁數: 4000 現在頁數:3000
        # 3000 + (3000 - 3000 // 2)
        # = 3000 + (3000 - 1500)
        # = 3000 + 1500
        # = 4500
        elif unix < start_time:
            p_page = page + (page - page // 2)
            # 因例子3000 + 1500 超過最大頁數 4500, 所以 1500 // 2 = 750。
            if p_page > max_page:
                p = (page - page // 2) // 2

                while True:
                    p = p // 2
                    print('page', page, 'p', p)
                    # 3000 + 750 < 最大頁數, 將 page 更新成3750。
                    if page + p < max_page:
                        # 如果 p = 0 代表從頭跑到尾巴都沒文章, 所以指定日期內沒文章。
                        if p is 0:
                            return '指定日期沒文章'
                        page += p
                        break

            else:
                page = p_page
            return get_class_index_url(start_time=start_time, end_time=end_time, key=key, page=page,
                                       max_page=m_page)  # 再叫自己方法, 在搜索。


def get_html(key, page):
    """
    任務:
        切掉公告與版規區塊, 回傳文章區塊的資料。

    參數:
        key: 看板名稱。
        page: 從哪一頁開始。

    調用其他方法:
        user_agent_list() 隨機抓 header 的 User-Agent 。

    各定意功能:
        url: Ptt進版後網址。
        cookie: 滿18歲的 cookie。
        header: 標頭。
        res: 抓網頁資料。
        html: 將 res 轉成 BeautifulSoup型態。

    回傳:
        切割版規後的網頁資料。(str)
    """
    url = f'https://www.ptt.cc/bbs/{key}/index{page}.html'
    cookie = {'over18': '1'}
    header = {'User-Agent': user_agent_list()}
    res = requests.get(url=url, headers=header, cookies=cookie).text
    if '<div class="r-list-sep"></div>' in res:
        res = res.split('<div class="r-list-sep"></div>')[0]
    html = BeautifulSoup(res, features='lxml')
    return html.find_all('div', class_='r-ent')


def mission_page_scrapy(start_time=None, end_time=None, key=None, page=None):
    """
    任務:
        抓現在此網頁的所有符合日期範圍內的文章 url, 接著判斷要往前爬 or 往後爬 or 前後都爬。

    參數:
        start_time: 指定日期初 unix 時間。
        end_time: 指定日期尾 unix 時間。
        key: 看板名稱。
        page: 從哪一頁開始。

    調用其他方法:
        get_html() 抓網頁資料。

    各定意功能:
        html: 抓網頁資料。
        unix: 定義 unix 只是讓程式不亮燈 什麼值都可以。
        result: 將所有時間內的文章 url 放入 result。
        start_page: 因為要往前爬 + 往後爬, 所以要定義往前 page。
        end_page: 因為要往前爬 + 往後爬, 所以要定義往後的 page。

    回傳:
        符合日期範圍內的 url。(list)
    """
    html = get_html(key=key, page=page)
    unix = 0
    result = []

    # 抓頁面第一筆 url 當作判斷要往前爬還是往後爬就可以退出 for 迴圈。
    for i in html:
        if i.find('a') is not None:
            unix = int(str(i.find('a')['href']).split(key)[1].split('.')[1])
            break

    # 如果該網頁的第一筆 unix 小於開始時間, 就往後開始爬, 爬到沒資料就退出。
    if unix < start_time:
        result += get_now_html_article_url(start_time=start_time, end_time=end_time, key=key,
                                           html=html)  # 先將此網頁符合日期範圍的 url 新增至 result。

        while True:
            page += 1  # 往後爬。
            html = get_html(key=key, page=page)  # 抓網頁資料。
            page_result = get_now_html_article_url(start_time=start_time, end_time=end_time, key=key,
                                                   html=html)  # 抓符合日期內的文章 url。

            if len(page_result) is 0:  # 如果沒資料就退出。
                break
            result += page_result  # 將抓到的 url 加到 result。

    elif unix > end_time:  # 如果該網頁的第一筆 unix 大於開始時間, 就往前開始爬, 爬到沒資料就退出, 但應該不會用到這個判斷, 只是保險。
        result += get_now_html_article_url(start_time=start_time, end_time=end_time, key=key,
                                           html=html)  # 先將此網頁符合日期範圍的 url 新增至 result。

        while True:
            page -= 1  # 往前爬。
            html = get_html(key=key, page=page)  # 抓網頁資料。
            page_result = get_now_html_article_url(start_time=start_time, end_time=end_time, key=key,
                                                   html=html)  # 抓符合日期內的文章 url。
            if len(page_result) is 0:  # 如果沒資料就退出。
                break
            result += page_result  # 將抓到的 url 加到 result。

    elif start_time < unix < end_time:  # 如果該網頁的第一筆在開始時間 < unix < 結束時間內就前後開始爬, 爬到沒資料就退出。
        result += get_now_html_article_url(start_time=start_time, end_time=end_time, key=key,
                                           html=html)  # 先將此網頁符合日期範圍的 url 新增至 result。
        start_page = page
        end_page = page

        while True:
            end_page += 1  # 往後爬。
            html = get_html(key=key, page=end_page)  # 抓網頁資料。
            page_result = get_now_html_article_url(start_time=start_time, end_time=end_time, key=key,
                                                   html=html)  # 抓符合日期內的文章 url。
            if len(page_result) is 0:  # 如果沒資料就退出。
                break
            result += page_result  # 將抓到的 url 加到 result。

        while True:
            start_page -= 1  # 往前爬。
            html = get_html(key=key, page=start_page)  # 抓網頁資料。
            page_result = get_now_html_article_url(start_time=start_time, end_time=end_time, key=key,
                                                   html=html)  # 抓符合日期內的文章 url。
            if len(page_result) is 0:  # 如果沒資料就退出。
                break
            result += page_result  # 將抓到的 url 加到 result。
    print(key, len(result), result)
    return result


def get_now_html_article_url(start_time=None, end_time=None, key=None, html=None):
    """
    任務:
        此網頁所有在日期範圍內的文章 url 抓出來。

    參數:
        start_time: 指定日期初 unix 時間。
        end_time: 指定日期尾 unix 時間。
        key: 看板名稱。
        html: Ptt 進版網址。

    各定意功能:
        get: 取得文章的 unix。
        result: 裝 url 的 list。

    回傳:
        網頁內所有文章符合指令日期的 url。(list)
    """
    result = []

    for i in html:
        if i.find('a') is not None:
            get = int(str(i.find('a')['href']).split(key)[1].split('.')[1])
            if start_time < get < end_time:  # 時間內全部加到result內
                result.append(f"https://www.ptt.cc{i.find('a')['href']}")
    return result


if __name__ == '__main__':
    pass
