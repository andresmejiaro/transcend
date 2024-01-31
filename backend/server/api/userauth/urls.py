from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views.auth import signup_view, login_view
from .views.user import info_me_view, info_me_id_view, update_avatar_view, get_user_id, user_exists, user_intra_exists, \
    user_friends_list, info_user_view
from .views.token import send_csrf_token_view, validate_jwt_token_view
from .views.googleauth import enable_2fa, disable_2fa, display_qr_code, verify_totp_code, user_2fa_setup_complete
from .views.auth import oauth_start, oauth_login
from .views.stats import get_kpi, get_kpi_username
from .views.user import update_user_information

urlpatterns = [
    path('user/signup/', signup_view, name="signup"),
    path('user/login/', login_view, name="login"),

    path('user/csrftoken/', send_csrf_token_view, name="send csrf token"),
    path('user/validate-jwt/', validate_jwt_token_view, name="validate jwt token"),

    path('user/info-me/', info_me_view, name='info-me'),
    path('user/info-user/<str:username>/', info_user_view, name='info-user'),

    path('user/info-me-id/<int:user_id>/', info_me_id_view, name='info-me-id'),
    path('user/update-avatar/', update_avatar_view, name='update-avatar'),
    path('user/friendlist/', user_friends_list, name='user_friendlist'),

    # BORRAR ESTA
    path('get_user_id/<str:username>/', get_user_id, name='get_user_from_username_view'),

    # @csrf_exempt
    path('user/exists/<str:username>/', user_exists, name='does_user_exist'),
    path('user/exists/<str:username>/<str:fullname>/', user_intra_exists, name='does_user_intra_exist'),

    path('verify_totp_code/', verify_totp_code, name='verify_totp_code'),  # @csrf_exempt
    path('enable_2fa/', enable_2fa, name='enable_2fa'),
    path('disable_2fa/', disable_2fa, name='disable_2fa'),
    path('display_qr_code/', display_qr_code, name='display_qr_code'),
    path('is_2fa_setup_complete/', user_2fa_setup_complete, name="is_2fa_setup_complete"),

    path('oauth-init/', oauth_start, name="oauth-start"),
    path('oauth/login/', oauth_login, name="oauth-login"),

    path('user/stats/', get_kpi, name="get_kpi"),
    path('user/stats/<str:username>/', get_kpi_username, name="get_kpi_username"),
    path('user/update/', update_user_information, name="update_user_info"),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)