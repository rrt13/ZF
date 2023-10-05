from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import Category, Product, ProductLink
from .serializers import CategorySerializer, ProductSerializer, ProductLinkSerializer
from user.models import User
from .authentication import token_protect_advisor
import secrets
import string

def generate_unique_link(client_id, product_id):
    # Combine client ID and product ID to form the base of the link
    link_base = f"C{client_id}_P{product_id}_"

    # Generate a random string of characters to make the link unique
    random_data = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(10))

    # Combine the link base and random data
    unique_link = f"{link_base}{random_data}"

    return unique_link

class CreateProduct(APIView):
    def post(self, request):
        category_name = request.data.get('category')
        product_name = request.data.get('name')
        product_description = request.data.get('description')

        #if category exists
        category, created = Category.objects.get_or_create(name=category_name)

        # Create the product
        product, flag = Product.objects.get_or_create(name=product_name, description=product_description, category=category)

        serializer = ProductSerializer(product)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class PurchaseProduct(APIView):
    @token_protect_advisor
    def post(self, request, *args, **kwargs):
        token = kwargs['token']
        advisor = token.user
        client_id = request.data.get('client_id')
        product_id = request.data.get('product_id')

        try:
            client = User.objects.get(id=client_id, role='user')
            product = Product.objects.get(id=product_id)

            link = generate_unique_link(client_id, product_id)

            # Create the product link
            product_link = ProductLink.objects.create(advisor=advisor, client=client, product=product, link=link)

            serializer = ProductLinkSerializer(product_link)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({'message': 'Client not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Product.DoesNotExist:
            return Response({'message': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(["GET", "POST", "DELETE", "PUT"])
def other_url(request):
    return Response({"status":False,"error":'Please check url again!'}, status=status.HTTP_406_NOT_ACCEPTABLE)
