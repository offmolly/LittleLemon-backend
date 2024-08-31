from rest_framework import permissions

class IsCustomer(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and not(request.user.groups.exists()))
    
class IsManagerORAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.user.is_staff or request.user.groups.filter(name='Manager').exists())
    
class IsDeliveryCrew(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='Delivery Crew').exists())
    
class IsManager(permissions.BasePermission):

    def has_permission(self, request, view):
        return bool(request.user and request.user.groups.filter(name='Manager').exists())