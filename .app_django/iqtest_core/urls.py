from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('question/<int:qnum>/', views.question, name='question'),
    path('submit/<int:qnum>/', views.submit, name='submit'),
    path('result/', views.result, name='result'),
]