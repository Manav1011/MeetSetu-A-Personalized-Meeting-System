from django.db import models
import random,string
from StakeHolders.models import StakeHolder

# Create your models here.

def generate_UID():    
    return ''.join(random.choices(string.ascii_letters + string.digits, k=64))

MEETING_TYPES = [
    ('public', 'Public Meeting'),
    ('private', 'Private Meeting'),
    ('asktojoin', 'Ask To Join Meeting'),
    ('onetoone', 'One To One Meeting'),
]

MEETING_STATUS = [
    ('active', 'Active'),
    ('ended', 'Ended'),
    ('upcoming', 'Upcoming'),
]

class Meeting(models.Model):
    UID = models.TextField(default=generate_UID)    
    host = models.ForeignKey(StakeHolder, on_delete=models.DO_NOTHING, related_name='hosted_meetings')    
    allowed_participants = models.ManyToManyField(StakeHolder, related_name='allowed_meetings')
    blacklisted_participants = models.ManyToManyField(StakeHolder, related_name='blacklisted_meetings')
    type = models.CharField(choices = MEETING_TYPES,max_length=15)
    status = models.CharField(choices = MEETING_STATUS,max_length=15)
    created_at = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)

    def __str__(self):
        return f"{self.type}_{self.UID}"