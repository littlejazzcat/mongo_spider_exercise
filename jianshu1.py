import requests
import re
from lxml import etree
import pymongo

headers = {
     'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
} #请求头

#连接数据库
client = pymongo.MongoClient('localhost', 27017)
mydb = client['mydb']
timeline = mydb['timeline']

def get_time_info(front_url, page): #front_url是某作者的动态首页url
    user_id = front_url.split('/')  #通过/将首页url拆成列表其中第四项是用户id后面会用到
    user_id = user_id[4]

    html = requests.get(front_url,headers = headers)
    selector = etree.HTML(html.text)
    infos = selector.xpath('//ul[@class = "note-list"]/li')#先爬大再爬小，一个li标签包含一个动态,infos是存储了所有li的列表
    
    for info in infos:
        publish_time = info.xpath('div/div/div/span/@data-datetime')[0]  #时间直接就在属性中所以直接用@取，也可以用正则表达式取标签中间内容里的时间
        #加上[0]获取列表中的内容（此时列表只有一个元素所以用0），否则结果是带有"[]"的
        typeofnew = info.xpath('div/div/div/span/@data-type')[0]
        timeline.insert_one({'date':publish_time,'type':typeofnew})
        print('%s,%s'%(publish_time,typeofnew))

    id_infos = selector.xpath('//ul[@class = "note-list"]/li/@id') #获取每个动态的id

    if len(infos)>1:
        feed_id = id_infos[-1]
        max_id = feed_id.split('-')[1]  #裂开后形成的列表应该是[feed (id)]所以取[1]
        nexturl = 'https://www.jianshu.com/users/%s/timeline?max_id=%s&page=%s' %(user_id,max_id,page) #构造下一页的url
        page = page+1
        get_time_info(nexturl,page) #递归获取下一页的数据

if __name__  == '__main__':
    first_url = 'https://www.jianshu.com/users/9104ebf5e177/timeline'
    get_time_info(first_url, 1) #从第一页开始


