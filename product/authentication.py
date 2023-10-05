import traceback
from rest_framework.authentication import TokenAuthentication
from user.models import Token
from rest_framework.response import Response
from rest_framework import status


class MyOwnTokenAuthentication(TokenAuthentication):
    model = Token

def token_protect_advisor(view_method):
    def _wrapped_view(*args, **kwargs):
        try:
            request = args[0].request
            token_key = request.META.get('HTTP_TOKEN')
            token = Token.objects.get(key=token_key)
            user = token.user
            if user.role!="advisor":
                return Response({"message": "Not an advisor!"}, status=status.HTTP_401_UNAUTHORIZED)
            kwargs['token'] = token
            return view_method(*args, **kwargs)
        except Token.DoesNotExist:
            return Response({"message": "Invalid/Expired token!"}, status=status.HTTP_401_UNAUTHORIZED)
    return _wrapped_view