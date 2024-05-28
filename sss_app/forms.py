from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'price', 'stock', 'image']
        labels = {
            'name': 'Name',
            'category': 'Category',
            'price': 'Price',
            'stock': 'Stock',
            'image': 'Image',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter product name'}),
            'category': forms.Select(attrs={'placeholder': 'Select category'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Enter price'}),
            'stock': forms.NumberInput(attrs={'placeholder': 'Enter stock quantity'}),
        }

class CheckoutForm(forms.Form):
    street = forms.CharField(label='Street', max_length=100)
    city = forms.CharField(label='City', max_length=100)
    state = forms.CharField(label='State', max_length=2)
    postcode = forms.CharField(label='Postcode', max_length=10)
    credit_card_number = forms.CharField(label='Credit Card Number', max_length=16)
    expiration_date = forms.CharField(label='Expiration Date', max_length=7)
    cvv = forms.CharField(label='CVV', max_length=3)
