from alpha_vantage.timeseries import TimeSeries
from django.db import models
from ui.models import Log


api_key = 'J7JRRVLFS9HZFPBY'


'''Economic market instrument, representing shares,
 obligations, currencies, etc. 
 Contains symbol, main quotes for certain period, price plot.'''
class Share(models.Model):
    symbol = models.CharField(
        max_length=255,
        unique=True,
        blank=False,
        null=False
    )
    quotes = models.JSONField()
    price_plot = models.ImageField(
        upload_to='plots'
    )

    def __str__(self):
        return self.symbol

    def add_quote_by_name(self, symbol):
        # Parsing quotes data
        time_series = TimeSeries(key=api_key, output_format='json')
        (data, meta_data) = time_series.get_daily(symbol=symbol, outputsize='full')
        # Adding quotes data to the database
        return self.objects.create(
            symbol=symbol,
            quotes={key: {
                'open': data[key]['1. open'],
                'high': data[key]['2. high'],
                'low': data[key]['3. low'],
                'close': data[key]['4. close'],
                'volume': data[key]['5. volume']
            } for key in data}
        )


'''Portfolio class containing shares and balance'''
class Portfolio(models.Model):
    name = models.CharField(
        max_length=255,
        blank=False,
        unique=True,
    )
    balance = models.FloatField(
        default=0,
    )
    shares = models.ManyToManyField(
        Share,
        related_name='portfolio_shares',
    )
    logs = models.ManyToManyField(
        Log,
        related_name='portfolio_logs'
    )
    slug = models.SlugField(
        max_length=255,
        blank=False,
        null=False,
        unique=True,
    )
