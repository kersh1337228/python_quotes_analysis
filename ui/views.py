from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, DeleteView
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response
from .business_logic.analytics import analyse
from .forms import CreateStrategyForm, UserInterface
from .models import Strategy, Log
from quotes.models import Portfolio


class AnalysisAPIView(
    CreateAPIView,
    RetrieveUpdateDestroyAPIView
):
    # Analysis page get request, returns the form fields
    # step by step, depending on the previous choices
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            # Choosing the portfolio
            if request.query_params.get('step') == 'portfolio':
                portfolio = Portfolio.objects.get(
                    slug=request.query_params.get('slug')
                )
                if not len(portfolio.shares.all()):
                    return Response(
                        data={
                            'error_message': 'No shares in the portfolio'
                        },
                        status=400,
                    )
                return Response(
                    data={
                        'dates': portfolio.get_quotes_dates()
                    },
                    status=200,
                )
            # Choosing the time interval end date
            elif request.query_params.get('step') == 'strategies':
                return Response(
                    data={
                        'strategies': [
                            model_to_dict(strategy) for strategy in Strategy.objects.all()
                        ]
                    },
                    status=200,
                )
        else:
            return render(
                request, 'main.html',
                {'title': 'Analytics',
                 'form': UserInterface}
            )

    # Getting form data and analysing them
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            pass
        else:
            log = analyse(
                Portfolio.objects.get(
                    slug=request.data.get('portfolio')
                ),
                request.data.get('time_interval_start'),
                request.data.get('time_interval_end'),
                Strategy.objects.get(
                    slug=request.data.get('strategy')
                )
            )
            return redirect(
                'logs_detail',
                slug=log.slug,
            )

    def put(self, request, *args, **kwargs):
        pass

    def patch(self, request, *args, **kwargs):
        pass

    def delete(self, request, *args, **kwargs):
        pass

    '''Redirecting if form is validated successfully'''
    def get_success_url(self):
        return reverse_lazy('plot')


class LogAPIView(RetrieveUpdateDestroyAPIView):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            pass
        else:
            return render(
                template_name='log_detail.html',
                context={
                    'log': Log.objects.get(
                        slug=kwargs.get('slug')
                    )
                },
                request=request
            )

    def delete(self, request, *args, **kwargs):
        if request.is_ajax():
            Log.objects.get(
                slug=request.data.get('slug')
            ).delete()
            return Response(
                data={},
                status=200,
            )
        else:
            pass


class LogListAPIView(ListAPIView):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            pass
        else:
            return render(
                template_name='log_list.html',
                context={
                    'logs': Log.objects.all(),
                },
                request=request
            )


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
    template_name = 'log_list.html'
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


'''Error 404 handler'''
def method404(request, exception):
    return render(request, 'error.html')
