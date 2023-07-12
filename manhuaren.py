from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import requests as rq
import time

'''
manhuaren用，方法似manhuagui，但首次進入爬取頁面時會有全頻廣告需手動關閉
2022/04/20
'''

def prepare_sele(unseen):
	global driver, headers
	print("準備瀏覽器中...")
	firefox_path = "D:/mypython/Selenium_firefox/firefox/firefox.exe"
	webdriver_path = "D:/mypython/Selenium_firefox/geckodriver.exe"
	binary = FirefoxBinary(firefox_path)
	opts = Options()
	if unseen:
		opts.headless = True
	
	driver = webdriver.Firefox(options=opts,executable_path=webdriver_path,firefox_binary=binary)
	headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0", "referer":"https://www.manhuaren.com/m98576/"}
	print("準備完成")
	return driver, headers

driver, headers = prepare_sele(0)
driver.get("https://www.manhuaren.com/m98576/")
time.sleep(3)
for i in range(4):
	pic = driver.find_element(By.CLASS_NAME, "lazy")
	url = pic.get_attribute("src")
	a = rq.get(url, headers = headers)
	with open(f"{i+1}.jpg", "wb") as f:
		f.write(a.content)
	next_page = driver.find_element(By.XPATH, "/html/body/ul/li[3]/a")
	driver.execute_script("arguments[0].click();", next_page)
	time.sleep(1.3)
driver.quit()