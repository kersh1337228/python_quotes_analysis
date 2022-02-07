from alpha_vantage.timeseries import TimeSeries
from django.db import models


api_key = 'J7JRRVLFS9HZFPBY'


'''Economic market instrument, representing shares,
 obligations, currencies, etc. 
 Contains name and main quotes for certain period.'''
class Instrument(models.Model):
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )
    quotes = models.JSONField()

    def __str__(self):
        return self.name

    def add_quote_by_name(self, name):
        # Parsing quotes data
        time_series = TimeSeries(key=api_key, output_format='json')
        (data, meta_data) = time_series.get_daily(symbol=name, outputsize='full')
        # Adding quotes data to the database
        return self.objects.create(
            name=name,
            quotes={key: {
                'open': data[key]['1. open'],
                'high': data[key]['2. high'],
                'low': data[key]['3. low'],
                'close': data[key]['4. close'],
                'volume': data[key]['5. volume']
            } for key in data}
        )



