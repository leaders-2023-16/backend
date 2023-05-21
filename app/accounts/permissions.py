from accounts.models import User
from rest_framework import permissions


class OwnProfilePermission(permissions.BasePermission):
    """
    Object-level permission to only allow updating his own profile
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # obj here is a UserProfile instance
        return obj.user == request.user


class IsCandidate(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.CANDIDATE


class IsTrainee(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.TRAINEE


class IsMentor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.MENTOR


class IsCurator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.CURATOR


class IsPersonnel(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == User.Role.PERSONNEL
