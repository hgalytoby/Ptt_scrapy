# Ptt_scrapy
## MongoDB雲端開發，所以以雲端Mongodb為例。
### [MongoDB雲端首頁](https://account.mongodb.com/account/login)<br><br>
點擊以下圖片連結影片教學。<br><br>
[![image](https://i.imgur.com/hJoWWMv.png)](https://drive.google.com/open?id=1mKID7gVvBlrk-1Wr5Gd5XwscDbbtg7nA)<br><br>
有了雲端資料庫後，開起 main.py 設定想要爬的日期(YYYY-MM-DD)，目前還沒做防呆請輸入正確 !!<br><br>

## 邏輯思維
設立一個專門更新最新頁數的，將最新的頁數上傳到雲端，當要指定爬取時間文章時，會先到最新頁數的資料庫拿最新頁數的url。<br><br>
接著在去爬日期範圍內其中一頁的頁數，將那一頁抓出來。<br><br>
因可能會遇到冷看板，可能第一筆不是在範圍日期內，所以會只往後面的頁數爬。<br><br>
如果文章在日期之間，那就會進行前後網頁都爬。<br><br>
當抓取全部日期的 url 時，會上傳到任務的資料庫。<br><br>
這樣可以不同電腦做不同的任務，當任務被某一台電腦拿走時，任務資料庫會刪除此任務。<br><br>

## 使用方法
* [下載程式碼](https://github.com/hgalytoby/Ptt_scrapy/archive/master.zip)<br><br>
* 安裝套件庫 `pip install -r requirements.txt`<br><br>
* 執行 main.py<br><br>
* 366 行 輸入 mongodb 資料庫。<br><br>
* 369 行 務必輸入日期初與日期尾以便讓之後的程式碼讀取日期 YYYY-MM-DD。<br><br>
* 375 行 更新看板資料或更新今天最新日期，如果是完全乾淨的資料庫，請 write_title_data 和 write_today_update 都設為True。<br><br>
* 379 行 如果雲端資料庫已經有看板資料與今日看板最新頁資料，可以不用做 375 行。給 Ptt 看板名稱(list), 如果沒給看板名稱，預設爬全部看板。example : `['Stock', 'Gossiping']`<br><br>
* 382 行  取得任務，給看板名稱(list)，如果沒給看板名稱，預設執行全部看板任務。example : `['Stock', 'Gossiping']`<br><br>

## 待開發功能
* 目前會隔一段時間不斷的去抓各個看板的新頁數是在本地端執行，後續會部屬到雲端上運行。<br><br>
* 已 Url 為標準資料庫有同樣的 Url 就不寫入，但因每篇文章之後會有新的回文，後續會增加更新資料的功能。<br><br>
* 當一台電腦拿任務時，該任務要從任務資料庫先清掉, 以免其他人也拿到此任務，待開發。<br><br>
* 考慮到可能做任務到一半，發生停機的狀況, 後續會增加追朔未擷取資料的功能。<br><br>
* 加強爬網頁速度，開進程與線程做爬網頁的方案, 但會發生請求過於快速且頻繁被伺服器 ban，後續打算抓取免費的 IP Pool | Proxy Pool，放到mongodb資料庫, 分配給任務的電腦，待開發。<br><br>
* 針對發生擷取錯誤網頁時該如何正確的擷取，目前是爬完一整個版才上傳全部錯誤的 Url，後續會改成當下發生錯誤就寫入資料庫待開發。<br><br>
* 解決還沒發現的Bug。
