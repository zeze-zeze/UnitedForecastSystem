import time, DAN, requests, random 
import threading, sys # for using a Thread to read keyboard INPUT

ServerURL = 'https://demo.iottalk.tw'  # with SSL secure connection
Reg_addr = None #if None, Reg_addr = MAC address #(本來在 DAN.py 要這樣做 :-) 
# Note that Reg_addr 在以下三句會被換掉! # the mac_addr in DAN.py is NOT used
mac_addr = 'CD8600D38' + str( random.randint(100,999 ) )  # put here for easy to modify :-) 
# 若希望每次執行這程式都被認為同一個 Dummy_Device, 要把上列 mac_addr 寫死, 不要用亂數。
Reg_addr = mac_addr  # Note that the mac_addr generated in DAN.py always be the same cause using UUID ! 

DAN.profile['dm_name']='Dummy_Device'   # you can change this but should also add the DM in server
DAN.profile['df_list']=['Dummy_Sensor', 'Dummy_Control']   # Check IoTtalk to see what IDF/ODF the DM has
DAN.profile['d_name']= "weather."+ str( random.randint(100,999 ) ) +"_"+ DAN.profile['dm_name'] # None
DAN.device_registration_with_retry(ServerURL, Reg_addr) 
print("dm_name is ", DAN.profile['dm_name']) ; print("Server is ", ServerURL)
# global gotInput, theInput, allDead    ## 主程式不必宣告 globel, 但寫了也 OK
gotInput=False
theInput="haha"
allDead=False
crawl=False

from bs4 import BeautifulSoup
from selenium import webdriver
import datetime

def clearLists( ):
  global date,temp,weather, wind_direction, wind_speed, gust_wind
  global visible, hum, pre, rain, sunlight
  date = []
  temp = []
  weather = []
  wind_direction = []
  wind_speed = []
  gust_wind = []
  visible = []
  hum = []
  pre = []
  rain = []
  sunlight = []

driverReady = False
region = 'hsinchu'
reginTitle="新竹測站觀測資料"

url = 'https://www.cwb.gov.tw/V8/C/W/OBS_Station.html?ID=46757'
from time import sleep   # so that we do NOT have to write time.sleep( ) :-) 
def initCWB(): 
   global  driver, driverReady
   #啟動模擬瀏覽器
   from selenium.webdriver.chrome.options import Options
   options = Options()
   options.add_argument('--no-sandbox') # Bypass OS security model
   options.add_argument("--log-level=3");  # "--disable-logging"  # 尚可, 仍有 Devtool 信息
   ## options.add_argument("--silent")  #  沒用 ! ! !
## get rid off Devtool msg / chrome msg ... 
   options.add_experimental_option('excludeSwitches', ['enable-logging'])  # 要! 要 !!要 !!!
## do NOT open the browser
   options.add_argument("--headless")
##
   try:
      driver = webdriver.Chrome(options=options) # for Windows: 把 chromedriver.exe 放要執行 .py 程式的目錄即可 !
      driverReady = True
   except:
      print("!!! Can NOT get WEB driver !!!")
   #取得網頁代碼
   try:
     driver.get(url)
     open(region+'.html','wb').write(driver.page_source.encode('utf-8'))
   except:
     print("!!! get URL Fail :" + url)

# #對list中的每一項 <tr>
#for tr in trs:
def processTr(tr):
  global date,temp,weather, wind_direction, wind_speed, gust_wind
  global visible, hum, pre, rain, sunlight
  # print("===NOW ", datetime.datetime.now() , flush=True) 
  if tr != None:
    # 使用datetime取得時間年分
    year = str(datetime.datetime.now().year)
#   取時間, <tr>內的<th>, <th>內為時間 月/日<br>時:分
    d = tr.th.text
    d = year + d
#   字串轉為datetime格式
    date.append(datetime.datetime.strptime(d, '%Y%m/%d %H:%M'))
    temp.append(tr.find('td',{'headers':'temp'}).text)
    ggyy = tr.find('td',{'headers':'weather'}).find('img')
    if ggyy != None:
       weather.append(ggyy['title'])
    else: weather.append( "不知道" )
    wind_direction.append(tr.find('td',{'headers':'w-1'}).text)
    wind_speed.append(tr.find('td',{'headers':'w-2'}).text)
    gust_wind.append(tr.find('td',{'headers':'w-3'}).text)
    visible.append(tr.find('td',{'headers':'visible-1'}).text)
    hum.append(tr.find('td',{'headers':'hum'}).text)
    pre.append(tr.find('td',{'headers':'pre'}).text)
    rain.append(tr.find('td',{'headers':'rain'}).text)
    sunlight.append(tr.find('td',{'headers':'sunlight'}).text)

def buildTable( ):
  global table    ## 以下兩列的  global  其實不必要 !
  global date,temp,weather, wind_direction, wind_speed, gust_wind
  global visible, hum, pre, rain, sunlight
  table = {
"觀測時間":date,
"溫度(°C)":temp,
"天氣":weather,
"風向":wind_direction,
"風力 (m/s)":wind_speed,
"陣風 (m/s)":gust_wind,
"能見度(公里)":visible,
"相對溼度(%)":hum,
"海平面氣壓(百帕)":pre,
"當日累積雨量(毫米)":rain,
"日照時數(小時)":sunlight
}

## 這函數會把 line 和 line2 準備好, 分別是次新和最新 的氣象資料 
def prepareData( ):
    global  driver, line, line2, driverReady, table
    #指定 lxml 作為解析器
    soup = BeautifulSoup(driver.page_source, features='lxml')
    # <tbody id='obstime'>  # 抓過去24小時資料 (氣象局網頁給的) 
    tbody = soup.find('tbody',{'id':'obstime'})

    # <tbody>内所有<tr>標籤
    trs = tbody.find_all('tr')   ## Google 搜尋 BeautifulSoup + find
    tr=trs[0]   #  最新的; 因只要 push 兩列, 偷懶沒寫函數, 複製上面一段過來用 :-)
    clearLists( )   # 清除所有 11 項 List   # (主要是後來才想要 push 兩筆資料 :-) 
    processTr(tr)  # 其實直接寫 processTr(trs[0]) 即可
    buildTable( )  # 參看前面處理 trs[1] ..
    line2 ="\r\n"
    for gg in table:    
       yy = table[gg][0]   
       if gg == "觀測時間":   # 特別處理這項
          yy = yy.strftime("%Y-%b-%d %H:%M:%S")
       line2 += gg +":" + yy
       line2 += "\r\n"
    print("Weather info: ", line2, flush=True)   # for debug  

def grabCWBthenPush( ): 
  global gotInput2, theInput2, allDead, driver, crawl
  sleep(12);   # give you several time to do binding in your project
  while True:
        if crawl:
            initCWB( )
            prepareData( )
            driver.quit()
            crawl=False
        if allDead: 
            break

#creat a thread to do Input data from keyboard, by tsaiwn@cs.nctu.edu.tw
thready = threading.Thread(target=grabCWBthenPush)
thready.daemon = True    # daemon 的 a 不發音 == 魔鬼 == server program
thready.start()   # 這時 thready 也開始 "同時" 執行

def check_alive(him):   # check a thread to see if it is alive?
    him.join(timeout=0.0)
    return him.is_alive() 

while True:     ##  這是 main thread 主執行緒的　典型寫法 : 一個 Loop !
    if(allDead): break;  

#  # 以上用來 check 負責抓 CWB 資料的 thread 是否還活著
    try:   ## main thread 依序做以下 (1)(2)(3) 三件事: 
    #(1)Pull data from a device feature called "Dummy_Control" 
        value1=DAN.pull('Dummy_Control')
        if value1 != None:
            print (value1[0])
            crawl=True 
                

    except KeyboardInterrupt:    ## 敲了 CTRL_C
        break
    except Exception as e:    ## 不明原因, 可能剛剛網路斷了!
        print(e)
        if str(e).find('mac_addr not found:') != -1:
            print('Reg_addr is not found. Try to re-register...')
            DAN.device_registration_with_retry(ServerURL, Reg_addr)
        else:
            print('Connection failed due to unknow reasons.')
            time.sleep(1)    
    try:
       time.sleep(0.2)
    except KeyboardInterrupt:
       break
time.sleep(0.5)
try: 
   DAN.deregister()
except Exception as e:
   print("===")
print("Bye ! --------------", flush=True)
sys.exit( );   ## Quit the program 
