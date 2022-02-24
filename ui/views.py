from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, DeleteView
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response
from .business_logic.analytics import analyse
from .forms import CreateStrategyForm
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
                request, 'analysis.html',
                {'title': 'Analytics',
                 'portfolios': Portfolio.objects.all()}
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


class StrategyAPIView(
    RetrieveUpdateDestroyAPIView,
    CreateAPIView
):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            pass
        else:
            return render(
                template_name='strategy_detail.html',
                context={
                    'strategy': Strategy.objects.get(
                        slug=kwargs.get('slug')
                    ),
                    'logs': Log.objects.filter(
                        strategy__slug=kwargs.get('slug')
                    )
                },
                request=request
            )

    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            pass
        else:
            pass

    def patch(self, request, *args, **kwargs):
        if request.is_ajax():
            pass
        else:
            pass

    def put(self, request, *args, **kwargs):
        if request.is_ajax():
            pass
        else:
            pass

    def delete(self, request, *args, **kwargs):
        if request.is_ajax():
            pass
        else:
            pass


class StrategyListAPIView(ListAPIView):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            pass
        else:
            return render(
                template_name='strategy_list.html',
                context={
                    'strategies': Strategy.objects.all()
                },
                request=request
            )


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
    template_name = 'log_delete.html'
    context_object_name = 'log'
    pk_url_kwarg = 'pk'
    success_url = reverse_lazy('logs')


'''Error 404 handler'''
def method404(request, exception):
    return render(request, 'error.html')
