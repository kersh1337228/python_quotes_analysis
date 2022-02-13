from django.urls import path, include
from .views import *


urlpatterns = [
    path('analysis/', UIView.as_view(), name='main'),
    path('analysis/form/', UIAPIView.as_view(), name='get_form'),
    path('plot/', plot_view, name='plot'),
    path('strategies/create/', CreateStrategyView.as_view(), name='create_strategy'),
    path('strategies/', ListOfStrategiesView.as_view(), name='strategies'),
    path('strategies/sortby/<slug:sortby>', ListOfStrategiesView.as_view(), name='strategies_sortby'),
    path('strategies/<slug:slug>', SingleStrategyView.as_view(), name='strategy'),
    path('strategies/delete/<slug:slug>', DeleteStrategyView.as_view(), name='delete_strategy'),
    path('logs/', ListOfLogsView.as_view(), name='logs'),
    path('logs/delete/<int:pk>', DeleteLogView.as_view(), name='delete_log'),
]
