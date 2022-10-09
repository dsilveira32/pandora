from rest_framework import permissions
from django.contrib.auth.models import User
from pandora import settings

class IsStaffEditorPermission(permissions.DjangoModelPermissions):
	perms_map = {
		'GET': ['%(app_label)s.view_%(model_name)s'],
		'OPTIONS': [],
		'HEAD': [],
		'POST': ['%(app_label)s.add_%(model_name)s'],
		'PUT': ['%(app_label)s.change_%(model_name)s'],
		'PATCH': ['%(app_label)s.change_%(model_name)s'],
		'DELETE': ['%(app_label)s.delete_%(model_name)s'],
	}


class IsOwnerOrModelPermission(permissions.DjangoModelPermissions):
	def __same_user(self, obj, request):
		print(request.user)
		return isinstance(obj, request.user) and obj.id == request.user.id
    
	def has_permission(self, request, view):
		print(request.user)
		return request.user.is_superuser
    
	def has_object_permission(self, request, view, obj):
		print(request.user)
		# Read permissions are allowed to any request,
		# so we'll always allow GET, HEAD or OPTIONS requests.
		if request.method in permissions.SAFE_METHODS:
			return True

		# obj here is a UserProfile instance
		return obj.user == request.user


class OwnUserPermission(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):
		if request.user.is_superuser or request.user.is_staff:
			return True
		if isinstance(obj, User) and obj.id == request.user.id:
			return True
		return False



class IsAdminOrStaff(permissions.BasePermission):
	def has_permission(self, request, view):
		if request.user.is_superuser or request.user.is_staff:
			return True
		return False


class AnyUser(permissions.BasePermission):
	def has_permission(self, request, view):
		if settings.ENABLE_USER_REGISTRATION or request.user.is_superuser or request.user.is_staff:
			return True




class OwnTeamPermission(permissions.BasePermission):
	def has_object_permission(self, request, view, obj):

		if request.user.is_superuser:
			return True

		if not obj:
			return False

		if obj.hasUser(user=request.user):
			return True

		return False



class UserDoesNotHaveTeamOnContest(permissions.BasePermission):

	def has_object_permission(self, request, view, obj):
		print(obj)

		if request.user.is_superuser:
			return True

		if not obj:
			return False

		if not obj.hasUser(user=request.user):
			return False

		if obj.getUserTeam(user=request.user):
			return False

		return True


class IsAdminGroupStaffTeamOwner(permissions.BasePermission):

	def has_object_permission(self, request, view, obj):

		if request.user.is_superuser:			
			return True

		if obj.create_by == request.user:
			return True

		if request.user.is_staff and obj.getContest().hasUser(request.user):
			return True

		return False

