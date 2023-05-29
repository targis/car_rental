from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import DateInput

from .models import *
from .widgets import ImagePreviewWidget, StarRatingWidget


class NewUserForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=False, help_text="Optional.")

    class Meta:
        model = User
        fields = ("username", "first_name", "password1", "password2")


class UserForm(UserCreationForm):
    # email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "password1", "password2")


class ProfileForm(forms.ModelForm):
    tel = forms.RegexField(regex="^0\d{9}$", max_length=10, min_length=10, required=True,
                           help_text="Enter a tel number in such format 0991234567")
    name = forms.CharField(max_length=30, required=False, help_text="Optional.")
    photo = forms.ImageField(widget=ImagePreviewWidget, required=False, help_text="It will be your profile picture.")

    class Meta:
        model = Profile
        fields = ("tel", "name",  "photo",)


class OrderForm(forms.ModelForm):
    date_start = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))
    date_end = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}))

    class Meta:
        model = Order
        fields = ("date_start", "date_end")


class ReviewForm(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea, label='Write your review')
    # rate = forms.SeleField(widget=StarRatingWidget, label='Write your review')

    class Meta:
        model = Review
        fields = ('text',)
