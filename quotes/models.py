from alpha_vantage.timeseries import TimeSeries
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from ui.models import Log


api_key = 'J7JRRVLFS9HZFPBY'


'''Portfolio class containing shares and balance'''
class Portfolio(models.Model):
    name = models.CharField(
        max_length=255,
        blank=False,
        unique=True,
    )
    balance = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(100000000.0)
        ]
    )
    shares = models.ManyToManyField(
        'Share',
        related_name='portfolio_shares',
    )
    logs = models.ManyToManyField(
        Log,
        related_name='portfolio_logs'
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    last_updated = models.DateTimeField(
        auto_now=True,
    )
    slug = models.SlugField(
        max_length=255,
        blank=False,
        null=False,
        unique=True,
    )


'''Economic market instrument, representing shares,
 obligations, currencies, etc. 
 Contains symbol, main quotes for certain period, price plot.'''
class Quote(models.Model):
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
    slug = models.SlugField(
        max_length=255,
        unique=True,
        blank=False,
        null=False
    )

    @staticmethod
    def add_quote_by_name(symbol):
        # Parsing quotes data
        time_series = TimeSeries(key=api_key, output_format='json')
        (data, meta_data) = time_series.get_daily(symbol=symbol, outputsize='full')
        # Adding quotes data to the database
        return Quote.objects.create(
            symbol=symbol,
            quotes={key: {
                'open': data[key]['1. open'],
                'high': data[key]['2. high'],
                'low': data[key]['3. low'],
                'close': data[key]['4. close'],
                'volume': data[key]['5. volume']
            } for key in data},
            slug=symbol.replace(' ', '_')
        )


'''Share model used to create portfolios'''
class Share(Quote):
    origin = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name='share_origin'
    )
    amount = models.IntegerField()


    def __str__(self):
        return self.symbol
