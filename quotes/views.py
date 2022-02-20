import datetime

from django.core.paginator import Paginator
from django.db.models import Q
from django.forms import model_to_dict
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from rest_framework.generics import CreateAPIView,\
    RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response

from ui.business_logic.data_parser import get_all_quotes, quote_name_search, paginate
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
                slug=request.data.get('slug'),
            )
            if request.data.get('type') == 'add':
                share = Share.objects.create(
                    origin=Quote.objects.get(
                        symbol=request.data.get('symbol')
                    ),
                    amount=1,
                )
                portfolio.shares.add(share)
                return Response(
                    data={'share': {
                        'symbol': share.origin.symbol,
                        'name': share.origin.name
                    }},
                    status=200
                )
            elif request.data.get('type') == 'change_amount':
                portfolio.shares.filter(
                    origin=Quote.objects.get(
                        symbol=request.data.get('symbol')
                    )
                ).update(
                    amount=request.data.get('amount')
                )
                portfolio.last_updated=datetime.datetime.now()
                portfolio.save()
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
                Quote.add_quote_by_symbol(
                    request.query_params.get('symbol'),
                    request.query_params.get('name'),
                    kwargs.get('slug'),
                )
            return Response(
                data={},
                status=201
            )
        else:
            quote = Quote.objects.get(
                slug=kwargs.get('slug')
            )
            quotes = quote.quotes[list(quote.quotes.keys())[0]]
            return render(
                request=request,
                template_name='quotes_detail.html',
                context={'quote': quote, 'quotes': {
                    'date': list(quote.quotes.keys())[0],
                    'open': quotes['open'],
                    'high': quotes['high'],
                    'low': quotes['low'],
                    'close': quotes['close'],
                    'volume': quotes['volume'],
                }}
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
            if request.query_params.get('downloaded'):
                quotes = Quote.objects.filter(
                    Q(symbol__icontains=request.query_params.get('name')) |
                    Q(name__icontains=request.query_params.get('name'))
                )
                return Response(
                    {'results': [{
                        'symbol': quote.symbol,
                        'name': quote.name,
                        'slug': quote.slug,
                    } for quote in quotes] if quotes else []},
                    status=200
                )
            else:
                results = quote_name_search(
                     request.query_params.get('search')
                ) if request.query_params.get('search') else \
                    get_all_quotes(int(request.query_params.get('page', 1)) - 1, 50)
                quotes = [{
                    'symbol': result[0],
                    'name': result[1],
                    'price': result[2],
                    'change': result[3],
                    'change_percent': result[4],
                    'volume': result[5],
                    'slug': result[1].lower().replace(' ', '_').replace(',', '_').replace('.', '_'),
                } for result in results]
                quotes_html = ''
                for quote in quotes:
                    quotes_html += render_to_string(
                        template_name='quote.html',
                        context={
                            'quote': quote,
                            'downloaded_quotes': [quote.symbol for quote in Quote.objects.all()],
                        },
                        request=request,
                    )
                return Response(
                    data={
                        'quotes_html': quotes_html,
                        'pagination_html': render_to_string(
                            template_name='pagination.html',
                            context={
                                'pagination': paginate(int(request.query_params.get('page', 1)), 50)
                            },
                            request=request
                        ) if not request.query_params.get('search') else None

                    },
                    status=200
                )
        else:
            current_page = int(request.query_params.get('page', 1))
            quotes = get_all_quotes(current_page - 1, 50)
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
                        'slug': quote[1].lower().replace(' ', '_').replace(',', '_').replace('.', '_'),
                    } for quote in quotes],
                    'downloaded_quotes': [quote.symbol for quote in Quote.objects.all()],
                    'pagination': paginate(current_page, 50)
                }
            )
