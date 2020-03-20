# Ptt_scrapy
## 流程大綱
![image](https://im6.ezgif.com/tmp/ezgif-6-a96f622186ce.gif)<br><br>
公會長:負責下日期。<br><br>
副會長:會隔一段時間不斷的去抓各個看板的新頁數。<br><br>
幹部:去資料庫(頁數)拿資料, 在開始爬日期內所有文章的網址, 寫到資料庫(任務)。<br><br>
櫃台小姐:任務看板, 可以有多名冒險者(其他電腦)領取任務的網址爬文章。<br><br>
![image](https://im6.ezgif.com/tmp/ezgif-6-9047f1085401.gif)<br><br>
如果抓資料失敗會將抓失敗的網址與失敗的狀態寫入資料庫。<br><br>

## MongoDB雲端開發, 所以以雲端Mongodb為例。
### [MongoDB雲端網頁](https://account.mongodb.com/account/login)<br><br>
點擊以下圖片連結影片教學。<br><br>
[![image](https://i.imgur.com/hJoWWMv.png)](https://drive.google.com/open?id=1mKID7gVvBlrk-1Wr5Gd5XwscDbbtg7nA)<br><br>
有了雲端資料庫後, 開起 main.py 設定想要爬的日期(YYYY-MM-DD), 目前還沒做防呆請輸入正確 !
