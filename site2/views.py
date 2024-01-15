from django.shortcuts import render


from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import UserSerializer
from .models import QuizQuestion
from .serializers import QuizQuestionSerializer
from rest_framework.permissions import IsAuthenticated


from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from .models import CustomUser

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
        


















    
# from .models import QuestionHistory
# from .serializers import QuestionHistorySerializer


# class QuestionHistoryDetailView(generics.RetrieveUpdateDestroyAPIView):
#     # queryset = QuestionHistory.objects.all()
#     # serializer_class = QuestionHistorySerializer
#     def get(self, request, user_id):
#         try:
#             # Retrieve question history for the specified user ID
#             user_id = self.request.query_params.get('user', None)
#             if user_id:
#                 queryset = queryset.filter(user_id=user_id)

#             # question_history = QuestionHistory.objects.filter(user_id=user_id)
#             # serializer_class = QuestionHistorySerializer
#             # serializer = QuestionHistorySerializer(question_history, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)