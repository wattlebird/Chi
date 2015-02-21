import re
from urlparse import urlparse
import requests # Yes, you need to install that
from app import cache

def validateform(username):

    if username==None:
        return None
    else:
        if username.startswith('http://') or username.startswith('https://'):
            try:
                username = urlparse(username).path.split('/')[-1]
            except IndexError:
                return None
        if not re.match(r'^(?!_)[a-zA-Z0-9_]+$',username):
            return None
        else:
            return username

@cache.memoize(timeout=172800)
def getnickname(username):
    r = requests.get("http://api.bgm.tv/user/"+username)
    return r.json()['nickname']

@cache.memoize(timeout=172800)
def getitemname(itemidx):
    r = requests.get("http://api.bgm.tv/subject/"+str(itemidx))
    j = r.json()
    if len(j['name_cn']):
        return j['name_cn']
    else:
        return j['name']