from rest_framework import generics, mixins
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import permissions
from rest_framework import status
from django.core.exceptions import PermissionDenied
from rest_framework import serializers
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.permissions import AllowAny



from api.permissions import IsStaffEditorPermission, OwnUserPermission, OwnTeamPermission, UserDoesNotHaveTeamOnContest, IsAdminGroupStaffTeamOwner, IsAdminOrStaff, AnyUser
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
	TeamSerializer,
	TeamCreateSerializer,
	TeamUpdateSerializer,
	TeamJoinSerializer,
	)

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

class UserListAPIView(generics.ListAPIView):
	permission_classes = [IsAdminOrStaff]

	queryset = User.objects.all()
	serializer_class = UserSerializer
	lookup_field = 'pk'

class UserCreateAPIView(generics.CreateAPIView):
	permission_classes = [AnyUser]

	queryset = User.objects.all()
	serializer_class = UserSerializer
	lookup_field = 'pk'

profile_list_view = UserListAPIView.as_view()
user_detail_update_view = UserDetailUpdateAPIView.as_view()
profile_create_view = UserCreateAPIView.as_view()


######################## Group Api Views ########################

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
	serializer_class = GroupAdminDetailSerializer

class GroupListAPIView(generics.ListAPIView):
	permission_classes = [IsAdminOrStaff]
	queryset = Group.objects.all()
	def get_serializer_class(self):
		if self.request.user.is_staff:
			return GroupAdminSerializer
		return GroupSerializer

class GroupCreateAPIView(generics.CreateAPIView):
	permission_classes = [permissions.IsAdminUser]

	queryset = Group.objects.all()
	serializer_class = GroupAdminSerializer

class GroupDestroyAPIView(generics.DestroyAPIView):
	permission_classes = [permissions.IsAdminUser]
	queryset = Group.objects.all()
	serializer_class = GroupAdminSerializer
	lookup_field = 'pk'
	def perform_destroy(self, instance):
		super().perform_destroy(instance)

group_destroy_view = GroupDestroyAPIView.as_view()
group_detail_view = GroupDetailAPIView.as_view()
group_update_view = GroupUpdateAPIView.as_view()
group_list_view = GroupListAPIView.as_view()
group_create_view = GroupCreateAPIView.as_view()

#################################################
# Teams
#################################################
def isAdminOrGroupStaff(user, contest):
	return user.is_superuser or (user.is_staff and contest.hasUser(user))


def isAdminOrGroupStaffOrTeamOwner(user, team):
	return isAdminOrGroupStaff(user, team.contest) or team.created_by == user


## team Detail (admin or user's team)
class TeamDetailAPIView(generics.RetrieveAPIView):
	permission_classes = [OwnTeamPermission]
	queryset = Team.objects.all()
	lookup_field = 'pk'
	serializer_class = TeamSerializer
	
"""
* create team *
Must:
	- be authenticated
	- belong to group in which the contest also belongs
	- not have a team on the contest
"""
class TeamCreateAPIView(generics.CreateAPIView):
	permission_classes = [permissions.IsAuthenticated]
	
	queryset = Team.objects.all()
	serializer_class = TeamCreateSerializer

	def perform_create(self, serializer):
		if not 'contest' in serializer.validated_data:
			raise PermissionDenied()

		contest_obj = get_object_or_404(Contest, pk=serializer.validated_data['contest'])
		user = self.request.user

		# check if user belongs to group
		if not contest_obj.hasUser(user=user):
			raise PermissionDenied()

		# check if user has a team
		if contest_obj.getUserTeam(user=user):
			raise serializers.ValidationError('User already has a team on this contest') 

		# create a new team
		team = Team.objects.create(name = serializer.validated_data['name'], contest = contest_obj, created_by = self.request.user)
		team.users.add(user)
		team.save()
		return team


"""
* list teams *
Must:
	- be admin or staff of the group
"""
## list (admins)
class TeamListAPIView(generics.ListAPIView):
	permission_classes = [permissions.IsAdminUser]

	queryset = Team.objects.all()
	serializer_class = TeamSerializer



"""
* team patch *
Must:
	- be authenticated and
		- be admin or group staff, or
		- belong to a team, or
		- be the team owner
"""
class TeamUpdateAPIView(generics.UpdateAPIView):
	permission_classes = [permissions.IsAuthenticated]
	queryset = Team.objects.all()
	lookup_field = 'pk'
	serializer_class = TeamUpdateSerializer

	@transaction.atomic
	def perform_update(self, serializer):
		team = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
		contest = team.contest
		user = self.request.user

		if not isAdminOrGroupStaffOrTeamOwner(user, team):
			raise PermissionDenied()

		if "users" in serializer.initial_data:
			for user_id in serializer.initial_data["users"]:
				user_obj = get_object_or_404(User, id=user_id)
				if team.hasUser(user=user_obj):
					continue

				if (isAdminOrGroupStaff(user, contest)):
						team.users.add(user_obj)
				else:
					raise PermissionDenied()

		if "remove_users" in serializer.initial_data:
			for user_id in serializer.initial_data["remove_users"]:
				user_obj = get_object_or_404(User, id=user_id)

				if team.hasUser(user=user_obj):
					if (isAdminOrGroupStaff(user, contest)) or user != user_obj:
						team.users.remove(user_obj)
					else:
						raise PermissionDenied()					

		if "name" in serializer.validated_data:
			if serializer.validated_data['name'] != team.name:
				team.name = serializer.validated_data['name']
			
		team.save()
		return team

"""
* team destroy *
Must:
	- be authenticated
	- be admin, staff on that group, or team owner
	- team must not have any submissions
"""
class TeamDestroyAPIView(generics.DestroyAPIView):
	permission_classes = [IsAdminGroupStaffTeamOwner]
	queryset = Team.objects.all()
	serializer_class = TeamSerializer
	lookup_field = 'pk'

	def perform_destroy(self, instance):
		if len(instance.getAttempts()) > 0:
			raise serializers.ValidationError('Impossible to delete this team') 

		super().perform_destroy(instance)


"""
* team join *
Must:
	- be authenticated
	- not blong to another team of the same contest
	- number of members of team must be blow maximum
	- user must belong to group
"""
class TeamJoinAPIView(APIView):
	permission_classes = [permissions.IsAuthenticated]
	serializer_class = TeamJoinSerializer

	def put(self, request):
		if 'join_code' in request.data:
			team = Team.objects.get(join_code = request.data['join_code'])
			if not team:
				raise PermissionDenied()					

			if len(team.getUsers()) >= team.contest.max_team_members:
				raise serializers.ValidationError('Team reached maximum number of members') 

			if team.contest.getUserTeam(request.user):
				raise serializers.ValidationError('User already has a team')

			if not team.contest.hasUser(request.user):
				raise PermissionDenied()

			team.users.add(request.user)
			team.save()
			return Response({"id" : team.id, "join_code" : team.join_code}, status=status.HTTP_201_CREATED)
		
		raise PermissionDenied()

class TeamLeaveAPIView(generics.UpdateAPIView):
	permission_classes = [permissions.IsAuthenticated]
	queryset = Team.objects.all()
	lookup_field = 'pk'
	serializer_class = TeamJoinSerializer

	@transaction.atomic
	def perform_update(self, serializer):
		team = get_object_or_404(self.get_queryset(), pk=self.kwargs["pk"])
		contest = team.contest
		user = self.request.user

		if not team.hasUser(user=user) or user == team.created_by:
			raise PermissionDenied()

		team.users.remove(user)
		team.save()

		return team

team_leave_view = TeamLeaveAPIView.as_view()
team_join_view = TeamJoinAPIView.as_view()
team_delete_view = TeamDestroyAPIView.as_view()
team_detail_view = TeamDetailAPIView.as_view()
team_create_view = TeamCreateAPIView.as_view()
team_list_view = TeamListAPIView.as_view()
team_update_view = TeamUpdateAPIView.as_view()
