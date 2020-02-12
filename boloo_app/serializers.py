from rest_framework import serializers
from boloo_app.models import *

class ItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Items
        fields = ('id','data','status') 


class TokenSerializer(serializers.Serializer):
    client_id = serializers.CharField(max_length=256)
    client_secret = serializers.CharField(max_length=256)
    token = serializers.CharField(max_length=4096)
