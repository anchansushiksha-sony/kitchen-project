from django import forms
from products.models import Rating

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['value']
        widgets = {
            'value': forms.NumberInput(attrs={'min': 1, 'max': 5})
        }
