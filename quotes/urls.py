from django.urls import path
from .views import *


urlpatterns = [
    path(
        'portfolio/list/',
        PortfolioListAPIView.as_view(),
        name='portfolio_list'
    ),
    path(
        'portfolio/create/',
        PortfolioAPIView.as_view(),
        name='portfolio_create'
    ),
    path(
        'portfolio/detail/<slug:slug>',
        PortfolioAPIView.as_view(),
        name='portfolio_detail'
    ),
    path(
        'portfolio/update/<slug:slug>',
        PortfolioAPIView.as_view(),
        name='portfolio_update'
    ),
    path(
        'portfolio/delete/<slug:slug>',
        PortfolioAPIView.as_view(),
        name='portfolio_delete'
    ),
    path(
        'quotes/list/',
        QuotesListAPIView.as_view(),
        name='quotes_list'
    ),
    path(
        'quotes/detail/<slug:slug>',
        QuotesAPIView.as_view(),
        name='quotes_detail'
    )
]
