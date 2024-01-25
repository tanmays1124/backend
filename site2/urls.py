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
from django.urls import path
from .views import register_user, user_login, user_logout, QuizQuestionList, get_user_details
from .views import QuestionHistoryListCreateView, QuestionHistoryDetailView, ResetPasswordRequest, update_model, upload_photo, get_user_photo


urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('questions/', QuizQuestionList.as_view(),name='questions'),
    path('questionhistorycreate/', QuestionHistoryListCreateView.as_view(), name='questionhistory-list-create'),
    path('questionhistoryget/', QuestionHistoryDetailView.as_view(), name='questionhistory-detail'),
    path('resetpassword/', ResetPasswordRequest.as_view(), name='reset_password'),
    path('userprofile/<int:user_id>',  get_user_details, name='Profile details'),
    path('update/<int:userid>',update_model, name ='Update Profile'),
    path('upload/<int:userid>',upload_photo, name="upload photo"),
    path('getphoto/<int:userid>/',get_user_photo, name = "Photo")
]

# urls.py


