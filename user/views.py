from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth import login, logout
from .models import OTP, User, Token, AdvisorClient
from .authentication import token_protect
import random, base64
import httpagentparser
from .serializers import SignupSerializer, UserSerializer, AdvisorClientsListSerializer

# Create your views here.
GENERATE_UNIQUE_ID = lambda details : base64.b64encode(str(details).encode('utf-8')).decode('utf-8')

def send_otp(phone_number):
    # Check if an active, unexpired OTP exists for the provided phone number
        existing_otp = OTP.objects.filter(phone_number=phone_number, is_used=False, expiration_time__gte=timezone.now()).first()
        if existing_otp:
            # If an active OTP exists, return it without generating a new one
            return existing_otp

        # Generate a new OTP
        otp_value = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        expiration_time = timezone.now() + timezone.timedelta(minutes=5)

        # Save the new OTP in the database
        otp = OTP(phone_number=phone_number, otp_value=otp_value, expiration_time=expiration_time)
        otp.save()
        return otp_value
        
class SignUp(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            print("valid  ")
            full_name = serializer.validated_data.get('full_name')
            phone_number = serializer.validated_data['phone_number']
            role = serializer.validated_data['role']

            # Generate a random OTP (6 digits)
            random_pass = ''.join([str(random.randint(0, 9)) for _ in range(6)])

            # Create a new user with the provided data
            user, flag = User.objects.get_or_create(full_name=full_name, phone_number=phone_number, role=role)
            if not flag:
                return Response({'message': 'Already Registered, Please Login!'}, status=status.HTTP_201_CREATED)
                
            user.set_password(random_pass)
            user.is_verified=False
            user.save()

            # Send the OTP to the user
            send_otp(phone_number)
            return Response({'message': 'OTP sent succesfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class Login(APIView):
    def post(self, request):
        
        phone_number = request.data.get('phone_number')
        user = User.objects.get(phone_number=phone_number, is_verified=True)
        if user:
            # Send the OTP to the user
            send_otp(phone_number)
            return Response({'message': 'OTP sent succesfully!'}, status=status.HTTP_200_OK)
        else:
            return Response({'message': 'User not registered!'}, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTP(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp_value = request.data.get('otp_value')

        # Find the OTP associated with the provided phone number
        otp = OTP.objects.filter(phone_number=phone_number, otp_value=otp_value, is_used=False, expiration_time__gte=timezone.now()).first()

        
        if otp:
            # Mark the OTP as used
            otp.is_used = True
            otp.save()
            
            user = User.objects.get(phone_number=phone_number)
            user.is_verified=True
            user.save()
            
            # create new token for every login
            login(request, user)
        
            user_agent = request.META['HTTP_USER_AGENT']
            details = httpagentparser.detect(user_agent)
            unique_id = GENERATE_UNIQUE_ID(details)
            
            new_token, _ = Token.objects.get_or_create(user=user, device_key = unique_id)
        
            return Response({'message': 'User Registered Successfully','token': new_token.key}, status=status.HTTP_200_OK)
        else: #this is basically hardcoding for the time being
            user = User.objects.get(phone_number=phone_number)
            print("user ", user)
            user.is_verified=True
            user.save()
            
            # create new token for every login
            login(request, user)
        
            user_agent = request.META['HTTP_USER_AGENT']
            details = httpagentparser.detect(user_agent)
            unique_id = GENERATE_UNIQUE_ID(details)
            
            new_token, _ = Token.objects.get_or_create(user=user, device_key = unique_id)
        
            return Response({'message': 'User Registered Successfully','token': new_token.key}, status=status.HTTP_200_OK)
        return Response({'message': 'Invalid OTP or OTP has expired'}, status=status.HTTP_400_BAD_REQUEST)

class Client(APIView):
    
    @token_protect
    def post(self, request, *args, **kwargs):
        token = kwargs['token']
        user = token.user
        if user.role != "advisor":
            return Response({'message': 'Only Advisor can perform this action!'}, status=status.HTTP_401_UNAUTHORIZED)
            
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            full_name = serializer.validated_data.get('full_name')
            phone_number = serializer.validated_data['phone_number']
            role = serializer.validated_data['role']

            # generate a random OTP (6 digits)
            random_pass = ''.join([str(random.randint(0, 9)) for _ in range(6)])

            # create a new client with the provided data
            client, flag = User.objects.get_or_create(full_name=full_name, phone_number=phone_number, role=role,)
            client.set_password(random_pass)
            client.is_verified=True
            client.save()
            data = UserSerializer(client).data
            
            # check if the relationship already exists
            if AdvisorClient.objects.filter(advisor=user, client=client, is_active=True).exists():
                return Response({'message': 'Client is already assigned to this advisor.'}, status=status.HTTP_400_BAD_REQUEST)

            # Create the relationship
            advisor_client = AdvisorClient(advisor=user, client=client)
            advisor_client.save()
            if flag:
                message = 'Client added to advisor successfully.'
            else:
                message = 'Client edited in advisor successfully.'
                
            return Response({'message': message, 'data':data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @token_protect
    def get(self, request, *args, **kwargs):
        token = kwargs['token']
        params = request.GET
        advisor_id = params.get('advisor_id', None)
        print("user ", token)
        
        user = token.user
        print("user ", user)
        if user.role != "advisor":
            return Response({'message': 'Only Advisor can perform this action!'}, status=status.HTTP_401_UNAUTHORIZED)
        clients = AdvisorClient.objects.filter(advisor__id=advisor_id)
        data = AdvisorClientsListSerializer(clients,many=True).data
        return Response({'message': 'List of clients','data': data}, status=status.HTTP_200_OK)
        
    
@api_view(["GET", "POST", "DELETE", "PUT"])
def other_url(request):
    return Response({"status":False,"error":'Please check url again!'}, status=status.HTTP_406_NOT_ACCEPTABLE)
