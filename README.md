# 2020 NCTU Advanced IoT Final Project
* Topic: United Forecast System

## Requirement
1. linebot
2. chrome driver
3. ngrok
4. NodeMCU + DHT

## Usage
```
ngrok http 5000
python3 bot.py
python3 crawlerDAI.py
# NodeMCU connected to iottalk with DHT
``` 

## Snapshot
1. iottalk connected graph
![img](assets/img1.PNG)

2. bot.py which connect to line and use gTTS to make sound
![img](assets/img2.PNG)

3. crawlerDAI.py which send and get data from iottalk and crawl the data from weather report
![img](assets/img3.PNG)

4. arduino code which is for NodeMCU to collect the temperature, humidity data from DHT and send to iottalk
![img](assets/img4.PNG)

5. executing result
![img](assets/img5.PNG)
