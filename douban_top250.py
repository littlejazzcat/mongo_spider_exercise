import requests
from lxml import etree
import pymongo
import re
import time

client = pymongo.MongoClient('localhost', 27017)#27017是mongodb默认端口号，这段用于链接数据库
mydb = client['mydb'] #新建mydb数据库，类似于新建一个excel文件
musictop = mydb['musictop'] #新建musictop数据集合，类似于excel文件中的一个表格

headers = {
     'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
} #请求头

#这个函数用来获取每首歌的详细介绍的url然后再调用下一个函数（并将获取的url传入）用来获取详细信息
#para:豆瓣top250每页的url
def get_music_url(url):
    html = requests.get(url,headers = headers)
    selector = etree.HTML(html.text)
    music_hrefs = selector.xpath('//a[@class = "nbg"]/@href')
    for music_href in music_hrefs:
        get_music_info(music_href)
    #---------------------------

#这个用来获取每首歌的详细信息
#para:从get_music_url()获取的url
def get_music_info(url):
    html = requests.get(url,headers = headers)
    selector = etree.HTML(html.text)
    name = selector.xpath('//*[@id="wrapper"]/h1/span/text()')[0]
    player = re.findall('表演者:.*?>(.*?)<',html.text,re.S)[0]
    #publish_time = selector.xpath('//*[@id="info"]/text()')
    publish_time = re.findall('发行时间:.*?;(.*?)\s',html.text,re.S)[0]
    genere = re.findall('流派:.*?;(.*?)\s',html.text,re.S)
    if len(genere) == 0:
        genere = '未知'
    else:
        genere = genere[0].strip()
    publishers = re.findall('出版者:.*?;(.*?)\s',html.text,re.S)
    if len(publishers) == 0:
        publisher = '未知'
    else:
        publisher = publishers[0].strip()
    score = selector.xpath('//*[@id="interest_sectl"]/div/div[2]/strong/text()')[0]
    #----------------------------------
    content = etree.tostring(selector)
    print("%s\n%s\n%s\n%s\n%s\n%s" %(name,player,genere,publish_time,publisher,score))
    info = {
        'name':name,
        'player':player,
        'style':genere,
        'time':publish_time,
        'publisher':publisher,
        'score':score
    }
    musictop.insert_one(info)

if __name__ == '__main__':
    urls = ['https://music.douban.com/top250?start={}'.format(str(i)) for i in range(0,250,25)]
    for url in urls: #这是榜单页面的url
        get_music_url(url)
        time.sleep(2)
