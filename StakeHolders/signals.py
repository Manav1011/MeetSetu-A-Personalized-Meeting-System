from .models import StakeHolder
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()

@receiver(post_save,sender=StakeHolder)
def email_confirmed_receiver(sender,instance,created,**kwargs):
    if not created and instance.email_verified:        
        channel_name = instance.secret        
        async_to_sync(channel_layer.group_send)(channel_name, {"type": "program.event"})