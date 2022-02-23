from django.urls import path
from .views import AnalysisAPIView, CreateStrategyView, ListOfStrategiesView,\
    SingleStrategyView, DeleteStrategyView, ListOfLogsView, LogAPIView


urlpatterns = [
    path(
        'analysis/',
        AnalysisAPIView.as_view(),
        name='main'
    ),
    path(
        'analysis/form/',
        AnalysisAPIView.as_view(),
        name='get_form'
    ),
    path(
        'strategies/create/',
        CreateStrategyView.as_view(),
        name='create_strategy'
    ),
    path(
        'strategies/',
        ListOfStrategiesView.as_view(),
        name='strategies'
    ),
    path(
        'strategies/sortby/<slug:sortby>',
        ListOfStrategiesView.as_view(),
        name='strategies_sortby'
    ),
    path(
        'strategies/<slug:slug>',
        SingleStrategyView.as_view(),
        name='strategy'
    ),
    path(
        'strategies/delete/<slug:slug>',
        DeleteStrategyView.as_view(),
        name='delete_strategy'
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
