from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('signup/', views.signup_view, name="signup"),
    # path('signup-intra/', views.signupIntra, name="signup intra"),

    path('login/', views.login_view, name="login"),
	
    path('csrftoken/', views.send_csrf_token_view, name="send csrf token"),
    path('validate-jwt/', views.validate_jwt_token_view, name="validate jwt token"),

    path('info-me-jwt/', views.info_me_view, name='info-me-jwt'),
    path('info-me/<str:username>', views.info_me_view, name='info-me'),
	
    path('update-avatar/<str:username>/', views.update_avatar_view, name='update-avatar'),

    # path('get_user/<str:username>/', views.get_user_from_username_view, name='get_user_from_username_view'),
] 
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
