from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'users'

class CustomLoginView(auth_views.LoginView):
    def get_success_url(self):
        return f'/profile/{self.request.user.userprofile.pk}/'

urlpatterns = [
    path('login/', CustomLoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
    path('manage/', views.user_management, name='manage'),
    path('upload-csv/', views.upload_csv, name='upload_csv'),
    path('create/', views.create_user, name='create_user'),
    path('toggle-active/<int:user_id>/', views.toggle_active, name='toggle_active'),
]