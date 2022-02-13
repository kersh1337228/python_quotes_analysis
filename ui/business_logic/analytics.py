import csv
import datetime
import re
import matplotlib.dates
import numpy
import matplotlib.pyplot as plt
import pandas
from mpl_finance import candlestick_ohlc

'''Briefcase class, storing the strategy,
money amount, shares amount and shares cost,
depending on the time point'''
class Briefcase:

    class Log:
        def __init__(self, money, shares_amount, cost, avg_cost):
            self.money = money
            self.shares_amount = shares_amount
            self.cost = cost
            self.avg_cost = avg_cost

        def liquidation_savings(self):
            return self.money + self.shares_amount * self.cost

        def average_savings(self):
            return self.money + self.shares_amount * self.avg_cost

        def __str__(self):
            return str({
                'money': self.money,
                'shares_amount': self.shares_amount,
                'avg_cost': self.avg_cost
            })

    def __init__(self, strategy, start_cost):
        self.strategy = strategy
        self.logs = [self.Log(
            strategy['shares_limit_high'] * start_cost,
            0,
            start_cost,
            start_cost
        )]

    '''Returns current share average cost,
    based on previous logs data'''
    def avg_cost_counter(self):
        cost = 0
        amount = 0
        for log in self.logs:
            cost += log.shares_amount * log.cost
            amount += log.shares_amount
        return cost / amount if amount != 0 else 0

    '''Buys or sells shares, depending on 3 previous logs data'''
    def buy_or_sell(self, shares_amount, cost):
        amount = 0
        if self.logs[-1].shares_amount + shares_amount > self.strategy['shares_limit_high'] \
                or self.logs[-1].shares_amount + shares_amount < self.strategy['shares_limit_low'] \
                and shares_amount:
            for i in range(abs(shares_amount)):
                if shares_amount > 0 and self.logs[-1].shares_amount + amount > self.strategy['shares_limit_high'] \
                        or self.logs[-1].shares_amount + amount < self.strategy['shares_limit_low']:
                    amount += 1
                if shares_amount < 0 and self.logs[-1].shares_amount + amount > self.strategy['shares_limit_high'] \
                        or self.logs[-1].shares_amount + amount < self.strategy['shares_limit_low']:
                    amount -= 1
        else:
            amount = shares_amount
        self.logs.append(self.Log(
            self.logs[-1].money - amount * cost,
            self.logs[-1].shares_amount + amount,
            cost,
            0,
        ))
        self.logs[-1].avg_cost = self.avg_cost_counter() if shares_amount > self.strategy['shares_limit_low'] \
            else self.logs[-2].avg_cost

    def __str__(self):
        return str(list(map(str, self.logs)))


'''The function to get the list of dates
to show this list in select-box on web-page'''
def get_dates():
    points = get_points('gazprom')
    start = [(i['date'], i['date'].strftime('%d/%m/%Y')) for i in points]
    end = [(i['date'], i['date'].strftime('%d/%m/%Y')) for i in points][3:]
    return {'start': start, 'end': end}


'''The function to convert the proper string into the dictionary
"{<string:key>: <int:value>, ...}"'''
def string_to_dict(string):
    pairs = string[1:-1].split(',')
    regular = r'^[ ]?(?P<key>\'[\w]+\'): (?P<value>[\w]+)$'
    dictionary = {}
    for pair in pairs:
        key = re.search(regular, pair)['key'][1:-1]
        value = int(re.search(regular, pair)['value'])
        dictionary[key] = value
    return dictionary


'''Formatted .csv file name getter'''
def get_filename(filename):
    if re.match(r'^(static/csv/)?([\w]+)(\.csv)?$', filename):
        filename = re.findall(r'^(static/csv/)?([\w]+)(\.csv)?$', filename)[0][1]
        return 'static/csv/' + filename + '.csv'
    else:
        print('Wrong csv filename')
        exit()

'''Time points list getter, where time point is a dictionary
with date, open, high, low and close costs'''
def get_points(filename):
    points = []
    with open(get_filename(filename), encoding='utf-8') as file:
        reader = csv.reader(file, delimiter=';')
        counter = 0
        for row in reader:
            if counter == 0:
                counter += 1
                continue
            points.append({
                'date': datetime.date(*list(map(int, row[0].split('.')[::-1]))),
                'open': float(row[2]),
                'high': float(row[3]),
                'low': float(row[4]),
                'close': float(row[5]),
                'volume': int(row[6]),
            })
        file.close()
    return points


'''Logging the data, depending on the chosen strategy,
basically is equal to data analysis'''
def briefcase_logging(points, strategy):
    briefcase = Briefcase(strategy, points[3]['close'])
    for i in range(len(points) - 3):
        count = 0
        for j in range(i, i + 3):
            if points[i + 3]['close'] > points[j]['high']:
                count += briefcase.strategy['buy']
            elif points[i + 3]['close'] < points[j]['low']:
                count -= briefcase.strategy['sell']
        briefcase.buy_or_sell(count, points[i + 3]['close'])
    logs = briefcase.logs[1:]
    return logs


'''Returns the start and end indexes 
to work with proper time interval,
cause all shares date fields are different'''
def get_date_indexes(start, end, dates):
    start_index = 0
    end_index = 0
    print(start)
    print(end)
    for i in range(len(dates)):
        if start >= dates[i]:
            start_index = i
    for i in range(len(dates) - 1, -1, -1):
        if end <= dates[i]:
            end_index = i
    return (start_index, end_index)


'''Building the plot, showing the total savings amount and
shares average_cost, depending on the time point'''
def plot_builder(time, cost, points, money):
    # Creating the first plot
    cost_plot = plt.subplot(2, 1, 1)
    cost_plot.set_title('Share cost', color='w')
    dats = pandas.to_datetime(time).to_series().apply(matplotlib.dates.date2num)
    candlestick_ohlc(cost_plot, zip(dats, [point['open'] for point in points],
                                    [point['high'] for point in points],
                                    [point['low'] for point in points],
                                    [point['close'] for point in points]),
                     width=1, colorup='g', colordown='r'
                     )

    # Setting x-axis data as formatted date
    plt.gca().xaxis.set_visible(False)

    # Setting axis labels
    plt.xlabel('Date')
    plt.ylabel('RUB')

    # Setting plot dark color-scheme
    plt.gca().set_facecolor((0.086, 0.086, 0.086))
    cost_plot.spines['bottom'].set_color('w')
    cost_plot.spines['top'].set_color('w')
    cost_plot.spines['left'].set_color('w')
    cost_plot.spines['right'].set_color('w')
    cost_plot.xaxis.label.set_color('w')
    cost_plot.yaxis.label.set_color('w')
    cost_plot.tick_params(axis='x', colors='w')
    cost_plot.tick_params(axis='y', colors='w')

    # Creating the second plot
    money_plot = plt.subplot(2, 1, 2)
    plt.plot(time, money, '-', color='r')
    money_plot.set_title('Balance', color='w')

    plt.gca().xaxis.set_visible(False)

    plt.xlabel('Time interval')
    plt.ylabel('RUB')

    # Recoloring plot (dark theme)
    plt.gca().set_facecolor((0.086, 0.086, 0.086))
    money_plot.spines['bottom'].set_color('w')
    money_plot.spines['top'].set_color('w')
    money_plot.spines['left'].set_color('w')
    money_plot.spines['right'].set_color('w')
    money_plot.xaxis.label.set_color('w')
    money_plot.yaxis.label.set_color('w')
    money_plot.tick_params(axis='x', colors='w')
    money_plot.tick_params(axis='y', colors='w')
    fig = plt.figure(1)
    fig.patch.set_facecolor((0.086, 0.086, 0.086))

    # Saving the obtained plot
    plt.savefig('ui/static/plots/plot.png')
    plt.close()


'''The main-hub function'''
def main(raw_filename, time_interval, raw_strategy):

    # Initializing data
    strategy = raw_strategy
    filename = get_filename(raw_filename)
    points = get_points(filename)
    logs = briefcase_logging(points, strategy)

    # Getting the dates list
    dates = [point['date'] for point in points]

    # Initializing data to build plot
    start_date = datetime.date(*list(map(int, time_interval['start'].split('-'))))
    end_date = datetime.date(*list(map(int, time_interval['end'].split('-'))))
    start_index, end_index = get_date_indexes(start_date, end_date, dates)
    time = numpy.array(dates[3:][start_index:end_index + 1])
    logs = logs[start_index:end_index + 1]
    cost = numpy.array([i.cost for i in logs])
    money = numpy.array([i.liquidation_savings() for i in logs])

    plot_builder(time, cost, points, money)

    share_delta_percent = logs[-1].cost / logs[0].cost - 1
    share_delta_money = round(logs[-1].cost - logs[0].cost, 2)
    balance_delta_percent = (logs[-1].liquidation_savings() / logs[0].liquidation_savings() - 1)
    balance_delta_money = round(logs[-1].liquidation_savings() - logs[0].liquidation_savings(), 2)

    return {
        'share_delta': {
            'share_delta_percent': share_delta_percent,
            'share_delta_money': share_delta_money,
        },
        'balance_delta': {
            'balance_delta_percent': balance_delta_percent,
            'balance_delta_money': balance_delta_money,
        },
        'strategy_name': raw_strategy['name'],
        'share_name': filename.split('/')[-1][:-4].capitalize(),
        'time_interval_start': dates[0],
        'time_interval_end': dates[-1],
    }
