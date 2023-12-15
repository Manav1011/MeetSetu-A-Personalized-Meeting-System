import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import AuthConsumerLogs
import numpy as np
import asyncio
from django.core.cache import cache
from .views import CustomTokenObtainPairSerializer

class AuthConsumer(AsyncWebsocketConsumer):    
    entities = {}
    async def connect(self):
        self.secret = self.scope["url_route"]["kwargs"]["secret_key"]           
        await self.channel_layer.group_add(self.secret, self.channel_name)
        await self.accept()
        if self.secret not in AuthConsumer.entities:
            AuthConsumer.entities[self.secret]={}        
        self.response = {'error':0, 'message':'', 'data':{}}        
        self.user = await self.get_user()        
        self.otparr = {}
        if not self.user:                 
            self.response['error']+=1
            self.response['message'] = 'User not found'
            await self.send(text_data=json.dumps(self.response))
            await self.close()
    
    async def disconnect(self,close_code):        
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self,text_data):
        text_data = json.loads(text_data)    
        if text_data["client"] == "authenticator":                    
            org_val = await self.get_latest_cache()              
            if org_val['authenticator'] > 0: 
                self.response['error']+=1
                self.response['message'] = 'Request Limit Exceeded please try again after a minute'
                await self.send(json.dumps(self.response))               
                await self.close()
            else:                
                AuthConsumer.entities[self.secret]['authenticator'] = self            
                print(self.entities)
                org_val['authenticator']+=1
                cache.set(self.secret,org_val,60)
            if text_data['action'] == 'send_otps':
                if 'app' in self.entities[self.secret]:
                    await self.entities[self.secret]['app'].send(json.dumps({'qr_scanned':True}))
                await self.send_otps()
        elif text_data["client"] == "app":
            if 'action' not in text_data:
                org_val = await self.get_latest_cache() 
                if org_val['app'] > 0: 
                    self.response['error']+=1
                    self.response['message'] = 'Request Limit Exceeded please try again after a minute'
                    await self.send(json.dumps(self.response))               
                    await self.close()
                else:                
                    AuthConsumer.entities[self.secret]['app'] = self
                    print(self.entities)
                    org_val['app']+=1
                    cache.set(self.secret,org_val,60)            
            if 'action' in text_data and text_data['action']=='verify' and 'otp' in text_data:
                self.otp = text_data['otp']
                verified = await self.verify_otp()
                if verified == True:
                    org_val = await self.get_latest_cache() 
                    if text_data['view'] == 'signup':
                        self.user.email_verified = True
                        self.user.is_active = True
                        await self.save_user_obj()
                        self.response['error'] = 0
                        self.response['message'] = 'User successfully signed up and logged in'
                        org_val['closed'] = True
                        cache.set(self.secret,org_val,60)
                        tokens = await self.get_tokens()
                        self.response['data'] = {'verified':True,'tokens':tokens}
                        await self.send(json.dumps(self.response))
                    if text_data['view'] == 'login':
                        self.response['error'] = 0
                        self.response['message'] = 'User successfully Logged in'
                        org_val['closed'] = True
                        cache.set(self.secret,org_val,60)
                        tokens = await self.get_tokens()
                        self.response['data'] = {'verified':True,'tokens':tokens}
                        await self.send(json.dumps(self.response))  
                    await self.close()
                elif verified == False:
                    self.response['error']+=1
                    self.response['message'] = 'OTP is wrong OR expired please try the latest one'
                    await self.send(json.dumps(self.response))       
                else:
                    self.response['error']+=1
                    self.response['message'] = 'Please scan the QR code first'
                    await self.send(json.dumps(self.response))  

    async def program_event(self,event):  
        print('nowhere')
        await self.send(json.dumps({
                'action':'email_confirmed',                        
        }))
    
    async def get_latest_cache(self):
        if not cache.has_key(self.secret):            
            cache.set(self.secret,{'authenticator':0,'app':0,'closed':False})        
        return cache.get(self.secret)

    async def verify_otp(self):
        org_val = await self.get_latest_cache() 
        if 'otp' in org_val:            
            if self.otp == org_val['otp']:
                return True
            else:
                return False         
        else:
            return 404    
    
    @database_sync_to_async
    def save_user_obj(self):
        self.user.save()
    @database_sync_to_async
    def get_user(self):
        User = get_user_model()
        try:
            user = User.objects.get(secret=self.secret)            
            return user
        except:
            return False
            
        
    async def send_otps(self):        
        while True:
            org_val = await self.get_latest_cache() 
            if org_val['closed']:
                del AuthConsumer.entities[self.secret]
                await self.close()
                break
            self.otp = str(np.random.randint(100000, 999999))
            org_val['otp'] = self.otp            
            cache.set(self.secret,org_val,60)
            self.otparr['otp'] = self.otp
            self.otparr['expiry'] = 20            
            await self.send(json.dumps(self.otparr))
            await asyncio.sleep(19)    
    
    @database_sync_to_async
    def get_tokens(self):
        obj = CustomTokenObtainPairSerializer()
        refresh = obj.get_token(self.user)
        tokens = {
            'refresh':str(refresh),
            'access':str(refresh.access_token)
        }
        return tokens