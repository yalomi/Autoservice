from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('news/', views.news, name='news'),
    path('glossary/', views.glossary, name='glossary'),
    path('contacts/', views.contacts, name='contacts'),
    path('privacy/', views.privacy, name='privacy'),
    path('vacancies/', views.vacancies, name='vacancies'),
    path('reviews/', views.reviews, name='reviews'),
    path('promocodes/', views.promocodes, name='promocodes'),
    path('reviews/add/', views.review_create, name='review_add'),
    path('reviews/<int:pk>/edit/', views.review_update, name='review_edit'),
    path('reviews/<int:pk>/delete/', views.review_delete, name='review_delete'),
    path('services/', views.services, name='services'),
    path('appointments/create/', views.appointment_create, name='appointment_create'),
    path('my-appointments/', views.appointment_list, name='my_appointments'),
    path('master-schedule/', views.master_schedule, name='master_schedule'),
    path('appointments/<int:pk>/confirm/', views.appointment_confirm, name='appointment_confirm'),
    path('appointments/<int:pk>/reject/', views.appointment_reject, name='appointment_reject'),
    path('appointments/<int:pk>/delete/', views.appointment_delete, name='appointment_delete'),
    path('appointments/<int:pk>/complete/', views.appointment_complete, name='appointment_complete'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('dashboard/', views.user_dashboard, name='dashboard'),
] 