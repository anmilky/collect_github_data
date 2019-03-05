import os
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


global finished;
finished=0
global_data = threading.local()

def restructjson(r,url):
    pagecount=int(r["total_count"]/100)+1
    items=r["items"]
    for i in range(2,pagecount+1):
        url = url + "&page="+str(i)
        r1=request_url(url)
        for item in r1["items"]:
            items.append(item)
    return r

def visit( urls, line, year,line_count):
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
                pass
            else:

                reponame=line.replace("/","#")
                pagecount = int(r["total_count"] / 100)+ 1
                if not pagecount==1:
                    # print(r["total_count"])
                    r=restructjson(r,url)
                if not os.path.exists(year + "incomplete"):
                    os.makedirs(year + "incomplete")
                f=open(year + "incomplete/" + reponame + "$" + str(global_data.keyword) + ".json", "w", encoding="utf-8")
                json.dump(r, f)
                f.close()
            # except Exception as e:
            #     print("visit "+e)
            global finished
            finished=finished+1
    except Exception as e:
        print(e)




if __name__ == '__main__':
    os.chdir("fix_npe")
    print(os.getcwd())
    bugtypes = ["fix npe NOT merge", "fix null pointer"]
    # year = sys.argv[1]
    # batchnum_lastrun = int(sys.argv[2])
    year=str(2016)
    batchsize = 50
    batchnum_lastrun = 0
    threadcount = 50

    logname = "log_"+year+"_incomplete"
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
        f=open (year+'_incomplete', 'r')
        line_count=0
        batchnum_now=0
        for line_ in f.readlines ():
            line_=line_.strip()
            line_count=line_count+1
            line=line_.split()[0].strip()
            bugflag=int(line_.split()[1].strip())-1
            bugtype=bugtypes[bugflag]
            if not batchnum_now==int((line_count-1)/batchsize+1):

                 batchnum_now=int(line_count/batchsize+1)
                 print (datetime.datetime.now ().strftime ('%Y-%m-%d %H:%M:%S') + "  "+year+" BATCH " + str (batchnum_now) + " start")
                 logger.info(datetime.datetime.now ().strftime ('%Y-%m-%d %H:%M:%S') + "  "+year+" BATCH " + str (batchnum_now) + " start")

            if batchnum_now<batchnum_lastrun:
                continue
            else:
                # print(line)
                urls=["https://api.github.com/search/commits?q=repo:" + line +"+"+bugtype+"&per_page=100"]
                if len(future_tasks)<batchsize:
                    # print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+"repo start: "+str(line_count))
                    future_task = pool.submit (visit,urls, line,year,line_count)
                    future_tasks.append(future_task)
                if len(future_tasks)==batchsize:
                    wait (future_tasks)
                    print ("finished，before " + str (line_count))
                    print (datetime.datetime.now ().strftime ('%Y-%m-%d %H:%M:%S') + " BATCH =========>" + str (batchnum_now) + " end"+"   finished:"+str(finished)+"   threadcount: "+str(threadcount))
                    logger.info (datetime.datetime.now ().strftime ('%Y-%m-%d %H:%M:%S') + " BATCH =========>" + str (batchnum_now) + " end"+"   finished:"+str(finished)+"   threadcount: "+str(threadcount))
                    future_tasks=[]

        f.close()

    except StopIteration as e:
        pass
    wait (future_tasks)
    print(time.time() - t1)
    print("write to file")



