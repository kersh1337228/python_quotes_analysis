from django import forms
from .models import Strategy


'''Form to set up your own strategy'''
class CreateStrategyForm(forms.ModelForm):
    class Meta:
        model = Strategy
        fields = ['name', 'long_limit', 'short_limit']

    '''Shares amount limit to borrow field validator'''
    def clean_shares_limit_low(self):
        borrow = self.cleaned_data.get('shares_limit_low')
        if borrow > 0:
            raise forms.ValidationError('Your shares amount limit to borrow can only be negative')
        return borrow
