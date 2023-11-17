from django.urls import path
from . import views

urlpatterns = [
    path('test/', views.testView, name='test'),

    path('token/', views.sendToken_view, name="send token"),

    path('get_user_by_username/', views.get_user_by_username, name='get_user_by_username'),
    path('get_user/<str:username>/', views.get_user_from_username_view, name='get_user_from_username_view'),
    

    path('signup-intra/', views.signupIntra, name="signup intra"),
    path('signup/', views.signup, name="signup"),

    path('login/', views.login, name="login"),

]
