import datetime
import os
import pandas
from alpha_vantage.timeseries import TimeSeries
from django.core.files import File
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from ui.business_logic.analytics import build_candle_plot
from ui.models import Log


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

    # Returns the first and the last dates available in quotes
    # to analyse portfolios with multiple different instruments
    def get_quotes_dates(self):
        return pandas.date_range(
            max([datetime.datetime.strptime(
                list(share.origin.quotes.keys())[0],
                '%Y-%m-%d'
            ) for share in self.shares.all()]),
            min([datetime.datetime.strptime(
                list(share.origin.quotes.keys())[-1],
                '%Y-%m-%d'
            ) for share in self.shares.all()])
        ).strftime('%Y-%m-%d').tolist()


    def __str__(self):
        return self.name


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
    name = models.CharField(
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

    # API key for alpha_vantage api
    api_key = 'J7JRRVLFS9HZFPBY'

    # Method to parse quotes of the instrument by its symbol
    # and then create a database note and model instance
    @staticmethod
    def add_quote_by_symbol(symbol, name, slug):
        # Parsing quotes data
        time_series = TimeSeries(key=Quote.api_key, output_format='json')
        (data, meta_data) = time_series.get_daily(symbol=symbol, outputsize='full')
        quotes = last = {}  # Formatting quotes
        for date in pandas.date_range(
            start=datetime.datetime.strptime(list(data.keys())[-1], '%Y-%m-%d'),
            end=datetime.datetime.strptime(list(data.keys())[0], '%Y-%m-%d'),
            freq='D'
        ):
            key = date.strftime('%Y-%m-%d')
            if data.get(key, None):
                last = {
                    'open': float(data[key]['1. open']),
                    'high': float(data[key]['2. high']),
                    'low': float(data[key]['3. low']),
                    'close': float(data[key]['4. close']),
                    'volume': float(data[key]['5. volume']),
                    'non-trading': False
                }
            else:
                last['non-trading'] = True
            quotes[key] = last
        # Adding quotes data to the database
        quote = Quote.objects.create(
            symbol=symbol,
            name=name,
            quotes=quotes,
            slug=slug
        )  # Building ohlc quotes plot
        quote.build_price_plot()
        return quote

    # Building price ohlc plot of the instrument using its quotes
    def build_price_plot(self):
        build_candle_plot(self.quotes)
        self.price_plot.save(
            f'{self.slug}_price_plot.png',
            File(open('ui/business_logic/plot.png', 'rb'))
        )  # Attaching plot image
        # Deleting unnecessary plot picture
        os.remove(f'ui/business_logic/plot.png')
        self.save()

    def __str__(self):
        return self.name


'''Share model used to create portfolios'''
class Share(models.Model):
    # Link to the original instrument model
    origin = models.ForeignKey(
        Quote,
        on_delete=models.CASCADE,
        related_name='share_origin'
    )
    # Amount of quotes in the portfolio
    amount = models.IntegerField()
