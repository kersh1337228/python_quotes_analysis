from django.shortcuts import render
from rest_framework.generics import CreateAPIView,\
    RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response

from .models import Portfolio, Share


class PortfolioAPIView(
    CreateAPIView,
    RetrieveUpdateDestroyAPIView
):
    # Portfolio detail view
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            pass
        else:
            return render(
                request=request,
                template_name='portfolio_detail.html',
                context={'portfolio': Portfolio.objects.get(slug=kwargs.get('slug'))}
            )

    # Portfolio creation view
    def post(self, request, *args, **kwargs):
        if request.is_ajax():
            name, balance = request.data.get('name').strip(), \
                            request.data.get('balance')
            portfolio = Portfolio.objects.create(
                name=name,
                slug=name.lower(),
                balance=balance
            )
            return Response(
                data={},
                content_type='json',
                status=200
            )
        else:
            pass

    # Portfolio update view
    def patch(self, request, *args, **kwargs):
        if request.is_ajax():
            name, balance = request.data.pop('shares')
            portfolio = Portfolio.objects.filter(
                slug=request.data.get('slug')
            ).update(
                name=name,
                slug=name.lower(),
                balance=balance,
            ).first()
            return Response(
                data={},
                content_type='json',
                status=200
            )
        else:
            pass

    # Portfolio share changes view
    def put(self, request, *args, **kwargs):
        if request.is_ajax():
            # Add, change amount of or delete shares
            return Response(
                data={},
                content_type='json',
                status=200
            )
        else:
            pass

    # Portfolio delete view
    def delete(self, request, *args, **kwargs):
        if request.is_ajax():
            Portfolio.objects.get(
                slug=request.data.get('slug')
            ).delete()
            return Response(
                data={},
                content_type='json',
                status=200
            )
        else:
            pass


class PortfolioListAPIView(
    ListAPIView
):
    def get(self, request, *args, **kwargs):
        pass
