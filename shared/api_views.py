from rest_framework import generics, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import permissions
from rest_framework import status
from api.permissions import IsStaffEditorPermission, OwnUserPermission, OwnTeamPermission
from shared.models import Group, Team


# from django.http import Http404
from django.shortcuts import get_object_or_404
from api.mixins import (
	StaffEditorPermissionMixin,
	UserQuerySetMixin,
	OwnerOrModelPermissionMixin
	)

from django.contrib.auth.models import User
from .models import Contest, Profile
from .serializers import (
	ContestSerializer, 
	ProfileSerializer, 
	UserSerializer, 
	GroupSerializer, 
	GroupAdminSerializer, 
	GroupAdminDetailSerializer,
	TeamSerializer)

class ContestListCreateAPIView(
	UserQuerySetMixin,
	OwnerOrModelPermissionMixin,
	generics.ListCreateAPIView):
	queryset = Contest.objects.all()
	serializer_class = ContestSerializer

#    def perform_create(self, serializer):
#        # serializer.save(user=self.request.user)
#        title = serializer.validated_data.get('title')
#        content = serializer.validated_data.get('content') or None
#        if content is None:
#            content = title
#        serializer.save(user=self.request.user, content=content)
		# send a Django signal
	
	# def get_queryset(self, *args, **kwargs):
	#     qs = super().get_queryset(*args, **kwargs)
	#     request = self.request
	#     user = request.user
	#     if not user.is_authenticated:
	#         return Contest.objects.none()
	#     # print(request.user)
	#     return qs.filter(user=request.user)


contest_list_create_view = ContestListCreateAPIView.as_view()

class ContestDetailAPIView(
	UserQuerySetMixin, 
	StaffEditorPermissionMixin,
	generics.RetrieveAPIView):
	queryset = Contest.objects.all()
	serializer_class = ContestSerializer
	# lookup_field = 'pk' ??

contest_detail_view = ContestDetailAPIView.as_view()


class ContestUpdateAPIView(
	UserQuerySetMixin,
	StaffEditorPermissionMixin,
	generics.UpdateAPIView):
	queryset = Contest.objects.all()
	serializer_class = ContestSerializer
	lookup_field = 'pk'

	def perform_update(self, serializer):
		instance = serializer.save()
		if not instance.content:
			instance.content = instance.title
			## 

contest_update_view = ContestUpdateAPIView.as_view()


class ContestDestroyAPIView(
	UserQuerySetMixin,
	StaffEditorPermissionMixin,
	generics.DestroyAPIView):
	queryset = Contest.objects.all()
	serializer_class = ContestSerializer
	lookup_field = 'pk'

	def perform_destroy(self, instance):
		# instance 
		super().perform_destroy(instance)

contest_destroy_view = ContestDestroyAPIView.as_view()

# class ContestListAPIView(generics.ListAPIView):
#     '''
#     Not gonna use this method
#     '''
#     queryset = Contest.objects.all()
#     serializer_class = ContestSerializer

# Contest_list_view = ContestListAPIView.as_view()


class ContestMixinView(
	mixins.CreateModelMixin,
	mixins.ListModelMixin,
	mixins.RetrieveModelMixin,
	generics.GenericAPIView
	):
	queryset = Contest.objects.all()
	serializer_class = ContestSerializer
	lookup_field = 'pk'

	def get(self, request, *args, **kwargs): #HTTP -> get
		pk = kwargs.get("pk")
		if pk is not None:
			return self.retrieve(request, *args, **kwargs)
		return self.list(request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		return self.create(request, *args, **kwargs)
	
	def perform_create(self, serializer):
		# serializer.save(user=self.request.user)
		title = serializer.validated_data.get('title')
		content = serializer.validated_data.get('content') or None
		if content is None:
			content = "this is a single view doing cool stuff"
		serializer.save(content=content)

	# def post(): #HTTP -> post

contest_mixin_view = ContestMixinView.as_view()


#################################################3
# users and user profile
#################################################

class UserDetailUpdateAPIView(generics.RetrieveUpdateAPIView):
	permission_classes = [OwnUserPermission]
	queryset = User.objects.all()
	serializer_class = UserSerializer
	lookup_field = 'pk'

user_detail_update_view = UserDetailUpdateAPIView.as_view()

class UserListCreateAPIView(generics.ListCreateAPIView):
	permission_classes = [permissions.IsAdminUser]

	queryset = User.objects.all()
	serializer_class = UserSerializer
	lookup_field = 'pk'

	def perform_create(self, serializer):
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

profile_list_create_view = UserListCreateAPIView.as_view()



# Delete User - Can we even allow a user to be deleted?
# class UserDestroy(generics.DestroyAPIView):
#     permission_classes = [permissions.IsAdminUser]
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     lookup_field = 'pk'
#     def perform_destroy(self, instance):
#         # instance 
#         super().perform_destroy(instance)
# user_destroy_view = UserDestroy.as_view()



#################################################
# Groups
#################################################

class GroupDetailAPIView(generics.RetrieveAPIView):
	permission_classes = [permissions.IsAuthenticated]
	queryset = Group.objects.all()
	lookup_field = 'pk'

	def get_serializer_class(self):
		if self.request.user.is_staff:
			return GroupAdminDetailSerializer
		return GroupSerializer


class GroupUpdateAPIView(generics.UpdateAPIView):
	permission_classes = [permissions.IsAdminUser]
	queryset = Group.objects.all()
	lookup_field = 'pk'
	serializer_class = GroupAdminSerializer

group_detail_view = GroupDetailAPIView.as_view()
group_update_view = GroupUpdateAPIView.as_view()


class GroupListAPIView(generics.ListAPIView):
	permission_classes = [permissions.IsAuthenticated]

	queryset = Group.objects.all()
	def get_serializer_class(self):
		if self.request.user.is_staff:
			return GroupAdminSerializer
		return GroupSerializer

class GroupCreateAPIView(generics.CreateAPIView):
	permission_classes = [permissions.IsAdminUser]

	queryset = Group.objects.all()
	serializer_class = GroupAdminSerializer


group_list_view = GroupListAPIView.as_view()
group_create_view = GroupCreateAPIView.as_view()



class GroupDestroyAPIView(generics.DestroyAPIView):
	permission_classes = [permissions.IsAdminUser]
	queryset = Group.objects.all()
	serializer_class = GroupAdminSerializer
	lookup_field = 'pk'
	def perform_destroy(self, instance):
#         # instance 
		super().perform_destroy(instance)
		
group_destroy_view = GroupDestroyAPIView.as_view()


#################################################
# Teams
#################################################


## team Detail (admin or user's team)
class TeamDetailAPIView(generics.RetrieveAPIView):
	permission_classes = [OwnTeamPermission]
	queryset = Team.objects.all()
	lookup_field = 'pk'
	serializer_class = TeamSerializer


team_detail_view = TeamDetailAPIView.as_view()

## create (any user)
# conditions to be able to create:
# authenticated
# 	does not have a team on the selected contest




## join (any user)
# conditions to be able to join:
# authenticated
# 	does not have a team on the selected contest
#	must provide the valid code

## leave a team (any user)




## list (admins)
class TeamListAPIView(generics.ListAPIView):
	permission_classes = [permissions.IsAdminUser]

	queryset = Team.objects.all()
	serializer_class = TeamSerializer


team_list_view = TeamListAPIView.as_view()
