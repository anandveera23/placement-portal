from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('mcq-test/', views.mcq_test, name='mcq_test'),
    path('coding/', views.coding_list, name='coding_list'),
path('coding/test/', views.coding_test, name='coding_test'),
path('performance/', views.performance, name='performance'),
path('leaderboard/', views.leaderboard, name='leaderboard'),
 path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
 path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
 path("all-results/", views.all_results, name="all_results"),

]