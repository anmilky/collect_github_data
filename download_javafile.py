import json
import re
import subprocess
import os
import sys
import threading
import time
import urllib
from struct import pack, unpack

import requests

from request_urls import request_url
from request_durls import request_durl
import logging
logger=logging.getLogger("mylogger")
counter_lock = threading.Lock()
class download():
    def __init__(self,year,commit_url,fileStorePath):
        self.language="c"
        self.path_org=os.getcwd()
        self.year=year
        self.commit_url=commit_url
        self.get=False
        self.basedir=fileStorePath
        self.basedir_new=fileStorePath+"/new_files/"
        self.basedir_old=fileStorePath+"/old_files/"
        # self.basedir=r"/javafiles/new_javafile/"
        self.geturldetail()

        if self.get:
            self.download_file()
    def geturldetail(self):
        request_result = request_url(self.commit_url)
        if request_result!=None:
            self.parent_sha = request_result["parents"][0]["sha"]
            files = request_result["files"]
            self.html_url = request_result["html_url"]
            if len(files)>0:
                for file in files:
                    filename=file["filename"]
                    if filename.endswith(self.language):
                        # if file["deletions"]!=0:
                            self.raw_url=file["raw_url"]
                            self.filename_comsha=file["sha"]+".java"
                            self.filename_pathname=file["filename"]
            self.get=True


    def download_file( self ):
        filenames = re.split (r"[a-zA-Z0-9]{40}/", self.raw_url)[-1]
        sha_new = re.findall (r"[a-zA-Z0-9]{40}/", self.raw_url)[0]
        sha_old = self.parent_sha

        down_title = "https://raw.githubusercontent.com/"
        reponame = re.findall (r"(?<=github.com/).*(?=/raw)",self.raw_url)[0]

        url_new = down_title + reponame + "/" + sha_new + filenames
        url_old = re.sub (r"[a-zA-Z0-9]{40}/", sha_old + "/", url_new)
        new_javafile_path = self.basedir_new+ self.year
        old_javafile_path = self.basedir_old+ self.year

        self.url2file_path_new = os.path.join(self.basedir, "url2file_" + self.year)
        self.url2file_path_old = os.path.join(self.basedir, "url2file_" + self.year)

        self.download_file_one(url_new,new_javafile_path,self.url2file_path_new)
        self.download_file_one(url_old,old_javafile_path,self.url2file_path_old)

    def download_file_one( self ,url,javafile_path,url2file_path):

        filename_comsha=javafile_path+"/"+ self.commit_url.split("repos/")[-1].replace("/","#")

        flag=False
        if os.path.exists (filename_comsha):
            if os.path.getsize (filename_comsha) == 0:
                    flag = True
                    logger.info (" %s already downloaded yet BUT it is null------new" % self.filename_comsha)
                    # print (" %s already downloaded yet BUT it is null------new" % self.filename_comsha)
        if not os.path.exists(filename_comsha):
            flag=True

        if flag:
            r=request_durl(url)
            with open(filename_comsha, "w", encoding="utf-8")as f:
                f.write(r.text)
            # urllib.request.urlretrieve(url,)
            # cmd_new="curl -s -o %s %s "%(filename_comsha,url)
            # subprocess.call(cmd_new,shell=True)
                with open(url2file_path,"a",encoding="utf-8") as f:
                    f.writelines (self.commit_url+"\n")
                    f.writelines (self.html_url+"\n")
                    f.writelines (filename_comsha+"\n")
                    f.writelines (self.filename_pathname+"\n")
                    f.write("\n")
            # print("download!")
            logger.info (" %sdownloaded successfully------new" % self.filename_comsha)
            return "done"

        else:
            logger.info (" %s already exists before------new" % self.filename_comsha)
            # print(" %s already exists before------new" % self.filename_comsha)




def download_javafile(*kwargs):
    year=kwargs[0]
    commit=kwargs[1]

    download(year,commit,fileStorePath="javafiles")



