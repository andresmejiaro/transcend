from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views.auth import signup_view, login_view
from .views.user import info_me_view, update_avatar_view, get_user_id
from .views.token import send_csrf_token_view, validate_jwt_token_view
from .views.googleauth import enable_2fa, disable_2fa, display_qr_code, verify_totp_code

urlpatterns = [
    path('user/signup/', signup_view, name="signup"),
    path('user/login/', login_view, name="login"),
	
    path('user/csrftoken/', send_csrf_token_view, name="send csrf token"),
    path('user/validate-jwt/', validate_jwt_token_view, name="validate jwt token"),

    path('user/info-me/<str:username>/', info_me_view, name='info-me'),	
    path('user/update-avatar/<str:username>/', update_avatar_view, name='update-avatar'),
	path('get_user_id/<str:username>/', get_user_id, name='get_user_from_username_view'),

    path('enable_2fa/<int:user_id>/', enable_2fa, name='enable_2fa'),
    path('disable_2fa/<int:user_id>/', disable_2fa, name='disable_2fa'),
    path('display_qr_code/<int:user_id>/', display_qr_code, name='display_qr_code'),
    path('verify_totp_code/', verify_totp_code, name='verify_totp_code'),
] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
