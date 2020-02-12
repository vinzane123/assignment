from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
import datetime
import json
import re
import requests
import os
import time
from celery import group
import asyncio
from final_bol.settings import client_id,client_secret,URL_CLOUD
from boloo_app.models import *
from .auto_refresh import *
from .tasks import sync_items,process,sync_test

from django.core import serializers

from rest_framework.decorators import api_view,APIView
from rest_framework import viewsets,views
from rest_framework import generics
from boloo_app.serializers import *
from rest_framework.parsers import JSONParser
from django.core import serializers
from rest_framework.response import Response
from rest_framework import status
from boloo_app.serializers import ItemsSerializer

token = None
os.environ['expiry'] = str(0)
expiry =  0



'''
Rest-api which returns
all the items from the database
'''

class ItemsView(viewsets.ReadOnlyModelViewSet):
        queryset = Items.objects.all()
        serializer_class = ItemsSerializer

'''
Rest-api which returns
token for client and secret
'''

class TokenView(viewsets.ViewSet):

     def create(self,request):
                if request.data:
                        url = "https://login.bol.com/token"
                        headers={'Accept':'application/json','Content-Type':'application/x-www-form-urlencoded'}
                        id = request.data['client_id']
                        secret = request.data['client_secret']
                        payload = {'client_id': id, 'client_secret': secret,'grant_type':'client_credentials'}
                        r = requests.post(url, data=payload)
                        respon = json.loads(r.text)
                        d = {'client_id': id, 'client_secret': secret,'token':respon['access_token']}
                        serializers =  TokenSerializer(data=d,many=True)
                        os.environ['token'] = respon['access_token']
                        token = respon['access_token']
                        dic =  {"access_token":respon['access_token'],"status_code":r.status_code,
                        "access_token_expiration":time.time()+respon['expires_in']}
                        expiry = time.time()+299
                        os.environ['expiry'] = str(expiry)
                        return Response(dic)
                else:
                        dic = {'details':'Please provide client_id & client_secret'}
                        return Response(dic)

'''Rest-api which gets the list
of items and syncs in db.
'''

class SyncItems(viewsets.ViewSet):

     def create(self,request):
                if request.data:
                        category = request.data['category']
                        payload = {'category':category}
                        r = requests.get('http://localhost:8000/getShipments', params=payload)
                        res = json.loads(r.text)
                        if 'isSuccess' in res:
                                return Response(res)
                        else:
                                jobs = group(process.s(item) for item in res['response'])
                                result = jobs.apply_async()
                                store_items(result.join(),res['data'],category)
                                dic = {'isSuccess':True,'details':'Data stored successfully','sync_items':result.join(),'status_code':200}
                                return Response(dic)          
                else:
                        dic = {'isSuccess':False,'details':'Please provide category','status_code':401}
                        return Response(dic) 


@csrf_exempt
def token(request):
        if request.method == 'POST':
                url = "https://login.bol.com/token"
                headers={'Accept':'application/json','Content-Type':'application/x-www-form-urlencoded'}
                if request.POST:
                        id = request.POST['client_id']
                        secret = request.POST['client_secret']
                        payload = {'client_id': id, 'client_secret': secret,'grant_type':'client_credentials'}
                        r = requests.post(url, data=payload)
                        respon = json.loads(r.text)
                        os.environ['token'] = respon['access_token']
                        token = respon['access_token']
                        dic =  {"access_token":respon['access_token'],"status_code":r.status_code,
                        "access_token_expiration":time.time()+respon['expires_in']}
                        expiry = time.time()+299
                        os.environ['expiry'] = str(expiry)
                        return HttpResponse(json.dumps(dic))



@refresh_token
@csrf_exempt
def list_items(request):
                items = []
                url = 'https://api.bol.com/retailer/'
                if os.environ['expiry'] == str(0):
                        dic = {'isSuccess':False,'details':'Please try after login','status_code':400}
                        return HttpResponse(json.dumps(dic))
                if token != None:
                        auth = "Bearer "+os.environ['token']
                        if request.method == 'GET':
                                myDict = dict(request.GET)
                                if 'category' in myDict:
                                        category=request.GET['category']
                                        url = url+category
                                        result=[]
                                        one_method = asyncio.run(recurse_all(auth,url,category,result,page = 1,method='FBR'))
                                        if len(one_method) >=0:
                                                items.append(one_method) 
                                        sec_method = asyncio.run(recurse_all(auth,url,category,result=[None],page = 1,method='FBB'))
                                        if len(sec_method) >=0:
                                                items.append(sec_method)
                                        if not items[0] and not items[1] :
                                                dic = {'isSuccess':True,'response':'No data available.','status_code':200,'data':None}
                                                return HttpResponse(json.dumps(dic))     
                                        else:                                                                                      
                                                result = auxy_list(items[0][0],category)
                                                result = result+auxy_list(items[1][0],category)
                                                iter_items = asyncio.run(all_items(auth,url,category,result))
                                                dic = {'response':result,'status_code':200,'data':iter_items}
                                                return HttpResponse(json.dumps(dic))
                                else:
                                        dic = {'isSuccess':False,'details':'Please provide category','status_code':401}
                                        return HttpResponse(json.dumps(dic))


async def recurse_all(auth,url,category,result=[],page=1,method='FBR'):
                result = []
                headers={'Accept':'application/vnd.retailer.v3+json','Authorization':auth}
                payload = {'maxCapacity':'7','timeToLive':'1','timeUnit':'MINUTES','page':page,'fulfilment-method':method}        
                r= requests.get(url,headers=headers,params=payload)
                d = json.loads(r.text)
                if d:
                        result.append(json.loads(r.text))
                        page+=1
                        if page%7 == 0:
                                await asyncio.sleep(60)
                        recurse_all(auth,url,category,result,page,method)  
                        return result   
                else:
                        return result




def auxy_list(data,category):
        result = []
        if data and category:
                eav = data[category]
                if category == 'shipments':
                        for i in range(0,len(eav)):
                                result.append(eav[i]['shipmentId'])
                        return result
                elif category == 'orders':
                        for i in range(0,len(eav)):
                                result.append(eav[i]['orederId'])
                        return result
                elif category == 'returns':
                        for i in range(0,len(eav)):
                                result.append(eav[i]['rmaId'])
                        return result
        else:
                return None



def store_items(ids,data,category):
        count=0
        if category == 'shipments':
                for i in data:
                        ins = Items(id=ids[count],data=data[count],status='shipment')
                        ins.save()
                        count+=1
        elif category == 'orders':
                for i in data:  
                        ins = Items(id=ids[count],data=data[count],status='open')
                        ins.save()
        else:
                for i in data:
                        ins = Items(id=ids[count],data=data[count],status='returned')
                        ins.save()
                


async def all_items(auth,uri,category,ids):
                result = []
                count=0
                headers={'Accept':'application/vnd.retailer.v3+json','Authorization':auth}
                payload = {'maxCapacity':'7','timeToLive':'1','timeUnit':'MINUTES'} 
                for i in ids:
                        if  count%6 == 0 and count != 0 :
                                print('count:',count)
                                await asyncio.sleep(60) 
                                count+=1                          
                        else:
                                print('count>7',count)
                                urs = uri+'/'+str(i)
                                r= requests.get(urs,headers=headers,params=payload)
                                result.append(json.loads(r.text))
                                count+=1        
                return result

   

