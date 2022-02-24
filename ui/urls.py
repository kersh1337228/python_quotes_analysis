from django.urls import path
from .views import AnalysisAPIView, ListOfLogsView, LogAPIView,\
    StrategyListAPIView, StrategyAPIView


urlpatterns = [
    path(
        'analysis/',
        AnalysisAPIView.as_view(),
        name='analysis'
    ),
    path(
        'analysis/form/',
        AnalysisAPIView.as_view(),
        name='get_form'
    ),
    path(
        'strategy/list/',
        StrategyListAPIView.as_view(),
        name='strategy_list'
    ),
    path(
        'strategy/create/',
        StrategyAPIView.as_view(),
        name='strategy_create'
    ),
    path(
        'strategy/detail/<slug:slug>',
        StrategyAPIView.as_view(),
        name='strategy_detail'
    ),
    path(
        'strategy/update/',
        StrategyAPIView.as_view(),
        name='strategy_update'
    ),
    path(
        'strategy/delete/',
        StrategyAPIView.as_view(),
        name='strategy_delete'
    ),
    path(
        'logs/list/',
        ListOfLogsView.as_view(),
        name='logs_list'
    ),
    path(
        'logs/detail/<slug:slug>/',
        LogAPIView.as_view(),
        name='logs_detail'
    ),
    path(
        'logs/delete/',
        LogAPIView.as_view(),
        name='logs_delete'
    ),
]
