from django.urls import path
from .views import create_meet,get_user_list,get_meeting_details


urlpatterns = [
    path('create_meet/',create_meet,name='create_meet'),
    path('get_user_list',get_user_list,name='get_user_list'),
    path('get_meeting_details',get_meeting_details,name='get_meeting_details')
]
