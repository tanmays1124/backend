from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import View
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.hashers import make_password
from .models import UserToken


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
from django.contrib.auth.tokens import default_token_generator



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
        

        user = CustomUser.objects.create(username=username, email=email, first_name=first_name, last_name=last_name, password=make_password(password))
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
    print(serializer.data)
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
from django.db.models import Q


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
        






class QuizQuestionList(generics.ListAPIView):
    serializer_class = QuizQuestionSerializer

    def get_queryset(self):
        queryset = QuizQuestion.objects.all()

        # Get parameters from the request, default to None if not provided
        category = self.request.query_params.get('category', None)
        num_questions = self.request.query_params.get('num_questions', None)
        difficulty = self.request.query_params.get('difficulty', None)
        user_id = self.request.query_params.get('user_id',None)
        # Apply filters based on parameters
        if category:
            queryset = queryset.filter(category=category)
        if difficulty:
            queryset = queryset.filter(difficulty=difficulty.lower())

        
        # Exclude questions already attempted by the user
        if user_id:
            user_history = QuestionHistory.objects.filter(user=user_id)
            attempted_questions_texts = []
            for history in user_history:
                for attempted_question in history.attempted_questions:
                    attempted_questions_texts.append(attempted_question['q_text'])
                    # print(attempted_question['q_text'])
            # Create a Q object to match any of the attempted questions
            query = Q()
            for question_text in attempted_questions_texts:
                query |= Q(question=question_text)
            queryset = queryset.exclude(query)

        # Limit the number of questions
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

#Added Manually
# from django.utils.crypto import get_random_string
# from django.contrib.sites.shortcuts import get_current_site

# def forgot_password(request):
#     if request.method == 'POST':
#         email = request.POST.get('email', '')
#         user = CustomUser.objects.filter(email=email).first()
#         if user:
#             # Generate a unique token and save it to the user model
#             token = get_random_string(length=32)
#             user_token = UserToken.objects.create(email=email, reset_password_token=token)
#              # Get the current site's domain
#             current_site = get_current_site(request)
#             domain = current_site.domain
            
#             # Construct the reset link dynamically
#             reset_link = f"http://{domain}/reset_password/{token}/"
#             send_mail('Reset Password', f'Click the following link to reset your password: {reset_link}',
#                       settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
#             return render(request, 'authentication/password_reset_done.html')
#         else:
#             return render(request, 'authentication/password_reset_failed.html')
#     return render(request, 'authentication/forgot_password.html')





# def reset_password(request, token):
#     user_token = UserToken.objects.filter(reset_password_token=token).first()
#     if not user_token:
#         # Handle invalid or expired token
#         return render(request, 'authentication/password_reset_invalid.html')
#     if request.method == 'POST':
#         new_password = request.POST.get('new_password', '')
#         confirm_new_password = request.POST.get('confirm_new_password', '')
#         if new_password != confirm_new_password:
#             error_message = "Passwords do not match."
#             return render(request, 'authentication/reset_password.html', {'error_message': error_message, 'token': token})
#         # Update the user's password and reset the token
#         user = CustomUser.objects.get(email=user_token.email)
#         user.set_password(new_password)
#         user.save()

#         # if user.email == user_token.email:
#             # user_token.email = None
#             # user_token.reset_password_token = None
#         user_token.delete()
#         return render(request, 'authentication/password_reset_complete.html')
#     return render(request, 'authentication/reset_password.html', {'token': token})









@api_view(['DELETE'])
def deleteUserProfile(request, user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
        user.delete()
        try:
            data = QuestionHistory.objects.get(user=user_id)
            data.delete()
        except:
            print('No history')
            pass

        return JsonResponse({'message': 'User profile deleted successfully.'}, status=204)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User does not exist.'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    

  


from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import  urlsafe_base64_decode
# from django.utils.encoding import force_bytes
from django.core.mail import send_mail



# class PasswordResetAPI(View):
#     def get(self, request):
#         return JsonResponse({'error': 'GET method not supported for this endpoint.'}, status=405)
    
#     def post(self, request):
#         email = request.POST.get('email')
#         user = CustomUser.objects.filter(email=email).first()
#         if user:
#             token_generator = PasswordResetTokenGenerator()
#             uid = urlsafe_base64_encode(force_bytes(user.pk))
#             print(uid)
#             token = token_generator.make_token(user)
#             reset_link = f'http://127.0.0.1:8000/reset-password/{uid}/{token}/'
#             send_mail(
#                 'Password Reset',
#                 f'Please click the link to reset your password: {reset_link}',
#                 'sampleuser788@gmail.com',
#                 [email],
#                 fail_silently=False,
#             )
#             return JsonResponse({'message': 'Password reset link sent successfully.'})
#         else:
#             return JsonResponse({'error': 'User not found.'}, status=404)
        






from django.urls import reverse
import base64



import site2.ip as ip
@csrf_exempt
def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = get_object_or_404(CustomUser, email=email)
        token = default_token_generator.make_token(user)
        uid_bytes = str(user.pk).encode('utf-8')
        uid = base64.urlsafe_b64encode(uid_bytes).decode('utf-8')
        print(user.pk,uid)

        reset_link = request.build_absolute_uri(
            reverse('reset_password') + f'?uid={uid}&token={token}'
        )
        send_mail(
            'Reset Your Password',
            f'Click the following link to reset your password: {reset_link}',
            'from@example.com',
            [email],
            fail_silently=False,
        )
        return render(request, 'mail_sent.html',{'email':email,'ip':ip.ip})
    elif request.method == 'GET':
        # Handle GET request if needed, for example, you can render a form to collect email
        return render(request, 'get_email.html')

    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)




@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        print(request.GET)

        uid = request.POST.get('uid')
        token = request.POST.get('token')
        print("a",uid,token)

        user_id = urlsafe_base64_decode(uid).decode('utf-8')
        user = CustomUser.objects.get(pk=user_id)
        if default_token_generator.check_token(user, token):
            new_password = request.POST.get('new_password')
            user.set_password(new_password)
            user.save()
            return render(request, 'success.html',{'ip':ip.ip})

        else:
            return JsonResponse({'error': 'Invalid or expired reset token.'}, status=400)
    elif request.method == 'GET':
        print(request.GET)
        # Handle GET request if needed, for example, you can render a form to reset password
        uid = request.GET['uid']
        token = request.GET['token']
        return render(request, 'new.html',{"uid":uid,"token":token})

    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=400)