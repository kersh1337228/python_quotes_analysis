from copy import deepcopy
import datetime
import numpy
import pandas
import matplotlib.pyplot as plt
import matplotlib.gridspec as grd
import matplotlib.dates as mdates
import mplfinance
from django.core.files import File
from ui.models import Log, Image


'''Copies the portfolio and share to allow the analyser
 function to change the data of the class 
 instance but not of the database'''
class Portfolio_Image:
    class Share_Image:
        def __init__(self, share):
            self.origin = share.origin
            self.amount = 0

    def __init__(self, portfolio):
        self.balance = portfolio.balance
        self.shares = [
            self.Share_Image(share) for share in portfolio.shares.all()
        ]
        self.cost = self.balance

    def set_cost(self, date):
        cost = self.balance
        for share in self.shares:
            cost += share.amount * share.origin.quotes[date]['close']
        self.cost = cost

    def __str__(self):
        return str({
            'balance': self.balance,
            'shares': [{
                'amount': share.amount,
                'name': share.origin.name
            } for share in self.shares],
            'cost': self.cost
        })


'''Analyser function, made to analyse the
 quotes data using different strategies'''
def analyse(portfolio, time_interval_start, time_interval_end, strategy):
    date_range = pandas.date_range(
        datetime.datetime.strptime(
            time_interval_start,
            '%Y-%m-%d'
        ),
        datetime.datetime.strptime(
            time_interval_end,
            '%Y-%m-%d'
        ) - datetime.timedelta(days=3),
    ) # Converting dates to date range
    logs = log(
        Portfolio_Image(portfolio),
        date_range,
        strategy,
    ) # Analysing and logging
    log_instance = Log.objects.create(
        time_interval_start=time_interval_start,
        time_interval_end=time_interval_end,
        price_deltas={
            'balance': {
                'percent': (logs[-1].cost / logs[0].cost - 1) * 100,
                'currency': round(logs[-1].cost - logs[0].cost, 2)
            },
            'shares': [
                {
                    'percent': (share.origin.quotes[time_interval_start]['close'] /
                                share.origin.quotes[time_interval_end]['close'] - 1) * 100,
                    'currency': round(
                        share.origin.quotes[time_interval_start]['close'] -
                        share.origin.quotes[time_interval_end]['close'], 2
                    )
                }
                for share in portfolio.shares.all()]
        },
        strategy=strategy,
        portfolio=portfolio,
    ) # Creating log model instance to save analysis data
    plot_builder(
        portfolio,
        date_range,
        logs,
    ) # Building balance change plot
    log_instance.balance_plot.save(
        'balance.png',
        File(open('ui/business_logic/balance.png', 'rb'))
    ) # Attaching balance change plot to log model instance
    for share in portfolio.shares.all():
        build_candle_plot( # Building share price ohlc candle plot
            {date: share.origin.quotes[date] for date in get_date_range(
                share.origin.quotes, time_interval_start, time_interval_end
            )},
            f'{share.origin.name}.png'
        ) # Attaching share price plot to log model instance
        image = Image.objects.create()
        image.attach_image(f'{share.origin.name}.png')
        log_instance.share_plots.add(image)
    log_instance.save() # Applying log model instance changes
    portfolio.logs.add(log_instance) # Attaching log to the portfolio
    portfolio.save()
    return log_instance


def get_date_range(quotes, time_interval_start, time_interval_end):
    return [date for date in quotes.keys() if datetime.datetime.strptime(date, '%Y-%m-%d') >=
            datetime.datetime.strptime(time_interval_start, '%Y-%m-%d') and
            datetime.datetime.strptime(date, '%Y-%m-%d') <=
            datetime.datetime.strptime(time_interval_end, '%Y-%m-%d')]


'''Log function uses the strategy to analyse
 the portfolio on the chosen time period'''
def log(portfolio_image, date_range, strategy):
    # Taking class instance copy for further work with the original one,
    # not being afraid to change logged data
    logs = [deepcopy(portfolio_image)]
    for date in date_range:
        for index in range(len(portfolio_image.shares)):
            portfolio_image = strategy.buy_or_sell(portfolio_image, index, date)
            print(portfolio_image)
        logs.append(deepcopy(portfolio_image))
    return logs


'''Building the plot, showing the total savings amount and
shares average_cost, depending on the time point'''
def plot_builder(portfolio, date_range, logs):
    # x-axis data (dates)
    dates_data = mdates.date2num(date_range.insert(
            0, date_range[0] - datetime.timedelta(days=1)
    ).to_pydatetime())
    # Creating balance and shares amount figures and subplots
    fig = plt.figure()
    gridspec = grd.GridSpec(
        nrows=2, ncols=1, height_ratios=[3, 1], hspace=0
    ) # Building subplot grid
    balance_subplot = plt.subplot(gridspec[0]) # Balance subplot
    shares_amount_subplot = plt.subplot(gridspec[1]) # Shares amount subplot
    # Setting x-axis date format
    shares_amount_subplot.xaxis.set_major_formatter(
        mdates.DateFormatter('%Y-%m-%d')
    )
    shares_amount_subplot.xaxis.set_major_locator(
        mdates.DayLocator(interval=((date_range[-1] - date_range[0]).days // 6))
    )
    shares_amount_subplot.xaxis.set_minor_locator(
        mdates.DayLocator()
    )
    for label in shares_amount_subplot.get_xticklabels(which='major'):
        label.set(rotation=45, horizontalalignment='right')
    # Getting subplot lines
    balance_line = balance_subplot.plot(
        dates_data,
        numpy.array([log.cost for log in logs]),
        label='Balance',
        color='r'
    )
    shares_lines = [shares_amount_subplot.plot(
        dates_data,
        numpy.array([log.shares[index].amount for log in logs]),
        label=f'{portfolio.shares.all()[index].origin.name}'
    )[0] for index, share in enumerate(portfolio.shares.all())]
    # Setting vertical axes labels
    balance_subplot.set_ylabel('Balance')
    shares_amount_subplot.set_ylabel('Amount')
    # Setting up legend
    leg = fig.legend(
        handles=shares_lines,
        loc='upper right',
        facecolor='#161a1e',
        edgecolor='#161a1e',
        framealpha=1
    ) # Customising legend text color
    for text in leg.get_texts():
        text.set_color('#838d9b')
    # Deleting unnecessary borders
    balance_subplot.label_outer()
    shares_amount_subplot.label_outer()
    # Figure color
    fig.set_facecolor('#161a1e')
    # Subplots foreground color
    balance_subplot.set_facecolor('#161a1e')
    shares_amount_subplot.set_facecolor('#161a1e')
    # Subplots grid color
    balance_subplot.grid(color='#1a1e23')
    shares_amount_subplot.grid(color='#1a1e23')
    # Subplots border colors
    balance_subplot.spines['bottom'].set_color('#838d9b')
    balance_subplot.spines['top'].set_color('#838d9b')
    balance_subplot.spines['left'].set_color('#838d9b')
    balance_subplot.spines['right'].set_color('#838d9b')
    shares_amount_subplot.spines['bottom'].set_color('#838d9b')
    shares_amount_subplot.spines['top'].set_color('#838d9b')
    shares_amount_subplot.spines['left'].set_color('#838d9b')
    shares_amount_subplot.spines['right'].set_color('#838d9b')
    # Subplots axe tick colors
    balance_subplot.tick_params(axis='x', colors='#838d9b')
    balance_subplot.tick_params(axis='y', colors='#838d9b')
    shares_amount_subplot.tick_params(axis='x', colors='#838d9b')
    shares_amount_subplot.tick_params(axis='y', colors='#838d9b')
    # Subplots label colors
    balance_subplot.xaxis.label.set_color('#838d9b')
    balance_subplot.yaxis.label.set_color('#838d9b')
    shares_amount_subplot.xaxis.label.set_color('#838d9b')
    shares_amount_subplot.yaxis.label.set_color('#838d9b')
    # Increasing bottom space below the plots
    plt.subplots_adjust(bottom=0.2)
    plt.savefig(f'ui/business_logic/balance.png', dpi=1200)
    plt.close()


'''Building quotes ohlc candle plot'''
def build_candle_plot(quotes, filename='plot.png'):
    # Formatting data
    data = pandas.DataFrame({
        'Open': [value['open'] for value in list(quotes.values())[::-1]],
        'High': [value['high'] for value in list(quotes.values())[::-1]],
        'Low': [value['low'] for value in list(quotes.values())[::-1]],
        'Close': [value['close'] for value in list(quotes.values())[::-1]],
        'Volume': [value['volume'] for value in list(quotes.values())[::-1]],
    }, index=pandas.DatetimeIndex(quotes.keys()))
    # Creating and customising plot
    plot, axes = mplfinance.plot(
        data=data, type='candle',
        style=mplfinance.make_mpf_style(
            marketcolors=mplfinance.make_marketcolors(
                up='#0ecb81', down='#f6465d', edge='none',
                volume={'up': '#0ecb81', 'down': '#f6465d'},
                wick={'up': '#0ecb81', 'down': '#f6465d'},
            ),
            facecolor='#161a1e', edgecolor='#474d57',
            figcolor='#161a1e', gridcolor='#1a1e23',
        ),
        volume=True, returnfig=True
    )
    for axe in axes: # Changing axes colors
        axe.tick_params(labelcolor='#838d9b')
        axe.set_ylabel(axe.get_ylabel(), color='#838d9b')
    plot.savefig(f'ui/business_logic/{filename}', dpi=1200)
