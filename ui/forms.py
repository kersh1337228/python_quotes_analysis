from django.forms import *

from quotes.models import Portfolio
from .business_logic.utils import get_shares
from .business_logic.analytics import *
from .models import Strategy


'''User interface form, allowing to choose the share name, 
beginning and ending date, strategy to use'''
class UserInterface(Form):
    portfolio = ModelChoiceField(
        queryset=Portfolio.objects.all(),
        to_field_name='slug',
        label='Portfolio',
        error_messages={
            'required': ('You have to choose the portfolio'),
        }, empty_label='(Choose the portfolio)',
    )
    time_interval_start = ChoiceField(
        label='Time Interval',
        choices=get_dates()['start'],
        error_messages={
            'required': ('You have to choose the first date of your time interval'),
        }
    )
    time_interval_end = ChoiceField(
        label='Time Interval',
        choices=get_dates()['end'],
        error_messages={
            'required': ('You have to choose the last date of your time interval'),
        }
    )
    strategy_name = ModelChoiceField(
        queryset=Strategy.objects.all(),
        label='Strategy',
        error_messages={
            'required': ('You have to choose the strategy'),
        }, empty_label='(Choose the strategy)'
    )
    '''Custom validator for time interval'''
    def clean(self):
        cleaned_data = super().clean()
        start_date = datetime.date(*list(map(int, cleaned_data.get('time_interval_start').split('-'))))
        end_date = datetime.date(*list(map(int, cleaned_data.get('time_interval_end').split('-'))))
        if start_date >= end_date:
            raise ValidationError('Wrong time interval')
        return cleaned_data

    '''Making share select-box show the empty variant on get request'''
    def __init__(self, *args, **kwargs):
        super(UserInterface, self).__init__(*args, **kwargs)


'''Form to set up your own strategy'''
class CreateStrategyForm(ModelForm):
    class Meta:
        model = Strategy
        fields = ['name', 'shares_limit_high', 'shares_limit_low', 'buy', 'sell']

    '''Shares amount limit to borrow field validator'''
    def clean_shares_limit_low(self):
        borrow = self.cleaned_data.get('shares_limit_low')
        if borrow > 0:
            raise ValidationError('Your shares amount limit to borrow can only be negative')
        return borrow
