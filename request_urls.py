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



