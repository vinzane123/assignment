import string
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from celery import shared_task
import datetime
import json
import re
import requests
import os
import time
from .auto_refresh import *
from boloo_app.views import *
from final_bol.settings import URL_CLOUD



# normal-sync
@shared_task
def sync_items(category):
    payload = {'category': category}
    r = requests.get(URL_CLOUD,params=payload)
    return r.text

# scaled-sync
@shared_task
def process(item):
    return item
    

@shared_task
def sync_test(ls):
    return ls