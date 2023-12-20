from .models import StakeHolder
from rest_framework.response import Response
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view
import qrcode
import qrcode.image.svg
from django.conf import settings as django_settings
from django_ratelimit.decorators import ratelimit
from django.contrib.auth import authenticate
import smtplib
from email.mime.multipart import MIMEMultipart
import io
from django.core.mail import send_mail
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import json
from threading import Thread
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.http import HttpResponse
import jwt
import random, string
import base64 
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
# Create your views here.


def generate_key(email,password):
    text = f"{email}:{password}"
    generated_hash = x = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    return generated_hash


def send_email(receiver,secret):    
    sender_email = django_settings.EMAIL_HOST_USER
    sent = False
    url = f'http://172.16.17.87:8000/stakeholder/confirm_email?secret={secret}'
    try:
        send_mail('Email Confirmation Link',url, from_email=sender_email,recipient_list=[receiver])
        sent=True
    except Exception as e:
        print(e)        
        sent = False
    return sent

def email_confirmed(request):
    if request.method == 'GET':            
        try:
            creds = request.GET
            if 'secret' in  creds:
                user = StakeHolder.objects.get_user_by_key(creds['secret'])
                if user:
                    user.email_verified = True
                    user.is_active = True
                    user.save()
                    return HttpResponse('Your email has been verified')
                else:
                    return HttpResponse('User does not exist')
            else:
                raise Exception('Please provide all the parameters')
        except Exception as e:
            return HttpResponse(e)


def get_qr_svg(secret):
    factory = qrcode.image.svg.SvgPathImage
    img = qrcode.make(secret, image_factory=factory)
    svg_code = img.to_string(encoding='unicode')

    return svg_code

def xor_decipher(ciphertext, key):
    key_bytes = key.encode('utf-8')
    ciphertext_bytes = base64.b64decode(ciphertext)    
    decrypted_bytes = [c ^ key_bytes[i % len(key_bytes)] for i, c in enumerate(ciphertext_bytes)]
    decrypted_data = bytes(decrypted_bytes).decode('utf-8')        
    return decrypted_data

def decryption_decorator(func):
    def wrapper(*args,**kwargs):
        key = args[0].data.get('secret')        
        data = args[0].data['data']        
        if key:
            data_decrypted  = xor_decipher(data,key)                    
            args[0].data['data']  = json.loads(data_decrypted)
        result = func(*args, **kwargs)
        return result
    return wrapper

@ratelimit(key='ip', rate='5/m', block=True)
@api_view(['POST'])
@decryption_decorator
def SignupUser(request):
    response = {'error':False, 'message':'', 'data':{}}
    creds = request.data.get('data')   
    try:
        if 'email' in creds and 'password' in creds and 'username' in creds:
            email = creds['email']
            password = creds['password']  
            username = creds['username']
            # Generate secret key from email and password
            # Create or get the users
            user,created = StakeHolder.objects.get_or_create(email=email)
            if created:
                user.set_password(password)
                user.username = username
                secret = generate_key(email,password)
                user.secret = secret
                user.origin = 'native'
                user.save()
            # Generate QR code from it                         
            if not user.is_active or not user.email_verified:
                response['data']['secret'] = user.secret
                response['data']['verified'] = 0
                Thread(target=send_email,args=(email,user.secret)).start()
                response['message'] = 'Please verifiy your email!!'
            else:
                raise Exception("You've already signed up")
        else:
            raise Exception('Credentials missing')
    except Exception as e:
        response['error'] = True
        response['message']=str(e)
        return Response(response,status=500)
    return Response(response,status=200)

@ratelimit(key='ip', rate='5/m', block=True)
@api_view(['POST'])
def SignupUserGoogle(request):
    response = {'error':False, 'message':'', 'data':{}}
    creds = request.data    
    try:
        if 'credential' in creds:
            credentials = creds.get('credential')
            credentials_decoded = jwt.decode(credentials, options={"verify_signature": False})       
            email = credentials_decoded.get('email')
            email_verified = credentials_decoded.get('email_verified')
            username = credentials_decoded.get('name')
            avatar = credentials_decoded.get('picture')
            # Generate secret key from email and password
            # Create or get the user
            user,created = StakeHolder.objects.get_or_create(email=email)
            if created:
                user.set_password(email)
                secret = generate_key(email,email)\
                
                user.secret = secret
                user.email_verified = email_verified
                user.username = username
                user.avatar = avatar                
                user.origin = 'google'
                user.save()
            if user.origin != 'google':
                raise Exception('User already exists')
            # Generate QR code from it                         
            svg_code = get_qr_svg(user.secret)
            response['message'] = 'Email is already verified'
            response['data']['email_verified'] = 1
            response['data']['svg'] = svg_code
            response['data']['secret'] = user.secret            
        else:
            raise Exception('Credentials missing')
    except Exception as e:
        response['error']=True
        response['message']=str(e)
    return Response(response)

# @ratelimit(key='ip', rate='10/m', block=True)
@api_view(['POST'])
@decryption_decorator
def LoginUser(request):
    response = {'error':False, 'message':'', 'data':{}}
    creds = request.data.get('data')
    print(creds)
    try:
        if 'email' in creds and 'password' in creds:
            email = creds['email']
            password = creds['password']
            user = authenticate(email=email,password=password)
            if user:
                secret = user.secret
                if user.is_active and user.email_verified:
                    svg_code = get_qr_svg(secret)
                    response['data']['email_verified'] = True
                    response['data']['svg'] = svg_code
                    response['data']['secret'] = secret
                    response['data']['email'] = user.email
                else:                    
                    response['data']['email_verified'] = False
                    Thread(target=send_email,args=(email,user.secret)).start()
                    response['data']['secret'] = secret
                    raise Exception('Please verifiy your email!!')
            else:
                raise Exception('User does not exist')
        else:
            raise Exception('Credentials missing')
    except Exception as e:
        response['error'] = True
        response['message'] = str(e)
        return Response(response,status=500)
    return Response(response,status=200)


@ratelimit(key='ip', rate='5/m', block=True)
@api_view(['POST'])
def LoginWithAuthenticator(request):
    response = {'error':False, 'message':'', 'data':{}}
    creds = request.data
    try:
        if 'email' in creds and 'password' in creds:
            email = creds['email']
            password = creds['password']
            user = authenticate(email=email,password=password)
            if user and user.is_active:
                if not user.secret:
                    raise Exception('Please Signup into the platform first.')
                secret = user.secret                
                response['data']['secret'] = secret
            else:
                raise Exception('User does not exist')
        else:
            raise Exception('Credentials missing')
    except Exception as e:
        response['error'] = True
        response['message'] = str(e)
    return Response(response)

@ratelimit(key='ip', rate='5/m', block=True)
@api_view(['POST'])
def LoginWithAuthenticatorGoogle(request):
    response = {'error':False, 'message':'', 'data':{}}
    creds = request.data
    try:
        if 'ID Token' in creds:
            token_encoded = creds['ID Token']
            token_decoded = jwt.decode(token_encoded, options={"verify_signature": False})            
            if token_decoded:            
                email = token_decoded['email']
                user = authenticate(email=email,password=email)
                if user and user.is_active:
                    if not user.secret:
                        raise Exception('Please Signup into the platform first.')
                    secret = user.secret                
                    response['data']['secret'] = secret
                else:
                    raise Exception('User does not exist')
            else:
                raise Exception('Invalid Token')
        else:
            raise Exception('Credentials missing')
    except Exception as e:
        response['error'] = True
        response['message'] = str(e)
    return Response(response)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.username                
        return token
