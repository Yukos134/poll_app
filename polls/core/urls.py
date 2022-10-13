from django.urls import path
from . import views

urlpatterns = [
    path('', views.Polls.as_view(), name='Polls'),
    path('polls', views.Polls.as_view(), name='Polls'),
    path('poll', views.Poll.as_view(), name='Poll'),
    path('vote', views.Vote.as_view(), name='Vote'),
]
