from django import forms
from django.contrib.auth.models import User
from django.contrib.admin import widgets as django_widgets

from contest.utils import print_variables_debug
from .models import Attempt, Team, Contest, Test, get_contest_code_path, Profile, Group, C_Specification


class DateInputWidget(forms.DateTimeInput):
	input_type = 'datetime-local'


class AttemptModelForm(forms.ModelForm):
	comment = forms.CharField(required=False)
	class Meta:
		model = Attempt
		fields = ['file', 'comment']

	def submit(self, user, can_submit, contest, team):
		if can_submit and self.is_valid():
			obj = self.save(commit=False)
			obj.user = user
			obj.contest = contest
			obj.team = team
			obj.save()
			print_variables_debug([
				"Object: " + str(obj),
				"Object file: " + str(obj.file),
				"Object file path: " + str(obj.file.path),
				"Contest object: " + str(contest)
			])
			return True, obj
		return False, None



class CreateContestModelForm(forms.ModelForm):
	class Meta:
		model = Contest
		#widgets = {'start_date': DateInputWidget(), 'end_date': DateInputWidget()}
		fields = "__all__"


	def submit(self):
		if self.is_valid():
			self.save()
			return True
		return False




class CreateTestModelForm(forms.ModelForm):
	override_default_specifications = forms.BooleanField(required=False, initial=False, label='Override contest programming language specifications?')

	class Meta:
		model = Test
		exclude = ['contest']

	def submit(self, contest):
		"""
			returns (formSaved, overrideSpecs)
			If override specs is true redirect to the specs creation page
		"""
		if self.is_valid():
			test = self.save(commit=False)
			test.contest = contest
			test.save()
			return True, not not self.data['override_default_specifications']
		return False, False

class C_SpecificationCreateForm(forms.ModelForm):
	class Meta:
		model = C_Specification
		exclude = ['contest', 'test']
		#fields = "__all__"

	def submit(self, obj):
		if not self.is_valid() or not obj:
			return False
		if type(obj) == Contest:
			self.contest = obj
		elif type(obj) == Test:
			self.test = obj
		else:
			return False
		spec = self.save(commit=False)
		spec.save()
		return True
class UserEditForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['first_name', 'last_name']

class ProfileEditForm(forms.ModelForm):
	number = forms.IntegerField(required=True, label='Student Number')
	gprd = forms.BooleanField(required=True, initial=False,
							  label='Agree to share my information (name, email, number, username, grade) with the authors and other users of this application')
	class Meta:
		model = Profile
		fields = ['number', 'gprd']


class TeamMemberApprovalForm(forms.Form):
	member_id = forms.CharField(required=False)
	member_id_remove = forms.CharField(required=False)
	team_remove = forms.CharField(required=False)


class TeamJoinForm(forms.Form):
	join_code = forms.SlugField(required=True, label='Code')

	def submit(self, user, contest):
		if not self.is_valid():
			return False
		team = Team.objects.filter(join_code=self.data['join_code'], contest=contest).first()
		if not team:
			self.add_error('join_code', 'There is no team with this join_code in this contest.')
			return False
		if team.hasUser(user):
			self.add_error('join_code', 'You already belong to this team.')
			return False
		if team.isFull():
			self.add_error('join_code', 'This team is full.')
		team.users.add(user)
		team.save()
		return True


class TeamCreateForm(forms.ModelForm):
	name = forms.CharField(required=True, label='Team Name')
	join_code = forms.SlugField(required=True, label='Join code')
	class Meta:
		model = Team
		fields = ['name', 'join_code']

	def submit(self, user, contest):
		if not self.is_valid():
			return False

		# Check if the team name is already in use
		team = Team.objects.filter(name=self.data['name'], contest=contest).exists()
		if team:
			self.add_error('name', 'The name you entered is already in use by other team')
			return False
		# Check if the team join code is already in use
		team = Team.objects.filter(join_code=self.data['join_code'], contest=contest).exists()
		if team:
			self.add_error('join_code', 'The code you entered is already in use by other team.')
			return False
		team = self.save(commit=False)
		team.contest = contest
		team.save()
		team.users.add(user)
		return True



class TestForm(forms.Form):
	pass

class GroupCreateForm(forms.ModelForm):
	name = forms.CharField(required=True, label='Group Name')
	join_code = forms.SlugField(required=True, label='Join code')
	registration_open = forms.BooleanField(required=False, label='Open registration?')
	# TODO: Find a way to make these checkbox selects scrollable
	# contests = forms.ModelMultipleChoiceField(required=False, label='Contests', queryset=Contest.objects.all(), widget=forms.CheckboxSelectMultiple)

	class Meta:
		model = Group
		fields = ['name', 'join_code', 'registration_open']

class GroupJoinForm(forms.Form):
	join_code = forms.SlugField(required=True, label='Code')

	def submit(self, user):
		if not self.is_valid():
			return False
		group = Group.objects.filter(join_code=self.data['join_code']).first()
		if not group:
			self.add_error('join_code', 'There is no group with this join_code.')
			return False
		if not group.registration_open:
			self.add_error('join_code', 'Registration for this group is closed.')
			return False
		if group.hasUser(user):
			self.add_error('join_code', 'You already belong to this group.')
			return False
		group.users.add(user)
		group.save()
		return True


# CUSTOM FIELDS

class ContestsModelChoiceField(forms.ModelChoiceField):
	def label_from_instance(self, contest):
		return contest.short_name

class UsersModelChoiceField(forms.ModelChoiceField):
	def label_from_instance(self, user):
		return "" + user.first_name + " " + user.last_name