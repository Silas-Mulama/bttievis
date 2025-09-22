from django.urls import path
from authentication.views import *
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('signup/', register_user, name='signup'),
    path('signin/', login_user, name='login-user'),
    path('otp/', otp_verification, name='otp_verification'),
    path('resent-otp/', resent_otp, name='resent_otp'),
    path('logout/', logout_user, name='logout'),
    path('profile-picture/update/',update_profile_pic, name='pro_pic'),
    path('user/profile/',profile, name='my-profile'),
    path('voting-id/', get_voting_id, name='voting_id'),
    path('verify-voting-id/',verify_voting_id, name='verify_voting_id'),
    
    
     # Reset Password
    path('reset_password/', 
         auth_views.PasswordResetView.as_view(template_name="auths/reset_password.html"), 
         name="reset_password"),

    path('reset_password_sent/', 
         auth_views.PasswordResetDoneView.as_view(template_name="auths/reset_password_sent.html"), 
         name="password_reset_done"),

    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name="auths/reset_password_confirm.html"), 
         name="password_reset_confirm"),

    path('reset_password_complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name="auths/reset_password_complete.html"), 
         name="password_reset_complete"),
]