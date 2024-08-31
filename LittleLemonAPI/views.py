from django.shortcuts import render, get_object_or_404
from rest_framework import generics,status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes,throttle_classes
from rest_framework import generics
from .models import MenuItem,Cart,OrderItem,Order,Category
from .serializers import MenuItemSerializer,CategorySerializer,UserSerializer,CartSerializer,OrderSerializer,OrderItemSerializer
from django.contrib.auth.models import User,Group
from .permissions import IsManagerORAdmin,IsDeliveryCrew,IsManager,IsCustomer
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

class MenuItemView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated, IsManagerORAdmin]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(),IsManagerORAdmin()]  # Allowing only managers to use this method
        else:
            return [IsAuthenticated()]

class SingleMenuItemView(generics.RetrieveUpdateAPIView, generics.DestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    permission_classes = [IsAuthenticated, IsManagerORAdmin]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    

    
    def get_permissions(self):
        if self.request.method in ['POST','PUT','PATCH','DELETE']:
            return [IsAuthenticated(), IsManagerORAdmin()]  # Allowing only managers to use this method
        else:
            return [IsAuthenticated()]


@api_view(['GET','POST','DELETE'])
@permission_classes([IsManagerORAdmin])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def managers(request):
    if request.method == 'GET':
        manager_group = Group.objects.get(name='Manager')
        manager_users = User.objects.filter(groups=manager_group)
        serializer = UserSerializer(manager_users, many=True)
        return Response(serializer.data)
    else:
        username = request.data['username']
        if username:
            user = get_object_or_404(User,username=username)
            crew = Group.objects.get(name="Manager")
            if request.method == 'POST':
                crew.user_set.add(user)
            if request.method == 'DELETE':
                crew.user_set.remove(user)        
            return Response({'message':'OK'})
        return Response({'message':'error'},status.HTTP_400_BAD_REQUEST)


@api_view(['GET','POST','DELETE'])
@permission_classes([IsManagerORAdmin])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def deliverycrew(request):
    if request.method == 'GET':
        delivery_group = Group.objects.get(name='Delivery Crew')
        delivery_users = User.objects.filter(groups=delivery_group)
        serializer = UserSerializer(delivery_users, many=True)
        return Response(serializer.data)
    else:
        username = request.data['username']
        if username:
            user = get_object_or_404(User,username=username)
            crew = Group.objects.get(name="Delivery Crew")
            if request.method == 'POST':
                crew.user_set.add(user)
            if request.method == 'DELETE':
                crew.user_set.remove(user)        
            return Response({'message':'OK'})
        return Response({'message':'error'},status.HTTP_400_BAD_REQUEST)

class CartView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        menuitem = serializer.validated_data['menuitem']
        unitprice = menuitem.price
        quantity = serializer.validated_data['quantity']
        price = unitprice*quantity
        serializer.save(user=self.request.user,unit_price=unitprice,price=price)

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class OrderView(generics.ListCreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    """def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        if self.request.method == 'POST':
            serializer_class.Meta.fields = ['date'] 
        else:
            serializer_class.Meta.fields = '__all__'
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)"""

    def get_queryset(self):
        if self.request.user.groups.filter(name='Delivery Crew').exists():
            return Order.objects.filter(delivery_crew=self.request.user)
        elif self.request.user.is_staff or self.request.user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        else:
            return Order.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        user = request.user 
        cart_items = Cart.objects.filter(user=user)
        if cart_items.exists():
            total = 0
            for cart_item in cart_items:
                total += cart_item.price
    
            orderdata_dict = {'user': user.id, 'delivery_crew': None, 'status': False, 'total': total}
            serializer = OrderSerializer(data=orderdata_dict)
            serializer.is_valid(raise_exception=True)
            order = serializer.save()
            order_items_data = []
            for cart_item in cart_items:
                order_item_data = {
                    'order':order.id,
                    'menuitem': cart_item.menuitem.pk,
                    'quantity': cart_item.quantity,
                    'unit_price':cart_item.unit_price,
                    'price':cart_item.price
                }
                order_items_data.append(order_item_data)

            order_item_serializer = OrderItemSerializer(data=order_items_data, many=True)
            if order_item_serializer.is_valid():
                order_item_serializer.save()
                cart_items.delete()    
                return Response(order_item_serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(order_item_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("No items in the cart to create order", status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET','DELETE','PUT','PATCH'])
@throttle_classes([AnonRateThrottle, UserRateThrottle])
def orderitemview(request,pk):
    order_items = OrderItem.objects.filter(order_id=pk)
    order = Order.objects.get(pk=pk)
    if request.method == 'GET':
        if not(request.user.groups.exists()):
            if order.user == request.user:
                serialized = OrderItemSerializer(data=order_items,many=True)
                serialized.is_valid()
                return Response(serialized.data)
            else:
                return Response({'message':'not authourized'},status=status.HTTP_403_FORBIDDEN)
            
        elif request.user.groups.filter(name='Manager').exists():
            serialized = OrderItemSerializer(data=order_items,many=True)
            serialized.is_valid()
            return Response(serialized.data)
        
        elif request.user.groups.filter(name='Delivery Crew').exists():
            delivery_orders = Order.objects.filter(delivery_crew=request.user)
            serialized = OrderItemSerializer(data=order_items,many=True)
            serialized.is_valid()
            return Response(serialized.data)
  
    if request.method in ['PUT','PATCH','DELETE']:
        if request.user.groups.filter(name='Manager').exists():
            data = request.data
            if data:
                if 'status' in data:
                    order.status = data['status']
                if 'delivery_crew' in data:
                    id = data['delivery_crew']
                    user= User.objects.get(id=id)
                    user_group = user.groups.filter(name='Delivery Crew').exists()
                    if not user_group:
                        return Response({'message':'User is not a Delivery Crew member'},status=status.HTTP_400_BAD_REQUEST)
                    order.delivery_crew = user
                order.save()
                return Response({'message':'Put request successful'},status=status.HTTP_201_CREATED)
            return Response({'message':'invalid data'},status=status.HTTP_400_BAD_REQUEST)
        
        if request.user.groups.filter(name='Delivery Crew').exists():
            data = request.data
            if 'status' not in data:
                return Response({'message':'Only allowed to change status'},status=status.HTTP_403_FORBIDDEN)
            if data['status'] not in ('0','1'):
                return Response({'error': 'Invalid status value (0 or 1 allowed)'}, status=status.HTTP_400_BAD_REQUEST)
            
            order.status = data['status']
            order.save()
            return Response({'message':'Patch request successful'},status=status.HTTP_201_CREATED)
        
        elif not(request.user.groups.exists()):
            return Response({'message':'Not Authorized to perform this'},status=status.HTTP_401_UNAUTHORIZED)
        return Response({'message':'no user found'})