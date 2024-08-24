from rest_framework import permissions

class CustomReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET': # 글 조회 : 누구나
            return True
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS: # 게시글 수정/삭제 : 해당 글의 작성자만
            return True
        return obj.author == request.user