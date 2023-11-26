from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('user/signup/', views.signup_view, name="signup"),
    path('user/login/', views.login_view, name="login"),
	
    path('user/csrftoken/', views.send_csrf_token_view, name="send csrf token"),
    path('user/validate-jwt/', views.validate_jwt_token_view, name="validate jwt token"),

    path('user/info-me/<str:username>/', views.info_me_view, name='info-me'),	
    path('user/update-avatar/<str:username>/', views.update_avatar_view, name='update-avatar'),
	path('get_user_id/<str:username>/', views.get_user_id, name='get_user_from_username_view'),

    path('enable_2fa/<int:user_id>/', views.enable_2fa, name='enable_2fa'),
    path('disable_2fa/<int:user_id>/', views.disable_2fa, name='disable_2fa'),
    path('display_qr_code/<int:user_id>/', views.display_qr_code, name='display_qr_code'),
    path('verify_totp_code/', views.verify_totp_code, name='verify_totp_code'),
] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
