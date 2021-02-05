from django import forms
from django.contrib.auth.models import User

from contest.utils import print_variables_debug
from .models import Attempt, Team, Contest, Test, get_contest_code_path, Profile, Group


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
		# widgets = {'start_date': DateInputWidget(), 'end_date': DateInputWidget()}
		fields = "__all__"


class CreateTestModelForm(forms.ModelForm):

	class Meta:
		model = Test
		fields = "__all__"

	def changed_input_file(self, *args, **kwargs):
		input_file = self.changed_data.get('input_file')

		print("****************************************" + str(input_file) + "****************************************")

		return input_file

	def changed_output_file(self, *args, **kwargs):
		output_file = self.changed_data.get('output_file')

		print("***************************************" + str(output_file) + "****************************************")

		return output_file


class UserEditForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['email','first_name','last_name']

class ProfileEditForm(forms.ModelForm):
	number = forms.IntegerField(required=True, label='Student Number')
	gprd = forms.BooleanField(required=True, initial=False,
							  label='Agree to share my information (name, email, number, username, grade) with the authors and other users of this application')
	class Meta:
		model = Profile
		fields = ['number','gprd']


class TeamMemberApprovalForm(forms.Form):
	member_id = forms.CharField(required=False)
	member_id_remove = forms.CharField(required=False)
	team_remove = forms.CharField(required=False)


class TeamJoinForm(forms.Form):
	team_id = forms.CharField(required=True)


class TeamModelForm(forms.ModelForm):
	name = forms.CharField(required=True, label='Team Name')

	class Meta:
		model = Team
		fields = ['name']


class TestForm(forms.Form):
	pass



class GroupCreateForm(forms.ModelForm):
	name = forms.CharField(required=True, label='Group Name')
	# TODO: Find a way to make these checkbox selects scrollable
	# contests = forms.ModelMultipleChoiceField(required=False, label='Contests', queryset=Contest.objects.all(), widget=forms.CheckboxSelectMultiple)

	class Meta:
		model = Group
		fields = ['name']


# CUSTOM FIELDS

class ContestsModelChoiceField(forms.ModelChoiceField):
	def label_from_instance(self, contest):
		return contest.short_name

class UsersModelChoiceField(forms.ModelChoiceField):
	def label_from_instance(self, user):
		return "" + user.first_name + " " + user.last_name