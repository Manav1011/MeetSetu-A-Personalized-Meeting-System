from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
import random,string
import json
from .models import Meeting
from StakeHolders.models import StakeHolder
from StakeHolders.serializers import UserListSerializer
import base64
from .serializers import MeetingSerializer

# Create your views here.

def xor_decipher(ciphertext, key):
    key_bytes = key.encode('utf-8')
    ciphertext_bytes = base64.b64decode(ciphertext)    
    decrypted_bytes = [c ^ key_bytes[i % len(key_bytes)] for i, c in enumerate(ciphertext_bytes)]
    decrypted_data = bytes(decrypted_bytes).decode('utf-8')        
    return decrypted_data

def decryption_decorator(func):
    def wrapper(*args,**kwargs):
        try:
            data = None
            key = None
            if args[0].method == 'POST':
                key = args[0].data.get('secret')        
                data = args[0].data['data']        
            if args[0].method == 'GET':
                key = args[0].GET.get('secret')
                data = args[0].GET.get('data')        
            if key:
                data_decrypted  = xor_decipher(data,key)                    
                args[0].data['data']  = json.loads(data_decrypted)            
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            response = {'error':True,'message':str(e)}
            return Response(response,status=500)
    return wrapper

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@decryption_decorator
def create_meet(request):
    creds = request.data.get('data')
    print(creds)        
    response = {'error':False,'data':{},'message':''}
    user = request.user    
    try:
        if 'meet_type' in creds:
            meet_type = creds['meet_type']
            if meet_type == 'public':
                # Create an meeting object
                meet_obj = Meeting.objects.create(type='public',host=user, status='active')
                # Get all the users to set the allowed participants field
                users = StakeHolder.objects.all()
                meet_obj.participants.add(user)
                meet_obj.allowed_participants.add(*users)                
                response['data']['UID'] = meet_obj.UID
            if meet_type == 'private':
                if  'user_list' in creds:
                    user_list = creds.get('user_list')
                    meet_obj = Meeting.objects.create(type='private',host=user, status='active')
                    # Get all the users to set the allowed participants field
                    users = StakeHolder.objects.filter(id__in=user_list)
                    meet_obj.participants.add(user)
                    meet_obj.allowed_participants.add(*users)
                    response['data']['UID'] = meet_obj.UID
                else:
                    raise Exception('Credentials missing')
                
            if meet_type == 'asktojoin':                
                meet_obj = Meeting.objects.create(type='onetoone',host=user, status='active')                                
                meet_obj.participants.add(user)
                response['data']['UID'] = meet_obj.UID
                
            if meet_type == 'onetoone':
                if  'user_list' in creds:
                    user_list = creds.get('user_list')
                    meet_obj = Meeting.objects.create(type='onetoone',host=user, status='active')
                    # Get all the users to set the allowed participants field
                    users = StakeHolder.objects.filter(id__in=user_list)
                    meet_obj.participants.add(user)
                    meet_obj.allowed_participants.add(*users)
                    response['data']['UID'] = meet_obj.UID
                else:
                    raise Exception('Credentials missing')
        else:
            raise Exception('Credentials missing')
    except Exception as e:
        response['error'] = True
        response['message'] = str(e)
        return Response(response,status=500)        
    return Response(response,status=200)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@decryption_decorator
def join_meet(request):
    creds = request.data.get('data')    
    response = {'error':False,'data':{},'message':''}
    user = request.user    
    try:
        if 'meet_uid' in creds:
            meet_obj = Meeting.objects.filter(UID=creds['meet_uid']).first()
            if meet_obj and meet_obj.status == 'active':
                if user in meet_obj.allowed_participants.all():
                    if user not in meet_obj.participants.all():
                        meet_obj.participants.add(user)
                    response['data']['UID'] = meet_obj.UID
                else:
                    raise Exception("You're not allowed to join this meeting")
            else:
                raise Exception('Meeting does not exist or ended')    
        else:
            raise Exception('Credentials missing')
    except Exception as e:
        response['error'] = True
        response['message'] = str(e)
        return Response(response,status=500)        
    return Response(response,status=200)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_list(request):    
    response = {'error':False,'data':{},'message':''}    
    try:
        users = StakeHolder.objects.all().exclude(id=request.user.id)
        user_serialized = UserListSerializer(users,many=True)
        response['data'] = user_serialized.data        
    except Exception as e:
        response['error'] = True
        response['message'] = str(e)
        return Response(response,status=500)        
    return Response(response,status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_active_meetings(request):    
    response = {'error':False,'data':{},'message':''}    
    user = request.user
    try:
        meet_objs = Meeting.objects.filter(participants=user).all()
        meet_serialized = MeetingSerializer(meet_objs,many=True)        
        response['data'] = meet_serialized.data        
    except Exception as e:
        response['error'] = True
        response['message'] = str(e)
        return Response(response,status=500)        
    return Response(response,status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@decryption_decorator
def get_meeting_details(request):
    response = {'error':False,'data':{},'message':''}    
    try:
        creds = request.data.get('data')        
        user = request.user
        if 'meet_uid' in creds:            
            meet_obj = Meeting.objects.filter(UID=creds['meet_uid']).first()            
            meet_obj_serialized = MeetingSerializer(meet_obj)
            response['data'] = meet_obj_serialized.data
            if meet_obj.host == user:
                response['data']['is_owner'] = True
        else:
            raise Exception('Credentials missing')
    except Exception as e:
        print(e)
        response['error'] = True
        response['message'] = str(e)
        return Response(response,status=500)        
    return Response(response,status=200)

