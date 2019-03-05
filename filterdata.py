import json
import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor, wait
from log import makelog

from request_urls import request_url
logger = logging.getLogger("mylogger")
global_data = threading.local()
class filter():
    def __init__(self,year,log_saved_name,threadnum,batchsize,lastbatch=0):
        self.year=str(year)
        self.log_saved_name=log_saved_name
        self.threadnum=threadnum
        self.pool = ThreadPoolExecutor(self.threadnum)
        self.batchsize=batchsize
        self.finished=0
        self.lastbatch=lastbatch
        makelog(self.log_saved_name)

    def filt(self):
        try:
          f= open(self.year+"_url")
          batchsize_tmp=0
          future_tasks=[]
          batchsize_ct=0
          for line in f.readlines():
              batchsize_tmp=batchsize_tmp+1
              batchsize_ct =int(batchsize_tmp/self.batchsize)+1
              if batchsize_ct<self.lastbatch:
                  pass
              else:
                  if len(future_tasks) <self.batchsize:
                      url=line.strip()
                      future_task=self.pool.submit (self.visit,url)
                      future_tasks.append(future_task)
                  if len(future_tasks) == self.batchsize:
                      logger.info("%s========================>batch:%d start"%(self.year,batchsize_ct))
                      print("%s======>batch:%d start"%(self.year,batchsize_ct))
                      for future_task in future_tasks:
                          if future_task.result()==None:
                              pass
                          else:
                              print(future_task.result())
                      wait(future_tasks)
                      print("threadsize:%d   finised:%d" % (self.threadnum, self.finished))
                      logger.info("%s========================>threadsize:%d   finised:%d" % (self.year,self.threadnum, self.finished))
                      print("%s======>batch:%d end" % (self.year,batchsize_ct))
                      future_tasks = []
          self.pool.shutdown(wait=True)
          logger.info("batch:%d end" % (batchsize_ct))
          print("batch:%d end" % (batchsize_ct))
          f.close()
        except Exception as e:
             print(e)
             logger.warning(e)

    def visit(self,url):
     # try:
        repo=url.split("commits")[0].split("repos")[1].replace("/"," ").strip().replace(" ","/")
        r=request_url(url)
        message=r["commit"]["message"]
        files=r["files"]
        if self.filter_msg(message) and self.filter_files(files):
            with open(self.year+"_url_filted","a",encoding="utf-8")as f:
                f.write(url+"\n")
                logger.info("pass:%5s  repo: %s"%("True",repo))
        else:
            logger.info("pass:%5s  repo: %s" % ("False",repo ))
        self.finished=self.finished+1
     # except Exception as e:
     #     print(e)


    def filter_msg(self,message):
        if message.lower().__contains__("merge")\
            or message.lower().__contains__("delete")\
            or message.lower().__contains__("remove"):
           return False
        else:
            return True
    def filter_files(self,files):
        javafile=0
        for item in files:
            if javafile>1:
                return False
            if item["filename"].endswith(".java"):
                javafile=javafile+1
        if javafile==1:
            return True


if __name__ == '__main__':
   os.chdir("fix_npe/all_api_url/")
   # yearlist=[2009,2010,2011,2018]
   # yearlist=[2012,2013,2014]
   # yearlist=[2015,2016,2017]
   # for year in yearlist:
   year=2014
   lastbatch=743
   a= filter(year=year,log_saved_name="log_"+str(year)+"_all_api_url",threadnum=50,batchsize=50,lastbatch=lastbatch)
   a.filt()


