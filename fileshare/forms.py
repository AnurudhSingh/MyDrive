from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, PasswordChangeForm, UserChangeForm
from django.contrib.auth.models import User
from .models import File, SharedFile, UserSettings

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'autofocus': True}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

class FileShareForm(forms.ModelForm):
    class Meta:
        model = SharedFile
        fields = '__all__'

    recipient = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),  # Include all users
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(FileShareForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['recipient'].queryset = User.objects.exclude(id=user.id)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']  # Include the fields you want to allow modification

class CustomPasswordChangeForm(PasswordChangeForm):
    pass

class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']

class UserPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = User

class RenameForm(forms.Form):
    new_name = forms.CharField(label='New Name', max_length=255)

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['name', 'file']

    def __init__(self, *args, **kwargs):
        super(FileUploadForm, self).__init__(*args, **kwargs)
        # Customize the form if needed
        self.fields['name'].widget.attrs['placeholder'] = 'Enter file name'
