import random
import threading
import time

import requests
import logging

from OpenSSL.SSL import SysCallError
#
logger = logging.getLogger ("mylogger")
# from OpenSSL.SSL import SysCallError
from OpenSSL.SSL import SysCallError
from urllib3.exceptions import MaxRetryError, SSLError
from fake_useragent import UserAgent

requests.packages.urllib3.disable_warnings()
authorization = [
        "ae02ced7b47e60bc22efd21c40c18a1de94922dd",  # caoshuai
        "8728bdb653c18e4b4d92d678bf99f17edfa0cc4f",  # tianyang
        "047b42e06e6814fab2fc25a12cc64b49210949fb",  # boshi
        "2f8c7a573e95b0aa85029a150637c22f07dd3fd2",  # lirong
        "e4bc0cf81371502ffdadf60445893c5d817606c3", # kongweixin
        "4403b9ce8efa7cad5ad8d7dac5765149c6dc1a95",# yaohouyou
        "c45fe873ae54cc066b4ebbbb7d74814f70459fdf",#haohui
        "ac20559afc5c9d6155ce2f9ddc732fe1d0c3c28b",  #hufei
        "b8671fcba454b798496edec890ce4748d987c37c", #lizheng
        "0565eba8bb2bab959af6fde65a9ff8648b3de66e",   #caoshuai
        "8b5f3381090965926e0cfe967ff850b392ac8c42",  #wangshuai
        "88378642320efb8587b78be6f95e7b9b655bfa3d", #hufei
        "3cf17763214b1cf226bb35a8f6d62ded234ca760",  #lixiao
        "977fbea78c417ca23ed2e4fbc40ec16ca05a1aab",#hezhongkai
        "7bea4254a6079b63a890e0fb4c5b18bcc3b56565",#wyw
        "7c24d0d32fff318f3df990f9f7fc35b594bd16c3",#limeng
        "9dd539b90e7fe301195cc7d00651b9fc1fc371f5",#wanghuanting
        "4467f0affcf017d423a319161f095d5d242fa581",#xueyongkang
        "ef50eb9b4ec209653296bfcd13b1f371175980b1",#dongping
        "ff606734988aefe6964fa63587514015e7314467",
        "648808ae3cd9499fb578805e72ca7ad31efeabab",
        "546d94a317d4cba3d7bb40449c9853b2cf8593a0",
        "ff68dbb9028c6c631ca44d275f095a3ffcbe0910",
        "5685751b924706580706ccf0ef08606059a5eae8",
        "6c0107b26ebaeb97ad7a1f4c6e367f9f0fefc995",#zhaishuangjiao
        "e063a2c0679b852fdd668fbb55b1691080b88851",
        "af7b21a1bf18948b4f2bc89d0a84ab4f764d158b",
        "835d51b6b66113b69388f1c46cd06372798b5c4f",
        "fd249f0e3dfc5de4ea6f1bf99e64875d34ffe3ec",
        "e19345f9eae74ba4b98b0ff005bf09f8f628fae4"
    ]


def changetoken():
    newid = random.choice (authorization)
    return "token " + newid

def changeagent():
    ua = UserAgent()
    return  ua.random
def change ( header ):

    header["Authorization"] = changetoken()
    header["User-Agent"] =changeagent()

    return header

def judge(r):
    if r==None:
        return False
    else:
        user=r.json()
        if user != None and "message" in user.keys() and user["message"] == "Bad credentials":

            # print(threading.current_thread(),"Bad credentials sleep 5 seconds")
            time.sleep(2)
            return False
        if user != None and "message" in user.keys () and user["message"] == "Validation Failed":
            return True
        if r.status_code==403:
            # print(threading.current_thread(),"API rate limit sleep 5 seconds")
            time.sleep (2)
            return False
        if r.status_code==200:
            return True


def request_url ( url ):
    # print(url)
    # token=changetoken()
    agent=changeagent()
    token=changetoken()
    header = {"Authorization":token,
              "User-Agent": agent,
              "Content-Type": "application/json",
              "Accept": "application/vnd.github.cloak-preview"}
    while 1:
        try:
            r = requests.get (url, headers=header,verify=False)
            if judge(r):
                return r.json()
            else:
                header=change(header)
        except ConnectionError as error:
            print("ConnectionERROR,sleep 2 seconds")
            logger.warning("ConnectionERROR ,sleep 2 seconds")
            time.sleep(2)
        except SSLError as error:
            print(" SSLError,sleep 2 seconds")
            logger.warning("SSLError,sleep 2 seconds" )
            time.sleep(2)
        except Exception as e:
                print(str(e))
                logger.warning(str(e))
                time.sleep(2)



