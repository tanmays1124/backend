"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django import views
from django.urls import path
from .views import UserDeleteView, register_user, user_login, user_logout, QuizQuestionList, get_user_details, forgot_password, reset_password
from .views import QuestionHistoryListCreateView, QuestionHistoryDetailView, update_model, upload_photo, deleteUserProfile,get_user_photo


urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('questions/', QuizQuestionList.as_view(),name='questions'),
    path('questionhistorycreate/', QuestionHistoryListCreateView.as_view(), name='questionhistory-list-create'),
    path('questionhistoryget/', QuestionHistoryDetailView.as_view(), name='questionhistory-detail'),
    # path('resetpassword/', ResetPasswordRequest.as_view(), name='reset_password'),
    path('userprofile/<int:user_id>',  get_user_details, name='Profile details'),
    path('update/<int:userid>',update_model, name ='Update Profile'),
    path('upload/<int:userid>',upload_photo, name="upload photo"),
    # path('getphoto/<int:userid>/',get_user_photo, name = "Photo"),
    path('delete/<int:user_id>', deleteUserProfile, name='delete_user'),


    # path('forgot/',PasswordResetAPI.as_view(), name = "forgot-password"),

    path('forgot_password/',forgot_password, name='forgot_password'),
    path('reset_password/', reset_password, name='reset_password'),

]

# urls.py


