from rest_framework import serializers
from .models import Meeting
from StakeHolders.serializers import UserListSerializer

class MeetingSerializer(serializers.ModelSerializer):
    host = UserListSerializer()
    allowed_participants = UserListSerializer(many=True)
    blacklisted_participants = UserListSerializer(many=True)
    class Meta:
        model = Meeting
        fields = ['UID','host','allowed_participants','blacklisted_participants','type','status','created_at']