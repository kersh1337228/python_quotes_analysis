import datetime

from django.forms import model_to_dict
from django.shortcuts import render
from django.template.loader import render_to_string
from rest_framework.generics import CreateAPIView,\
    RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response

from ui.business_logic.data_parser import get_all_quotes
from .forms import PortfolioCreateForm
from .models import Portfolio, Share, Quote


class PortfolioAPIView(
    CreateAPIView,
    RetrieveUpdateDestroyAPIView
):
    # Portfolio detail view
    def get(self, request, *args, **kwargs):
        portfolio = Portfolio.objects.get(
            slug=kwargs.get('slug')
        )
        if request.is_ajax():
            return Response(
                data={'form': render_to_string(
                    template_name='form.html',
                    context={'form': PortfolioCreateForm(
                             initial=model_to_dict(portfolio)
                         )},
                    request=request
                )},
                status=200
            )
        else:
            return render(
                request=request,
                template_name='portfolio_detail.html',
                context={'portfolio': portfolio}
            )

    # Portfolio creation view
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            data = {key: request.data.get(key) for key in request.data}
            data.pop('csrfmiddlewaretoken')
            form = PortfolioCreateForm(data=data)
            if not form.is_valid():
                return Response(
                    data={'form': render_to_string(
                        request=request,
                        template_name='form.html',
                        context={'form': form}
                    )},
                    status=400,
                )
            Portfolio.objects.create(
                name=data.get('name').strip(),
                slug=data.get('name').strip().lower().replace(' ', '_'),
                balance=data.get('balance')
            )
            return Response(
                data={},
                status=200
            )
        else:
            pass

    # Portfolio update view
    def patch(self, request, *args, **kwargs):
        if request.is_ajax():
            data = {key: request.data.get(key) for key in request.data}
            data.pop('csrfmiddlewaretoken', None)
            form = PortfolioCreateForm(data=data)
            portfolio = Portfolio.objects.get(
                slug=kwargs.get('slug')
            )
            if not form.is_valid():
                errors = form.errors.get_json_data()
                if errors == {"name": [{
                    "message": "Portfolio with this Name already exists.",
                    "code": "unique"}]
                } and data.get('name') == portfolio.name:
                    pass
                else:
                    if data.get('name') == portfolio.name:
                        for i in range(len(errors['name'])):
                            if errors['name'][i]['code'] == 'unique':
                                del errors['name'][i]
                    return Response(
                        data={'errors': errors},
                        status=400,
                    )
            Portfolio.objects.filter(
                slug=kwargs.get('slug')
            ).update(
                name=request.data.get('name').strip(),
                slug=request.data.get('name').strip().lower().replace(' ', '_'),
                balance=request.data.get('balance'),
                last_updated=datetime.datetime.now()
            )
            return Response(
                data={},
                status=200
            )
        else:
            pass

    # Portfolio share changes view
    def put(self, request, *args, **kwargs):
        if request.is_ajax():
            # Add, change amount of or delete shares
            portfolio = Portfolio.objects.get(
                slug=kwargs.get('slug'),
            )
            if request.data.get('type') == 'add':
                portfolio.shares.add(
                    Share.objects.create(
                        origin=Quote.objects.get(
                            symbol=request.data.get('symbol')
                        ),
                        amount=1,
                    )
                )
            elif request.data.get('type') == 'change_amount':
                portfolio.shares.filter(
                    origin=Quote.objects.get(
                        symbol=request.data.get('symbol')
                    ).update(
                        amount=request.data.get('amount')
                    )
                )
            elif request.data.get('type') == 'delete':
                portfolio.shares.get(
                    origin=Quote.objects.get(
                        symbol=request.data.get('symbol')
                    ),
                ).delete()
            return Response(
                data={},
                status=200
            )
        else:
            pass

    # Portfolio delete view
    def delete(self, request, *args, **kwargs):
        if request.is_ajax():
            Portfolio.objects.get(
                slug=kwargs.get('slug')
            ).delete()
            return Response(
                data={},
                status=200
            )
        else:
            pass


class PortfolioListAPIView(
    ListAPIView
):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            return Response(
                data={'form': render_to_string(
                    template_name='form.html',
                    context={'form': PortfolioCreateForm},
                    request=request
                )},
                status=200
            )
        else:
            return render(
                request=request,
                template_name='portfolio_list.html',
                context={'portfolios': Portfolio.objects.all(),
                         'form': PortfolioCreateForm}
            )


class QuotesAPIView(
    RetrieveUpdateDestroyAPIView,
    CreateAPIView
):
    # Quote detail view
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            if not Quote.objects.filter(slug=kwargs.get('slug')):
                print('\n\tHELLO\t\n')
            return Response(
                data={},
                status=200
            )
        else:
            return render(
                request=request,
                template_name='quotes_list.html',
                context={'quotes': [
                    result[0].strip() for result in get_all_quotes()
                ]}
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


class QuotesListAPIView(
    ListAPIView
):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            pass
        else:
            return render(
                request=request,
                template_name='quotes_list.html',
                context={'quotes': [{
                        'symbol': quote[0],
                        'name': quote[1],
                        'price': quote[2],
                        'change': quote[3],
                        'change_percent': quote[4],
                        'volume': quote[5],
                        'slug': quote[1].lower().replace(' ', '_'),
                    } for quote in get_all_quotes()]
                }
            )
