from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('user/signup/', views.signup_view, name="signup"),
    # path('signup-intra/', views.signupIntra, name="signup intra"),

    path('user/login/', views.login_view, name="login"),
	
    path('user/csrftoken/', views.send_csrf_token_view, name="send csrf token"),
    path('user/validate-jwt/', views.validate_jwt_token_view, name="validate jwt token"),

    path('user/info-me-jwt/', views.info_me_view, name='info-me-jwt'),
    path('user/info-me/<str:username>', views.info_me_view, name='info-me'),
	
    path('user/update-avatar/<str:username>/', views.update_avatar_view, name='update-avatar'),

    # path('get_user/<str:username>/', views.get_user_from_username_view, name='get_user_from_username_view'),
] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
