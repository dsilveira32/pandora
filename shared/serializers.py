from rest_framework import serializers
from rest_framework.reverse import reverse
from django.contrib.auth.hashers import make_password

from api.serializers import UserPublicSerializer
from django.contrib.auth.models import User
from shared.models import Group, Team


from .models import Contest, Profile
from . import validators

class ContestInlineSerializer(serializers.Serializer):
	url = serializers.HyperlinkedIdentityField(
		view_name='contest-detail',
		lookup_field='pk',
		read_only=True
	)


class ContestSerializer(serializers.ModelSerializer):
	#    owner = UserPublicSerializer(source='user', read_only=True)
	class Meta:
		model = Contest
		fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
	class Meta:
		model = Group
		fields = ['id', 'name']

class TeamSerializer(serializers.ModelSerializer):
	class Meta:
		model = Team
		fields = '__all__'

class ProfileSerializer(serializers.ModelSerializer):
	groups = serializers.SerializerMethodField()
	teams = serializers.SerializerMethodField()

	def get_groups(self, obj):
		return GroupSerializer(obj.groups(), many=True).data

	def get_teams(self, obj):
		return GroupSerializer(obj.teams(), many=True).data


	number = serializers.IntegerField(required=False, default=0)
	valid = serializers.BooleanField(required=False, default=False)


	class Meta:
		model = Profile
		fields = ['number', 'valid', 'groups', 'teams']


class UserSerializer(serializers.ModelSerializer):
	profile = ProfileSerializer(required=False, many=False)

	password = serializers.CharField(
		write_only=True,
		required=True,
		help_text='Leave empty if no change needed',
		style={'input_type': 'password', 'placeholder': 'Password'}
	)

	email = serializers.EmailField(required=True, allow_blank=False)
	first_name = serializers.CharField(required=False, default="")
	last_name = serializers.CharField(required=False, default="")
	is_superuser = serializers.BooleanField(required=False, default=False)
	is_staff = serializers.BooleanField(required=False, default=False)
	is_active = serializers.BooleanField(required=False, default=True)

	class Meta:
		model = User
		fields = ('id', 'username', 'email', 'password', 'first_name',
					'last_name', 'is_superuser', 'is_staff', 'is_active', 'last_login', 'date_joined', 'profile')

		read_only_fields = ('id', 'last_login', 'date_joined')


	def create(self, validated_data):
		"""Create and return a new user"""
		userInstance = User.objects.create(email=validated_data['email'],
											username=validated_data['username'],
											first_name=validated_data['first_name'],
											last_name=validated_data['last_name'],
											is_active=True
											)
		userInstance.set_password(validated_data['password'])
		try:
			profile_data = validated_data.pop('profile')
			profile = Profile.objects.get(user=userInstance)
			profile.number = profile_data['number']
			profile.valid = profile_data['valid']
			profile.save()
		except:
			pass
		return User.objects.get(id=userInstance.id)

	def update(self, instance, validated_data):
		if 'email' in validated_data:
			instance.email = validated_data['email']
		if 'first_name' in validated_data:
			instance.first_name = validated_data['first_name']
		if 'last_name' in validated_data:
			instance.last_name = validated_data['last_name']

		user = self.context.get('request').user
		if user.is_authenticated and user.is_superuser:
			if 'is_superuser' in validated_data:
				instance.is_superuser = validated_data['is_superuser']
			if 'is_staff' in validated_data:
				instance.is_staff = validated_data['is_staff']
			if 'is_active' in validated_data:
				instance.is_active = validated_data['is_active']
			if 'username' in validated_data:
				instance.username = validated_data['username']

		try:
			instance.set_password(validated_data['password'])
		except KeyError:
			pass

		try:
			profile_data = validated_data.pop('profile')
			profile = Profile.objects.get(user=instance)
			profile.number = profile_data['number']
			profile.valid = profile_data['valid']
			profile.save()
		except:
			pass		

		instance.save()
		return instance

class GroupAdminSerializer(serializers.ModelSerializer):
	
	join_code = serializers.SlugField(required=False, default="")
	registration_open = serializers.BooleanField(required=False, default=False)

	class Meta:
		model = Group
		fields = ['id', 'name', 'join_code', 'registration_open']
		read_only_fields = ['id']


class GroupAdminDetailSerializer(serializers.ModelSerializer):
	join_code = serializers.SlugField(required=False, default="")
	registration_open = serializers.BooleanField(required=False, default=False)
	contests = serializers.SerializerMethodField()
	users = serializers.SerializerMethodField()

	def get_contests(self, obj):
		return obj.getContests().values_list('id', flat=True)

	def get_users(self, obj):
		return obj.getUsers().values_list('id', flat=True)

	class Meta:
		model = Group
		fields = ['id', 'name', 'join_code', 'registration_open', 'contests', 'users']
		read_only_fields = ['id']