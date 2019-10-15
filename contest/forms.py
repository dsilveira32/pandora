from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from .models import Atempt, Team, TeamMember, Profile

class SignUpForm(UserCreationForm):
	first_name = forms.CharField(required=True, label='First Name', max_length=30)
	last_name = forms.CharField(required=True, label='Last Name', max_length=150)
	number = forms.IntegerField(required=True, label='Student Number')	
	gprd = forms.BooleanField(required=True, initial=False, label='Agree to share my information (name, email, number, username, grade) with the authors and other users of this application')

	class Meta:
		model = User
		fields = ('email', 'username', 'password1', 'password2')


class AtemptModelForm(forms.ModelForm):
	comment = forms.CharField(required=False)

	class Meta:
		model = Atempt
		fields = ['file', 'comment']


class TeamModelForm(forms.ModelForm):
	name = forms.CharField(required=True, label='Team Name')
	class Meta:
		model = Team
		fields = ['name']


class TeamMemberForm(forms.Form):
	team_id = forms.CharField(required=True)


class TeamMemberApprovalForm(forms.Form):
	member_id = forms.CharField(required=False)
	member_id_remove = forms.CharField(required=False)
	team_remove = forms.CharField(required=False)

