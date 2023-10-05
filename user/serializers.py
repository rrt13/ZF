from rest_framework import serializers
from .models import User, AdvisorClient

role_choices = [('user', 'User'), ('advisor', 'Advisor'), ('admin', 'Admin')]

class SignupSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=150, required=False)
    phone_number = serializers.CharField(max_length=10, required=True)
    role = serializers.ChoiceField(choices=role_choices, default='user', required=False)
    
    def validate_phone_number(self, value):
        if len(value) != 10 or not value.isdigit():
            raise serializers.ValidationError("Phone number should be 10 digits and valid format.")
        return value

class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        exclude = ('id','is_verified','is_active','is_deleted','password','last_login','is_staff')
        
class AdvisorClientsListSerializer(serializers.ModelSerializer):
    client = serializers.SerializerMethodField()  # Create a SerializerMethodField for client

    class Meta:
        model = AdvisorClient
        fields = ['id','client']

    def get_client(self, obj):
        client = obj.client
        return UserSerializer(client).data