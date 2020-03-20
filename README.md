# Ptt_scrapy
## 流程大綱
![image](https://i.imgur.com/s6n4kqC.gif)<br><br>
公會長:負責下日期。<br><br>
副會長:會隔一段時間不斷的去抓各個看板的新頁數。<br><br>
請將額外開一個 main.py 將 375 行改成(預設一小時抓一次)<br><br>
while True:<br><br>
　　　ptt.get_ppt_title_data(write_title_data=False, write_today_update=True)<br><br>
　　　time.sleep(3600)<br><br>
幹部:去資料庫(頁數)拿資料, 在開始爬日期內所有文章的網址, 寫到資料庫(任務)。<br><br>
櫃台小姐:任務看板, 可以有多名冒險者(其他電腦)領取任務的網址爬文章。<br><br>
![image](https://i.imgur.com/zeu3Dmz.gif)<br><br>
如果抓資料失敗會將抓失敗的網址與失敗的狀態寫入資料庫。<br><br>

## MongoDB雲端開發, 所以以雲端Mongodb為例。
### [MongoDB雲端網頁](https://account.mongodb.com/account/login)<br><br>
點擊以下圖片連結影片教學。<br><br>
[![image](https://i.imgur.com/hJoWWMv.png)](https://drive.google.com/open?id=1mKID7gVvBlrk-1Wr5Gd5XwscDbbtg7nA)<br><br>
有了雲端資料庫後, 開起 main.py 設定想要爬的日期(YYYY-MM-DD), 目前還沒做防呆請輸入正確 !

## 待開發功能
目前已 Url 為標準資料庫有同樣的 Url 就不寫入, 但因每篇文章之後會有新的回文, 後續會增加更新資料的功能。<br><br>
考慮到可能做任務到一半, 發生停機的狀況, 後續會增加追朔未擷取資料的功能<br><br>
加強爬網頁速度, 開進程與線程做爬網頁的方案, 但會有發生請求過於快速且頻繁被伺服器ban調, <br><br>
目前是打算抓取免費的 IP Pool | Proxy Pool, 放到mongodb資料庫, 分配給任務的電腦, 待開發。<br><br>
