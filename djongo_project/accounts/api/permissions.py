from rest_framework import permissions

from accounts.models import Role


class ANonPermissionOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class StaffOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role <= Role.STAFF


class UserOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == Role.NORMAL


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == Role.ADMIN
