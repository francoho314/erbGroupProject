from django import forms
from .models import Book, Order, Review, Customer, Genre, Author
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea)
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    zip_code = forms.CharField(max_length=10)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class BookSearchForm(forms.Form):
    query = forms.CharField(required=False, label='Search Books')
    genre = forms.ModelChoiceField(queryset=Genre.objects.all(), required=False)
    author = forms.ModelChoiceField(queryset=Author.objects.all(), required=False)

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['Rating', 'ReviewText']
        widgets = {
            'ReviewText': forms.Textarea(attrs={'rows': 4}),
        }