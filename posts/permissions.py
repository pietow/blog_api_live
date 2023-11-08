from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        print('author: ',obj.author)
        print('user: ', request.user)
        print('superuser: ', request.user.is_superuser)
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_superuser or obj.author == request.user




        