import csv
import datetime
import json
import os
import sys
import time
import threading
from asyncio import as_completed
from concurrent.futures import ThreadPoolExecutor,wait

from request_urls import request_url
import queue
import logging


finished=0
global_data = threading.local()
# q_result= queue.Queue()

def readCSV(year):
    with open(year+".csv") as csvfile:
        csv_reader = csv.reader(csvfile) # 使用csv.reader读取csvfile中的文件
        header = next(csv_reader)  # 读取第一行每一列的标题
        line=next(csv_reader)
        while line:
            line=next(csv_reader)
            yield line[0]
        yield None

def visit( urls, line, year,line_count):
    global finished
        # print(url)
    # print ("Thread visit->>>>>>>>>>",str(line_count))
    try:
        global_data.keyword=0
        for url in urls:
            global_data.keyword=global_data.keyword+1
            bugtype=url.split("+")[-1]
            # try:
            #     print(threading.current_thread().is_alive())
            r=request_url(url)
            logger.info("%-40s keyword: %-20s commit num:%d"%(line,bugtype,r["total_count"]))
            # print(line+" "+str(r["total_count"]))
            if r["total_count"]==0:
                global_data.total_count=0
                pass
            else:
                global_data.total_count = r["total_count"]
                reponame=line.replace("/","#")
                with open(year+"/"+reponame+"$"+str(global_data.keyword)+".json","w",encoding="utf-8")as f:
                    json.dump(r,f)
        finished=finished+1
            # except Exception as e:
            #     print("visit "+e)
    except Exception as e:
        print(e)

    #     global_data.total_count = -1
    # dict={line:global_data.total_count}
    # q_result.put(dict)
    # print (datetime.datetime.now ().strftime ('%Y-%m-%d %H:%M:%S') + "repo end: " + str (line_count))
    # print("Thread end ->>>>>>>>>>",str(line_count))


if __name__ == '__main__':
    year = sys.argv[1]
    batchnum_lastrun = int(sys.argv[2])

    # year=str(2009)
    batchsize =50
    # batchnum_lastrun = 0
    threadcount = 50
    bugtype = ["fix npe", "fix null pointer"]
    logname = bugtype[0].replace(" ", "_")
    logger = logging.getLogger("mylogger")
    logger.setLevel(level=logging.INFO)
    time_now = datetime.datetime.now().strftime('%Y-%m-%d')
    handler = logging.FileHandler("log_" + year + "_" + logname + ".txt")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    t1 = time.time ()
    if not os.path.exists(year):
         os.makedirs (year)

    pool = ThreadPoolExecutor (threadcount)  # 不填则默认为cpu的个数*5
    start = time.time ()
    future_tasks=[]
    try:
        f=open (year+'.txt', 'r')
        # with open (year+'.txt', 'r') as f:
        line_count=0
        batchnum_now=0
        old_finished=0
        for line in f.readlines ():
            line=line.strip()
            line_count=line_count+1
            if not batchnum_now==int((line_count-1)/batchsize+1):

                 batchnum_now=int(line_count/batchsize+1)
                 print (datetime.datetime.now ().strftime ('%Y-%m-%d %H:%M:%S') + "  "+year+" BATCH " + str (batchnum_now) + " start")
                 logger.info(datetime.datetime.now ().strftime ('%Y-%m-%d %H:%M:%S') + "  "+year+" BATCH " + str (batchnum_now) + " start")

            if batchnum_now<batchnum_lastrun:
                continue
            else:
                # print(line)
                urls=["https://api.github.com/search/commits?q=repo:" + line +"+"+type+"&per_page=100" for type in bugtype]
                # print(urls)
                if len(future_tasks)<batchsize:
                    # print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+"repo start: "+str(line_count))
                    future_task = pool.submit (visit,urls, line,year,line_count)
                    future_tasks.append(future_task)
                if len(future_tasks)==batchsize:
                    wait (future_tasks)
                    print ("finished，before " + str (line_count))

                    live=finished-old_finished
                    old_finished=finished
                    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " BATCH =========>" + str(
                        batchnum_now) + " end" + "   finished:" + str(live) + "   threadcount: " + str(threadcount))
                    logger.info(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + " BATCH =========>" + str(
                        batchnum_now) + " end" + "   finished:" + str(live) + "   threadcount: " + str(threadcount))

                    if not live==batchsize:
                        print("finised!=batchsize  something wrong! run this batch again: "+str(batchnum_now))
                        logger.info("finised!=batchsize  something wrong! run this batch again: "+str(batchnum_now))
                        exit(1)
                    else:
                        future_tasks = []
        f.close()

    except StopIteration as e:
        pass
    pool.shutdown(wait=True)
    print(time.time() - t1)
    print("write to file")

    # csvFile = open (year + "fix_sql_injection"+".csv", 'w', newline='')
    # try:
    #     writer = csv.writer (csvFile)
    #     writer.writerow (("reponame",))
    #     while not q_result.empty ():
    #         for k, v in q_result.get ().items ():
    #             writer.writerow ((k,v))
    # finally:
    #     csvFile.close ()


