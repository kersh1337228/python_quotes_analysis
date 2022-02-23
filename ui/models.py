import datetime
from django.core.files import File
from django.db import models
from django.urls import reverse


'''Strategy model, where strategy is basically what to do 
when getting the 'good' and 'bad' analytics result,
how much of shares can be in the briefcase at the same time and
how much shares can we borrow'''
class Strategy(models.Model):
    name = models.CharField(
        max_length=255,
        verbose_name='Strategy name',
        unique=True
    )
    shares_limit_high = models.PositiveSmallIntegerField(
        verbose_name='Shares amount limit to store'
    )
    shares_limit_low = models.SmallIntegerField(
        verbose_name='Shares amount limit to borrow'
    )
    buy = models.PositiveSmallIntegerField(
        verbose_name='Shares amount to buy if success'
    )
    sell = models.PositiveSmallIntegerField(
        verbose_name='Shares amount to sell if failure'
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
    )

    # Decides whether it to buy or to sell the share
    def buy_or_sell(self, portfolio_image, index, date):
        for delta in range(3):
            quote = portfolio_image.shares[index].origin.quotes[(
                    date + datetime.timedelta(days=delta)
            ).strftime('%Y-%m-%d')]['close']
            current = portfolio_image.shares[index].origin.quotes[
                (date + datetime.timedelta(days=3)).strftime('%Y-%m-%d')
            ]['close']
            if current > quote and portfolio_image.shares[index].amount + 1 <= self.shares_limit_high\
                    and portfolio_image.balance >= current:
                portfolio_image.shares[index].amount += 1
                portfolio_image.balance -= current
            elif current < quote and portfolio_image.shares[index].amount - 1 >= self.shares_limit_low:
                portfolio_image.shares[index].amount -= 1
                portfolio_image.balance += current
        portfolio_image.set_cost((date + datetime.timedelta(days=3)).strftime('%Y-%m-%d'))
        return portfolio_image


    '''Creating slug to use in strategy object url further,
    slug is based on strategy name'''
    def save(self, **kwargs):
        if not self.slug or self.slug != self.name.replace(' ', '_').lower():
            self.slug = self.name.replace(' ', '_').lower()
        super(Strategy, self).save()

    '''Getting strategy object absolute url, based on its slug, created before'''
    def get_absolute_url(self):
        return reverse('strategy', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name


'''Log class with user analytics log,
created after pushing the analyze button and
stores the data of the analysis'''
class Log(models.Model):
    time_interval_start = models.DateField()
    time_interval_end = models.DateField()
    price_deltas = models.JSONField()
    strategy = models.ForeignKey(
        'Strategy',
        on_delete=models.CASCADE
    )
    portfolio = models.ForeignKey(
        'quotes.Portfolio',
        on_delete=models.CASCADE
    )
    balance_plot = models.ImageField(
        upload_to='plots/%Y/%m/%d/%H/%M/%S'
    )
    share_plots =models.ManyToManyField(
        'Image',
        related_name='log_share_plots',
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        db_index=True,
    )

    def save(self, **kwargs):
        if not self.slug:
            self.slug = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        super(Log, self).save(**kwargs)


'''Image class to attach multiple images to one model'''
class Image(models.Model):
    image = models.ImageField(
        upload_to='plots/%Y/%m/%d/%H/%M/%S'
    )

    def attach_image(self, filename):
        self.image.save(
            filename,
            File(open(f'ui/business_logic/{filename}', 'rb'))
        )
        self.save()
