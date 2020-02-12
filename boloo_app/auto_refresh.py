import time,requests
from final_bol.settings import client_id,client_secret,url
import os


def getAccessToken():
        host = url
        id= client_id
        secret= client_secret
        token_body = {'client_id': id, 'client_secret': secret,'grant_type':'client_credentials'}
        try:
            request = requests.post(host,data=token_body)
            request.raise_for_status()
        except Exception as e:
            return None
        else:
            return request.json()['access_token']

def refresh_token(func):
    def wrapper(*args,**kwargs):
        e = os.environ['expiry']
        for i in args:
            if time.time() > float(e) and float(e) != 0:
                getAccessToken()
            else:
                pass
            return func(*args,**kwargs)
    return wrapper


