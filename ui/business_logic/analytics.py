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
                'percent': (logs[-1].balance / logs[0].balance - 1) * 100,
                'currency': round(logs[-1].balance - logs[0].balance, 2)
            },
            'shares': [
                {
                    'percent': (share.origin.quotes[list(
                        share.origin.quotes.keys()
                    )[-1]]['close'] / share.origin.quotes[list(
                        share.origin.quotes.keys()
                    )[-1]]['close'] - 1) * 100,
                    'currency': round(share.origin.quotes[list(
                        share.origin.quotes.keys()
                    )[-1]]['close'] - share.origin.quotes[list(
                        share.origin.quotes.keys()
                    )[-1]]['close'], 2)
                }
                for share in portfolio.shares]
        },
        strategy=strategy,
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
    for share in portfolio.shares:
        build_candle_plot( # Building share price ohlc candle plot
            {date.strftime('%Y-%m-%d'): share.origin.quotes[
                date.strftime('%Y-%m-%d')
            ] for date in date_range},
            f'{share.origin.name}.png'
        ) # Attaching share price plot to log model instance
        image = Image.objects.create()
        image.attach_image(f'{share.origin.name}.png')
    log_instance.save() # Applying log model instance changes
    portfolio.logs.add(log_instance) # Attaching log to the portfolio


def log(portfolio_image, date_range, strategy):
    # Taking class instance copy for further work with the original one,
    # not being afraid to change logged data
    logs = [deepcopy(portfolio_image)]
    for share in portfolio_image.shares:
        for date in date_range:
            strategy.buy_or_sell(portfolio_image, share, date)
            logs.append(deepcopy(portfolio_image))
    return logs


'''Building the plot, showing the total savings amount and
shares average_cost, depending on the time point'''
def plot_builder(portfolio, date_range, logs):
    # x-axis data (dates)
    dates_data = mdates.date2num(pandas.DatetimeIndex(
        date_range
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
        mdates.MonthLocator(bymonth=(1, 13))
    )
    shares_amount_subplot.xaxis.set_minor_locator(
        mdates.MonthLocator()
    )
    for label in shares_amount_subplot.get_xticklabels(which='major'):
        label.set(rotation=45, horizontalalignment='right')
    # Getting subplot lines
    balance_line = balance_subplot.plot(
        dates_data,
        numpy.array([log.balance for log in logs]),
        label='Balance'
    )
    shares_lines = [shares_amount_subplot.plot(
        dates_data,
        numpy.array([log.shares[i].amount for log in logs]),
        label=f'{portfolio.shares[i].origin.name}'
    ) for i in range(len(portfolio.shares))]
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


def build_candle_plot(quotes, filename='plot.png'):
    # Formatting data
    data = pandas.DataFrame({
        'Open': [value['open'] for value in quotes.values()],
        'High': [value['high'] for value in quotes.values()],
        'Low': [value['low'] for value in quotes.values()],
        'Close': [value['close'] for value in quotes.values()],
        'Volume': [value['volume'] for value in quotes.values()],
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


# # Creating the first plot
#     cost_plot = plt.subplot(2, 1, 1)
#     cost_plot.set_title('Share cost', color='w')
#     dats = pandas.to_datetime(time).to_series().apply(matplotlib.dates.date2num)
#     candlestick_ohlc(cost_plot, zip(dats, [point['open'] for point in points],
#                                     [point['high'] for point in points],
#                                     [point['low'] for point in points],
#                                     [point['close'] for point in points]),
#                      width=1, colorup='g', colordown='r'
#                      )
#
#     # Setting x-axis data as formatted date
#     plt.gca().xaxis.set_visible(False)
#
#     # Setting axis labels
#     plt.xlabel('Date')
#     plt.ylabel('RUB')
#
#     # Setting plot dark color-scheme
#     plt.gca().set_facecolor((0.086, 0.086, 0.086))
#     cost_plot.spines['bottom'].set_color('w')
#     cost_plot.spines['top'].set_color('w')
#     cost_plot.spines['left'].set_color('w')
#     cost_plot.spines['right'].set_color('w')
#     cost_plot.xaxis.label.set_color('w')
#     cost_plot.yaxis.label.set_color('w')
#     cost_plot.tick_params(axis='x', colors='w')
#     cost_plot.tick_params(axis='y', colors='w')
#
#     # Creating the second plot
#     money_plot = plt.subplot(2, 1, 2)
#     plt.plot(time, money, '-', color='r')
#     money_plot.set_title('Balance', color='w')
#
#     plt.gca().xaxis.set_visible(False)
#
#     plt.xlabel('Time interval')
#     plt.ylabel('RUB')
#
#     # Recoloring plot (dark theme)
#     plt.gca().set_facecolor((0.086, 0.086, 0.086))
#     money_plot.spines['bottom'].set_color('w')
#     money_plot.spines['top'].set_color('w')
#     money_plot.spines['left'].set_color('w')
#     money_plot.spines['right'].set_color('w')
#     money_plot.xaxis.label.set_color('w')
#     money_plot.yaxis.label.set_color('w')
#     money_plot.tick_params(axis='x', colors='w')
#     money_plot.tick_params(axis='y', colors='w')
#     fig = plt.figure(1)
#     fig.patch.set_facecolor((0.086, 0.086, 0.086))
#
#     # Saving the obtained plot
#     plt.savefig('ui/static/plots/plot.png')
#     plt.close()


# '''The main-hub function'''
# def main(raw_filename, time_interval, raw_strategy):
#
#     # Initializing data
#     strategy = raw_strategy
#     filename = get_filename(raw_filename)
#     points = get_points(filename)
#     logs = briefcase_logging(points, strategy)
#
#     # Getting the dates list
#     dates = [point['date'] for point in points]
#
#     # Initializing data to build plot
#     start_date = datetime.date(*list(map(int, time_interval['start'].split('-'))))
#     end_date = datetime.date(*list(map(int, time_interval['end'].split('-'))))
#     start_index, end_index = get_date_indexes(start_date, end_date, dates)
#     time = numpy.array(dates[3:][start_index:end_index + 1])
#     logs = logs[start_index:end_index + 1]
#     cost = numpy.array([i.cost for i in logs])
#     money = numpy.array([i.liquidation_savings() for i in logs])
#
#     plot_builder(time, cost, points, money)
#
#     share_delta_percent = logs[-1].cost / logs[0].cost - 1
#     share_delta_money = round(logs[-1].cost - logs[0].cost, 2)
#     balance_delta_percent = (logs[-1].liquidation_savings() / logs[0].liquidation_savings() - 1)
#     balance_delta_money = round(logs[-1].liquidation_savings() - logs[0].liquidation_savings(), 2)
#
#     return {
#         'share_delta': {
#             'share_delta_percent': share_delta_percent,
#             'share_delta_money': share_delta_money,
#         },
#         'balance_delta': {
#             'balance_delta_percent': balance_delta_percent,
#             'balance_delta_money': balance_delta_money,
#         },
#         'strategy_name': raw_strategy['name'],
#         'share_name': filename.split('/')[-1][:-4].capitalize(),
#         'time_interval_start': dates[0],
#         'time_interval_end': dates[-1],
#     }


# if __name__ == '__main__':
#     plot_builder()
