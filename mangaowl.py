import requests as rq
from bs4 import BeautifulSoup
import os
import time

'''
mangaowl.net爬蟲用
Date : 2022/04/19
Step1. 進入漫畫閱覽模式
Step2. 選擇所需的章節
Step3. F12 Source找到html檔，全選複製放在同目錄，檔名為下載後的資料夾名
Step4. 執行程式，直接連到圖片地址下載

Tip1. 這個網站被cloudflare保護，也有其他限制，所以不爬直接手動載html
Tip2. html檔中就有每張圖片的地址了，而且完全沒保護
'''

htmls = os.listdir(os.getcwd())

FIRST = True

for html in htmls:
	if not html.endswith("html"):
		continue
	if FIRST:
		os.mkdir(html[:-5])
		FIRST = False
		
	rf = open(html, "r", encoding = "utf8")
	soup = BeautifulSoup(rf, "lxml")
	img_tags = soup.find_all("img", class_ = "owl-lazy")
	
	urls = list(map(lambda x: x["data-src"], img_tags))
	
	for i in range(len(urls)):
		jpg = rq.get(urls[i])
		with open(f"./{html[:-5]}/{i+1}.jpg", "wb") as wf:
			wf.write(jpg.content)
		time.sleep(2)
	FIRST = True