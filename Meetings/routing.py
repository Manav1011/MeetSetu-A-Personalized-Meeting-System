from .consumers import ChatRoomConsumer,SignalingConsumer
from django.urls import re_path

meet_endpoints = [
    re_path(r"chat/(?P<meet_uid>.+)/$", ChatRoomConsumer.as_asgi()),
    re_path(r"signaling/(?P<meet_uid>.+)/(?P<user>.+)/$", SignalingConsumer.as_asgi()),
]