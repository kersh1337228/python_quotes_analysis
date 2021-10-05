from django.core.files import File
from django.core.files.images import ImageFile
from django.shortcuts import render, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import FormView, CreateView, DetailView, ListView, DeleteView

from .business_logic.analytics import main
from .forms import *
from .models import *


'''User interface view, calling the 
analytics function if form is valid'''
class UIView(FormView):
    template_name = 'main.html'
    form_class = UserInterface

    main_result = {}

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['title'] = 'Main Menu'
        return context


    '''Form validation with post request'''
    def form_valid(self, form):
        form_data = form.data
        time_interval = {
            'start': form_data['time_interval_start'],
            'end': form_data['time_interval_end'],
        }
        global main_result
        main_result = main(form_data['share_name'], time_interval,
                           Strategy.objects.get(pk=int(form_data['strategy_name'])).get_params())
        return super(UIView, self).form_valid(form)

    '''Redirecting if form is validated successfully'''
    def get_success_url(self):
        return reverse_lazy('plot')


'''Creating your own set up strategy,
creates a new object in database'''
class CreateStrategyView(CreateView):
    form_class = CreateStrategyForm
    template_name = 'create_strategy.html'
    success_url = reverse_lazy('strategies')
    model = Strategy
    extra_context = {'title': 'Create Strategy'}


'''All strategies list on one single page,
allowing also to view any of it more detailed'''
class ListOfStrategiesView(ListView):
    model = Strategy
    template_name = 'strategies.html'
    context_object_name = 'strategies'
    extra_context = {'title': 'Strategies'}

    '''Gets the list of all strategies ordered by certain parameter'''
    def get_queryset(self):
        queryset = Strategy.objects.all()
        if self.kwargs.get('sortby'):
            sort = self.kwargs.get('sortby')
            if sort == 'name':
                queryset = Strategy.objects.order_by('name')
            elif 'efficiency' in sort:
                bad = []
                normal = []
                good = []
                for strategy in queryset:
                    verdict = strategy.get_efficiency().get('verdict')
                    if verdict == 'bad':
                        bad.append(strategy)
                    elif verdict == 'normal':
                        normal.append(strategy)
                    else:
                        good.append(strategy)
                if sort == 'efficiency_gtb':
                    bad.extend(normal)
                    bad.extend(good)
                    return bad
                else:
                    good.extend(normal)
                    good.extend(bad)
                    return good
        return queryset


'''Single strategy detailed analytics and information'''
class SingleStrategyView(DetailView):
    model = Strategy
    template_name = 'strategy.html'
    context_object_name = 'strategy'
    slug_url_kwarg = 'slug'


'''Delete certain strategy'''
class DeleteStrategyView(DeleteView):
    model = Strategy
    template_name = 'delete_strategy.html'
    context_object_name = 'strategy'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('strategies')


'''All logs list on one single page.
Logs are automatically created while doing analytics'''
class ListOfLogsView(ListView):
    model = Log
    template_name = 'logs.html'
    context_object_name = 'logs'
    extra_context = {'title': 'Logs'}

    def get_queryset(self):
        return Log.objects.all()


'''Delete certain strategy'''
class DeleteLogView(DeleteView):
    model = Log
    template_name = 'delete_log.html'
    context_object_name = 'log'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('logs')


'''Plot view, which is shown after the analytics is finished'''
def plot_view(request):
    global main_result
    context = {
        'title': 'Plot',
        'share_delta': round(main_result['share_delta'] * 100, 2),
        'balance_delta': round(main_result['balance_delta'] * 100, 2),
        'time_interval_start': main_result['time_interval_start'],
        'time_interval_end': main_result['time_interval_end'],
        'share_name': main_result['share_name']
    }
    if context['share_delta'] == 0 and context['balance_delta'] == 0:
        context['no_data'] = True
        return render(request, 'plot.html', context)
    '''Creating new log connected to a certain strategy'''
    log = Log.objects.create(
        share_delta=context['share_delta'],
        balance_delta=context['balance_delta'],
        strategy=Strategy.objects.get(name=main_result['strategy_name']),
        share=main_result['share_name'],
        time_interval_start=main_result['time_interval_start'],
        time_interval_end=main_result['time_interval_end'],
    )
    log.plot.save('plot.png', File(open('ui/static/plots/plot.png', 'rb')), save=True)
    log.save()
    return render(request, 'plot.html', context)


'''Error 404 handler'''
def method404(request, exception):
    return render(request, 'error.html')
