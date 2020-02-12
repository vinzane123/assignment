import datetime
from django.db import models
from django.db.models.query import QuerySet


class Shipments(models.Model):
    shipmentId = models.TextField(unique=True,null=False,default=None,primary_key=True)
    data = models.TextField(null=True,default=None)
    category = models.TextField(default=None,null=False)
    shipmentDate = models.TextField(unique=False,blank=False)
    shipmentItems = models.TextField(null=False,default=None)
    transportId = models.TextField(null=False,default=None)

'''Currently-used model.'''
class Items(models.Model):
    id = models.IntegerField(unique=True,null=False,default=None,primary_key=True)
    data = models.TextField(null=False,default=None)
    status = models.TextField(null=False,default='Open')

