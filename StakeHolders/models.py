from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import StakeHolderManager
from django.db.models.signals import post_save
from django.dispatch import receiver
import random
import string
# Create your models here.

def generate_backup_codes():
    for _ in range(6):
        x = ''.join(random.choices(string.ascii_letters + string.digits, k=16))    
        yield x

class StakeHolder(AbstractUser):
    username=models.CharField(max_length=20)
    email = models.EmailField(_('email address'),unique=True)
    secret = models.CharField(_("secret"), max_length=128)
    email_verified = models.BooleanField(default=False)
    origin = models.CharField(max_length=10,default='native')
    avatar = models.TextField(default='')

    USERNAME_FIELD='email'
    REQUIRED_FIELDS = []

    objects = StakeHolderManager()

    def __str__(self):
        return self.email
    
class BackupCodes(models.Model):
    user = models.ForeignKey(StakeHolder,on_delete=models.CASCADE)
    code = models.CharField(max_length=16)
    used = models.BooleanField(default=False)

    def __str__(self):
        return self.code
    
class AuthConsumerLogs(models.Model):
    secret = models.TextField()
    entities = models.JSONField(null=True,blank=True)
    
@receiver(post_save, sender=StakeHolder)
def create_backup_codes(sender, instance, created,**kwargs):
    if created:
        for i in generate_backup_codes():
            BackupCodes.objects.create(user=instance,code=i)