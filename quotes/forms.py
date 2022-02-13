from django import forms
from .models import Portfolio


class PortfolioCreateForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ('name', 'balance')
        widgets = {
            'name': forms.TextInput(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'Portfolio name',
                }
            ),
            'balance': forms.TextInput(
                attrs={
                    'class': 'form-input',
                    'placeholder': 'Portfolio balance',
                }
            )
        }
