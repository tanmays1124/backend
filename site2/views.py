from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import View
from rest_framework.decorators import api_view, permission_classes
import logging
from django.contrib.auth.hashers import make_password


from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import UserSerializer
from .models import QuizQuestion
from .serializers import QuizQuestionSerializer
from rest_framework.permissions import IsAuthenticated
from .models import ResetToken, CustomUser
from .serializers import ResetPasswordSerializer
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.authtoken.views import ObtainAuthToken


from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

from .utils import generate_reset_token 

# @api_view(['POST'])
# def register_user(request):
#     if request.method == 'POST':
#         print(request.data)
#         serializer = UserSerializer(data=request.data)
#         try:
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             # return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        print(request.data)

        username = request.data["username"]
        email=request.data["email"]
        first_name=request.data["first_name"]
        last_name=request.data["last_name"]
        password=request.data["password"]

        if CustomUser.objects.filter(email=email):
            return Response({'error': "Email Already Exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        if CustomUser.objects.filter(username=username):
            return Response({'error': "Username Already Exists"},status=status.HTTP_400_BAD_REQUEST)
        

        user = CustomUser.objects.create(username=username, email=email, password=make_password(password))
        user.save()
        
        

        return Response({"success":"Profile created"}, status=status.HTTP_201_CREATED)











@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')
        print(username)
        print(password)
        user = None
        if '@' in username:
            try:
                user = CustomUser.objects.get(email=username)
            except ObjectDoesNotExist:
                pass
        if not user:
            user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            

            return Response({'token': token.key,'username':user.username,'id':user.id}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    




class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super(CustomAuthToken, self).post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({'token': token.key, 'user_id': token.user.id})


@api_view(['GET'])
def get_user_details(request, user_id):

    user = get_object_or_404(CustomUser, id=user_id)

    serializer = UserSerializer(user)
    # return Response({'id':serializer.data.id, 'username': serializer.data.username, 'first_name': serializer.data.first_name, 'last_name': serializer.data.last_name, 'email': serializer.data.email, 'photo':photo_data})

    return Response(serializer.data)


custom_auth_token = CustomAuthToken.as_view()




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import CustomUser  # Import your model
import json

@csrf_exempt  # Disable CSRF protection for simplicity (enable only in development)
def update_model(request, userid):
    if request.method == 'POST':
        try:
            # Parse incoming JSON data
            data = json.loads(request.body)
            
            # Retrieve the model instance to update
            instance = CustomUser.objects.get(id=userid)  # Assuming user_id is a field in your model

            # Update the model instance
            instance.first_name = data.get('first_name', instance.first_name)
            instance.last_name = data.get('last_name', instance.last_name)
            instance.email = data.get('email', instance.email)
            # Update other fields similarly
            
            # Save the updated instance
            instance.save()

            return JsonResponse({'message': 'Model updated successfully'})
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'Model not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)




    
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class UserDeleteView(View):
    def destroy(self, request, user_id=None):
        try:
            user = CustomUser.objects.get(id=user_id)
            user.delete()
            return Response(status=status.HTTP_204_NO_CONTENT) 
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)




class QuizQuestionList(generics.ListAPIView):
    serializer_class = QuizQuestionSerializer

    def get_queryset(self):
        queryset = QuizQuestion.objects.all()

        # Get parameters from the request, default to None if not provided
        category = self.request.query_params.get('category', None)
        num_questions = self.request.query_params.get('num_questions', None)
        difficulty = self.request.query_params.get('difficulty', None)

        # Apply filters based on parameters
        if category:
            queryset = queryset.filter(category=category)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty)
        if num_questions:
            queryset = queryset[:int(num_questions)]
        print(queryset)

        return queryset
    

    
from .models import QuestionHistory
from .serializers import QuestionHistorySerializer


class QuestionHistoryListCreateView(generics.ListCreateAPIView):
    queryset = QuestionHistory.objects.all()
    serializer_class = QuestionHistorySerializer



class QuestionHistoryDetailView(generics.ListAPIView):
    serializer_class = QuestionHistorySerializer

    def get_queryset(self):
        queryset = QuestionHistory.objects.all()

        # Get parameters from the request, default to None if not provided
        user_id = self.request.query_params.get('user_id', None)


        # Apply filters based on parameters
        if user_id:
            queryset = queryset.filter(user=user_id)

        print(queryset)

        return queryset
    





class ResetPasswordRequest(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = CustomUser.objects.filter(email=email).first()

            if user:
                # Generate and save reset token
                reset_token = generate_reset_token()
                ResetToken.objects.create(user=user, token=reset_token)
                subject = 'Password Reset'
                reset_link = f'http://127.0.0.1:8000/reset-password/{reset_token}/'  # Update with your actual reset link

                # Create the email message
                message = render_to_string('reset_password_email.html', {'reset_link': reset_link})
                plain_message = strip_tags(message)

                # Send the email
                send_mail(subject, plain_message, 'from@example.com', [user.email], html_message=message)

                return Response({'message': 'Reset email sent successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomUserView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = CustomUser.objects.all()

        # Get parameters from the request, default to None if not provided
        user_id = self.request.query_params.get('user_id', None)


        # Apply filters based on parameters
        if user_id:
            queryset = queryset.filter(id=user_id)

        print(queryset)

        return queryset



    

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    user = request.user  # Get the authenticated user

    serializer = UserSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)
        






# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import CustomUser
from .serializers import UserSerializer

@api_view(['POST'])
def upload_photo(request, userid):
    try:
        user = CustomUser.objects.get(id=userid)
    except CustomUser.DoesNotExist:
        return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

    if 'photo' not in request.FILES:
        return Response({'error': 'No photo provided'}, status=status.HTTP_400_BAD_REQUEST)

    user.photo = request.FILES['photo']
    user.save()

    serializer = UserSerializer(user)
    return Response(serializer.data)


from django.http import HttpResponse
from django.conf import settings
import os

@api_view(['GET'])
def get_user_photo(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    photo_path = user.photo.path  # Assuming 'photo' is a FileField in your CustomUser model
    
    # Open the photo file and read its content
    with open(photo_path, 'rb') as f:
        photo_data = f.read()

    # Set the appropriate content type for the photo
    content_type = "image/*"  # Adjust according to your photo format

    # Return the photo data as an HTTP response
    return HttpResponse(photo_data, content_type=content_type)
