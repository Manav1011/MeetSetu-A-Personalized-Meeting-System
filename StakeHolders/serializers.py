from .models import StakeHolder
from rest_framework import serializers

class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StakeHolder
        fields = ['id','email']