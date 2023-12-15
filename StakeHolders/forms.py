from django.contrib.auth.forms import UserCreationForm,UserChangeForm

from .models import StakeHolder

class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = StakeHolder
        fields = ('email',)

class CustomUserChangeForm(UserChangeForm):

    class Meta(UserChangeForm):
        model = StakeHolder
        fields = ('email',)