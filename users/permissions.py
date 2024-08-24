from rest_framework import permissions

class CustomReadOnly(permissions.BasePermission):
    def has_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS: # GET같은 데이터에 영향을 주지 않는 요청은 허용
            return True
        return obj.user == request.user