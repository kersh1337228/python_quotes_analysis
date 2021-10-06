from django.db.models import *
from django.urls import reverse

'''Strategy model, where strategy is basically what to do 
when getting the 'good' and 'bad' analytics result,
how much of shares can be in the briefcase at the same time and
how much shares can we borrow'''
class Strategy(Model):
    name = CharField(max_length=255, verbose_name='Strategy name', unique=True)
    shares_limit_high = PositiveSmallIntegerField(verbose_name='Shares amount limit to store')
    shares_limit_low = SmallIntegerField(verbose_name='Shares amount limit to borrow')
    buy = PositiveSmallIntegerField(verbose_name='Shares amount to buy if success')
    sell = PositiveSmallIntegerField(verbose_name='Shares amount to sell if failure')
    #url specifier
    slug = SlugField(max_length=255, unique=True, db_index=True, verbose_name='URL')

    '''Creating slug to use in strategy object url further,
    slug is based on strategy name'''
    def save(self, **kwargs):
        self.slug = self.name.replace(' ', '_').lower()
        super(Strategy, self).save()

    '''Getting strategy object absolute url, based on its slug, created before'''
    def get_absolute_url(self):
        return reverse('strategy', kwargs={'slug': self.slug})

    '''Get the dictionary with all model main parameters'''
    def get_params(self):
        return {
            'name': self.name,
            'shares_limit_high': self.shares_limit_high,
            'shares_limit_low': self.shares_limit_low,
            'buy': self.buy,
            'sell': self.sell,
        }

    '''Get the efficiency assessment, 
    depending on user-built analytics logs'''
    def get_efficiency(self):
        logs = Log.objects.filter(strategy=self)
        efficiency = {
            'bad': 0, 'normal': 0,
            'good': 0, 'bad_percent': 0,
            'normal_percent': 0, 'good_percent': 0,
            'logs': logs,
            'verdict': 'no data to observe',
        }
        if not list(logs):
            return efficiency
        for log in logs:
            result = log.get_result()
            if result == 'bad':
                efficiency['bad'] += 1
            elif result == 'normal':
                efficiency['normal'] += 1
            else:
                efficiency['good'] += 1
        efficiency['bad_percent'] = round(
            (efficiency['bad'] /
            (efficiency['bad'] + efficiency['normal'] + efficiency['good']))
            * 100, 2
        )
        efficiency['normal_percent'] = round(
            (efficiency['normal'] /
             (efficiency['bad'] + efficiency['normal'] + efficiency['good']))
            * 100, 2
        )
        efficiency['good_percent'] = round(
            (efficiency['good'] /
             (efficiency['bad'] + efficiency['normal'] + efficiency['good']))
            * 100, 2
        )
        if max(efficiency['bad'], efficiency['normal'], efficiency['good']) \
                == efficiency['bad']:
            efficiency['verdict'] = 'bad'
        elif max(efficiency['bad'], efficiency['normal'], efficiency['good']) \
                == efficiency['normal']:
            efficiency['verdict'] = 'normal'
        else:
            efficiency['verdict'] = 'good'
        return efficiency

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Strategy'
        verbose_name_plural = 'Strategies'
        ordering = ['name']


'''Log class with user analytics log,
created after pushing the analyze button and
stores the data of the analysis'''
class Log(Model):
    plot = ImageField(upload_to='plots/%Y/%m/%d/%H/%M/%S')
    share_delta_percent = FloatField(null=True)
    share_delta_money = FloatField(null=True)
    balance_delta_percent = FloatField(null=True)
    balance_delta_money = FloatField(null=True)
    strategy = ForeignKey('Strategy', on_delete=CASCADE)
    share = CharField(max_length=255)
    time_interval_start = DateField()
    time_interval_end = DateField()

    '''Says whether the analytics result is bad(-), normal(0) or good(+)'''
    def get_result(self):
        result = self.balance_delta_percent - self.share_delta_percent
        if result < 0:
            return 'bad'
        elif result == 0:
            return 'normal'
        return 'good'

    def __str__(self):
        return str(self.pk)
