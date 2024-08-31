from django.urls import path,include
from . import views

urlpatterns = [
    path('menu-item/', views.MenuItemView.as_view()),
    path('menu-item/<int:pk>', views.SingleMenuItemView.as_view()),
    path('',include('djoser.urls')),
    path('',include('djoser.urls.authtoken')),
    path('groups/managers/users',views.managers),
    path('groups/delivery-crew/users',views.deliverycrew),
    path('cart/menu-items',views.CartView.as_view()),
    path('orders/',views.OrderView.as_view()),
    path('orders/<int:pk>',views.orderitemview),
]