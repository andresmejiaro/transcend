from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name="signup"),
    # path('signup-intra/', views.signupIntra, name="signup intra"),

    path('login/', views.login_view, name="login"),
	
    path('csrftoken/', views.send_csrf_token_view, name="send csrf token"),
    path('validate-jwt/', views.validate_jwt_token_view, name="validate jwt token"),

    path('info-me-jwt/', views.info_me_jwt_view, name='info-me-jwt'),
    # path('get_user/<str:username>/', views.get_user_from_username_view, name='get_user_from_username_view'),
]
