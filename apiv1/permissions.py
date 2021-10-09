from account.models import User
from rest_framework import permissions

"""User Model"""


class InOwnOrReadOnly(permissions.BasePermission):
    """Allow user to edit their own usermodel"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user


"""Profile Model"""


class IsOwnProfileOrReadOnly(permissions.BasePermission):
    """Allow user to edit their own profile"""

    def has_object_permission(self, request, view, obj):
        """Check user is trying to edit their own profile"""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


"""Post Model"""


class IsOwnPostOrReadOnly(permissions.BasePermission):
    """Allow user to edit their own profile"""

    def has_object_permission(self, request, view, obj):
        """Check user is trying to edit their own post"""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.posted_by == request.user

# class IsMyLookBack(permissions.BasePermission):
#     def has_object_permission(self, request, view, obj):
#         return obj.step.roadmap.challenger.id == request.user.id
