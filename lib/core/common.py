# coding:utf-8
from __future__ import print_function
from bs4 import BeautifulSoup
import sys
import string

if sys.version.split()[0].split(".")[0] == 2:
    from urlparse import urlparse  
else :
    from urllib.parse import urlparse
    
import random
import configparser
import requests
import time
import os
import re

from lib.core.data import vulnoutput,unvulnoutput,unreachoutput,lock
from lib.core.log import logverifyerror,logvuln,logunvuln

from requests.exceptions import ConnectTimeout
from requests.exceptions import ConnectionError
from requests.exceptions import HTTPError
from requests.exceptions import TooManyRedirects

def get_title(htmlcode):
    """
    获取网站title  

    use:
    get_title(html_source)  

    return:  
    title  
    """
    soup = BeautifulSoup(htmlcode, 'html.parser')
    return str(soup.title)[7:-8]



def url_handle(url):
    """
    url处理函数  

    return:
    dict urldict  
    """

    if url.startswith("http"):
        p = urlparse(url)
        # pass

    else:
        url = "http://" + url 
        p = urlparse(url)
        if ":" in p.netloc:
            if "443" in p.netloc.split(":")[1]:
                url = url.replace("http://","https://")
                p = urlparse(url)

            else:
                pass
        else:
            pass
        

    return p.scheme+"://"+p.netloc

def get_random_ua():
    with open("./data/user_agents.txt","r") as f:
        UAs = [i.strip() for i in f.readlines()]
    return random.choice(UAs)


def random_str(length=10, chars=string.ascii_letters + string.digits):
    return ''.join(random.sample(chars, length))

def get_local_version(path):
    cp = configparser.ConfigParser()
    cp.read(path)
    return cp["info"]["version"]


def get_latest_revision():
    lv = None
    cp = configparser.ConfigParser()
    try:
        req = requests.get("https://raw.githubusercontent.com/bigblackhat/oFx/master/info.ini",timeout = 15)
        cp.read_string(req.text)

        lv = cp["info"]["version"]
    except Exception:
        pass
    return lv




def run(POC_Class,target,proxy=False,output=True,PocRemain=""):

    global vulnoutput,unvulnoutput,unreachoutput
    while not target.empty():

        try:
            target_url = target.get()
            rVerify = POC_Class(target_url,proxy)
            poc_name = rVerify._info["name"]
            # print(poc_name)
            vuln = rVerify._verify()
            if vuln[0] == True:
                try:
                    vulntitle=get_title(vuln[1])
                except:
                    vulntitle = ""
                lock.acquire()
                logvuln("POC Remain : %s ╭☞ Target Remain : %d Vuln %s | WebSite Title：%s "%(PocRemain,target.qsize(),target_url,vulntitle))
                # logvuln("%s ╭☞ %d Vuln %s | WebSite Title：%s | Server Response : %s"%(PocRemain,target.qsize(),target_url,vulntitle,vuln[1]))
                if poc_name in vulnoutput:
                    vulnoutput[poc_name].append(target_url+" || 网站Title： "+vulntitle)
                else:
                    vulnoutput.update({poc_name:list()})
                    vulnoutput[poc_name].append(target_url+" || 网站Title： "+vulntitle)
                lock.release()
            else:
                lock.acquire()
                logunvuln("POC Remain : %s ╭☞ Target Remain : %d UnVuln %s "%(PocRemain,target.qsize(),target_url))
                unvulnoutput.append(target_url)
                lock.release()
        
        except NotImplementedError as e :
            lock.acquire()
            logverifyerror("POC Remain : %s ╭☞ %d The POC does not support virtualized depiction scan mode  Error details：%s "%(PocRemain,target.qsize(),str(e)))
            unreachoutput.append(target_url+" || Error details"+str(e))
            lock.release()
            pass

        except TimeoutError as e:
            lock.acquire()
            logverifyerror("POC Remain : %s ╭☞ %d Connection timed out %s Error details：%s "%(PocRemain,target.qsize(),target,str(e)))
            unreachoutput.append(target_url+" || Error details"+str(e))
            lock.release()
            pass

        except HTTPError as e:
            lock.acquire()
            logverifyerror("POC Remain : %s ╭☞ %d HTTPError occurred %s Error details：%s "%(PocRemain,target.qsize(),target,str(e)))
            unreachoutput.append(target_url+" || Error details"+str(e))
            lock.release()
            pass

        except ConnectionError as e:
            lock.acquire()
            logverifyerror("POC Remain : %s ╭☞ %d Connection error %s Error details：%s "%(PocRemain,target.qsize(),target,str(e)))
            unreachoutput.append(target_url+" || Error details"+str(e))
            lock.release()
            pass

        except TooManyRedirects as e:
            lock.acquire()
            logverifyerror("POC Remain : %s ╭☞ %d The number of resets exceeds the limit, and the goal is discarded %s Error details：%s "%(PocRemain,target.qsize(),target,str(e)))
            unreachoutput.append(target_url+" || Error details"+str(e))
            lock.release()
            pass

        except BaseException as e:
            lock.acquire()
            logverifyerror("POC Remain : %s ╭☞ %d unknown mistake %s Error details：%s "%(PocRemain,target.qsize(),target,str(e)))
            unreachoutput.append(target_url+" || Error details"+str(e))
            lock.release()
            pass