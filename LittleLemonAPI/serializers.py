from rest_framework import serializers
from .models import Category,MenuItem,Cart,Order,OrderItem
from django.contrib.auth.models import User,Group

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['slug','title']

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['title','price','featured','category']


class CartSerializer (serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity','unit_price','price']
        read_only_fields = ['unit_price','price']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
    

class OrderItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OrderItem
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
