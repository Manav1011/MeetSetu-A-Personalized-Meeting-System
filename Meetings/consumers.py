import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Meeting

class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):        
        self.meet = self.scope["url_route"]["kwargs"]["meet_uid"]
        meet_obj = await self.get_meet_obj(self.meet)
        if meet_obj:            
            self.group_name = f"chat_{self.meet}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()
    async def disconnect(self,close_code):        
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.close()

    async def receive(self,text_data):
        text_data = json.loads(text_data)    
        if 'type' in text_data:
            if text_data['type'] == 'adminonly' and 'adminonly' in text_data:
                await self.channel_layer.group_send(
                    self.group_name, {"type": "chat.message", "message": text_data}
                )
            if text_data['type'] == 'chat' and 'message' in text_data:
                await self.channel_layer.group_send(
                    self.group_name, {"type": "chat.message", "message": text_data}
                )
            if text_data['type'] == 'file_upload' and 'content' in text_data:
                await self.channel_layer.group_send(
                    self.group_name, {"type": "chat.message", "message": text_data}
                )            
        else:
            await self.send('Please pass the type of the message')
    
    async def chat_message(self, event):
        message = event["message"]        
        await self.send(text_data=json.dumps(message))

    @database_sync_to_async
    def get_meet_obj(self,meet_uid):
        return Meeting.objects.filter(UID=meet_uid).first()

class SignalingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.meet = f'{self.scope["url_route"]["kwargs"]["meet_uid"]}'
        meet_obj = await self.get_meet_obj(self.meet)                
        if meet_obj:            
            self.group_name = f"signaling_{self.meet}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            await self.send(json.dumps({
                'action':'joined'
            }))            
        else:
            await self.close()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        return await super().disconnect(code)

    async def receive(self, text_data):
        text_data = json.loads(text_data)
        if 'action' in text_data:
            if text_data['action'] == 'new_peer':
                # Send notification to every other peer                
                await self.channel_layer.group_send(
                    self.group_name, {"type": "new.peer", "message": text_data,"exclude":self.channel_name}
                )

            if text_data['action'] == 'peer_left':
                await self.channel_layer.group_discard(self.group_name, self.channel_name)                
                await self.send(json.dumps({
                    "action":'you_left'
                }))
                await self.channel_layer.group_send(
                    self.group_name, {"type": "peer.left", 'channel':self.channel_name}
                )
            if text_data['action'] == 'offer' and 'channel_name' in text_data and 'sdp_offer' in text_data:                
                await self.channel_layer.group_send(
                    self.group_name, {"type": "send.offer",'message':text_data,'sender_channel':self.channel_name}
                )

            if text_data['action'] == 'answer' and 'sdp_answer' in text_data and 'sender_channel' in text_data:                
                await self.channel_layer.group_send(
                    self.group_name, {"type": "send.answer",'message':text_data,'channel':self.channel_name}
                )  
            
            if text_data['action'] == 'onicecandidate' and 'channel_name' in text_data and 'candidate' in text_data:
                await self.channel_layer.group_send(
                    self.group_name, {"type": "send.candidate",'message':text_data,'sender_channel':self.channel_name}
                )                
    async def send_candidate(self,event):
        message = event['message']
        channel_name = message['channel_name']
        sender_channel = event['sender_channel']
        message['sender_channel'] = sender_channel
        if self.channel_name == channel_name:
            await self.send(json.dumps(message))

    async def peer_left(self,event):
        message = {'channel_name':event['channel']}
        await self.send(text_data=json.dumps(message))


    async def send_offer(self,event):
        message = event['message']
        channel_name = message['channel_name']
        sender_channel = event['sender_channel']
        message['sender_channel'] = sender_channel                
        if channel_name == self.channel_name:
            await self.send(text_data=json.dumps(message))        
    
    async def send_answer(self,event):
        message = event['message']
        channel_name = event['channel']
        sender_channel = message['sender_channel']
        message['channel_name'] = channel_name
        if sender_channel == self.channel_name:
            await self.send(text_data=json.dumps(message))        

    async def new_peer(self, event):        
        message = event["message"]    
        sender_channel_name = event["exclude"]
        message['sender_channel'] = self.channel_name
        message['new_peer'] = sender_channel_name        
        if self.channel_name != sender_channel_name:
            await self.send(text_data=json.dumps(message))       

    @database_sync_to_async
    def get_meet_obj(self,meet_uid):
        return Meeting.objects.filter(UID=meet_uid).first()