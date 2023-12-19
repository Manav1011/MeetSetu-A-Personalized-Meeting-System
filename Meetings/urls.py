from django.urls import path
from .views import create_meet,get_user_list,get_meeting_details,join_meet,get_active_meetings


urlpatterns = [
    path('create_meet/',create_meet,name='create_meet'),
    path('join_meet/',join_meet,name='join_meet'),
    path('get_user_list',get_user_list,name='get_user_list'),
    path('get_active_meetings',get_active_meetings,name='get_active_meetings'),
    path('get_meeting_details',get_meeting_details,name='get_meeting_details')
]
