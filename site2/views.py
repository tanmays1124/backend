from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import api_view, permission_classes


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

from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

from .utils import generate_reset_token 

@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        print(request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    





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
    


# class UserProfile(generics.ListAPIView):
    
#     serializer_class = UserSerializer
#     def get_queryset(self):
#         # userid = request.data.get('user_id')
            
#         queryset = CustomUser.objects.all()
        
#         user = self.request.query_params.get('user_id', None)

#         if user:
#             queryset = queryset.filter(id=user)
#         return user


@api_view(['GET'])
def get_user_details(request, user_id):
    # Ensure that the user making the request is authenticated

    # Retrieve the user object from the database or return 404 if not found
    user = get_object_or_404(CustomUser, id=user_id)

    # Serialize the user data
    serializer = UserSerializer(user)

    # Return the serialized data as a JSON response
    return Response(serializer.data)




@api_view(['PUT'])
@permission_classes([IsAuthenticated])

def update_user_profile(request):
    user = request.user  # Get the authenticated user

    serializer = UserSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=400)



    
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
    

    # def get_queryset(self):
    #     queryset = QuestionHistory.objects.all()
    #     user_id = self.request.query_params.get('user_id', None)
    #     if user_id:
    #         queryset = queryset.filter(user=user_id)
    #     serialized_data = QuestionHistorySerializer(queryset, many=True).data
    #     print(serialized_data)
    #     return queryset
        

# myapp/views.py



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












