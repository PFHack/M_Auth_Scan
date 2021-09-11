'''
==================================
Author: PFinal南丞
Date: 2021-09-11 11:54:45
Description:  高山仰止,景行行制,虽不能至,心向往之
==================================
'''
from zoomeye.sdk import ZoomEye
from queue import Queue
import threading
import requests
import pymongo
import socket

yellow = '\033[01;33m'
white = '\033[01;37m'
green = '\033[01;32m'
blue = '\033[01;34m'
red = '\033[1;31m'
end = '\033[0m'

version = 'v0.1'
message = white + '{' + red + version + ' #dev' + white + '}'

mongodb_scan_banner = f"""
{yellow} MongoDBAuthScan is a tool to Scan for unauthorized {yellow}
___  ___                       ____________  ___        _   _     _____                 
|  \/  |                       |  _  \ ___ \/ _ \      | | | |   /  ___|                {message}{green}
| .  . | ___  _ __   __ _  ___ | | | | |_/ / /_\ \_   _| |_| |__ \ `--.  ___ __ _ _ __  {blue}
| |\/| |/ _ \| '_ \ / _` |/ _ \| | | | ___ \  _  | | | | __| '_ \ `--. \/ __/ _` | '_ \ {blue}
| |  | | (_) | | | | (_| | (_) | |/ /| |_/ / | | | |_| | |_| | | /\__/ / (_| (_| | | | |{green}
\_|  |_/\___/|_| |_|\__, |\___/|___/ \____/\_| |_/\__,_|\__|_| |_\____/ \___\__,_|_| |_|{white}PFinal南丞{white}
                     __/ |                                                              
                    |___/                                                               
{red}MongoDBAuthScan is under development, please update before each use!{end}
"""
class Crawl_thread(threading.Thread):
    '''
       抓取线程类，注意需要继承线程类Thread
    '''

    def __init__(self, thread_id, queue):
        threading.Thread.__init__(self)  # 需要对父类的构造函数进行初始化
        self.thread_id = thread_id
        self.queue = queue  # 任务队列

    def run(self):
        '''
        线程在调用过程中就会调用对应的run方法
        :return:
        '''
        print('启动线程：', self.thread_id)
        self.crawl_spider()
        print('退出了该线程：', self.thread_id)

    def crawl_spider(self):
        zm = ZoomEye()
        zm.username = ''
        zm.password = ''
        zm.login()
        while True:
            if self.queue.empty():  # 如果队列为空，则跳出
                break
            else:
                page = self.queue.get()
                print('当前工作的线程为：', self.thread_id, " 正在采集：", page)
                try:
                    data = zm.dork_search('app:"MongoDB" +country:"CN" +service:"mongodb"', page)
                    for ip in zm.dork_filter("ip,port"):
                        data_queue.put(str(ip[0]) + ':' + str(ip[1]))  # 将采集的结果放入data_queue中
                except Exception as e:
                    print('采集线程错误', e)

class Parser_thread(threading.Thread):
    def __init__(self, thread_id, queue, file):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.queue = queue
        self.file = file

    def run(self):
        print('启动线程：', self.thread_id)
        while not flag:
            try:
                item = self.queue.get(False)  # get参数为false时队列为空，会抛出异常
                if not item:
                    pass
                self.parse_data(item)
                self.queue.task_done()  # 每当发出一次get操作，就会提示是否堵塞
            except Exception as e:
                pass
    def parse_data(self, item):
        sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sk.settimeout(0.3)
        iplist = item.split(':');
        try:
            sk.connect((iplist[0], int(iplist[1])))
            print(green, 'MongoDB未授权：', item)
            self.file.write(item+'\n')
            sk.close()
            conn = pymongo.MongoClient(iplist[0],int(iplist[1]),socketTimeoutMS=3000)
            dbname = conn.database_names()
            print(dbname)
        except Exception as e:
            #print(e)   
            pass


data_queue = Queue()  # 存放解析数据的queue
flag = False

def main():
    output = open('scan.txt', 'a')  # 将结果保存到一个json文件中
    pageQueue = Queue(50)  # 任务队列，存放网页的队列
    for page in range(1, 2):
        pageQueue.put(page)  # 构造任务队列

    # 初始化采集线程
    crawl_threads = []
    crawl_name_list = ['crawl_1', 'crawl_2', 'crawl_3']  # 总共构造3个爬虫线程
    for thread_id in crawl_name_list:
        thread = Crawl_thread(thread_id, pageQueue)  # 启动爬虫线程
        thread.start()  # 启动线程
        crawl_threads.append(thread)

        # 等待队列情况，先进行网页的抓取
    while not pageQueue.empty():  # 判断是否为空
        pass  # 不为空，则继续阻塞

    # 等待所有线程结束
    for t in crawl_threads:
        t.join()


    # 初始化解析线程
    parse_thread = []
    parser_name_list = ['parse_1', 'parse_2', 'parse_3']
    for thread_id in parser_name_list:  #
        thread = Parser_thread(thread_id, data_queue, output)
        thread.start()  # 启动线程
        parse_thread.append(thread)

     # 等待队列情况，对采集的页面队列中的页面进行解析，等待所有页面解析完成
    while not data_queue.empty():
        pass
    # 通知线程退出
    global flag
    flag = True
    for t in parse_thread:
        t.join()  # 等待所有线程执行到此处再继续往下执行

    print('退出主线程')
    output.close()    

if __name__ == '__main__':
    print(mongodb_scan_banner)
    main()    