from django.db import models
from user.models import User

class Category(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class ProductLink(models.Model):
    id = models.BigAutoField(primary_key=True)
    advisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advisor_products')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    link = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.client.full_name}'s {self.product.name} Link"
