import re
from urlparse import urlparse

def validateform(username):

    if username==None:
        return None
    else:
        if username.startswith('http://'):
            try:
                username = urlparse(username).path.split('/')[-1]
            except IndexError:
                return None
        if not re.match(r'^[^_][a-zA-Z0-9_].',username):
            return None
        else return username
