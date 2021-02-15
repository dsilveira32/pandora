from django import forms
from django.contrib.auth.models import User
from .models import Atempt, Team, Contest, Test, get_contest_code_path, TeamMember, Profile, Group


class DateInputWidget(forms.DateTimeInput):
	input_type = 'datetime-local'


class AttemptModelForm(forms.ModelForm):
	comment = forms.CharField(required=False)

	class Meta:
		model = Atempt
		fields = ['file', 'comment']


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


class TeamMemberForm(forms.Form):
	team_id = forms.CharField(required=True)


class TeamModelForm(forms.ModelForm):
	name = forms.CharField(required=True, label='Team Name')

	class Meta:
		model = Team
		fields = ['name']


class TestForm(forms.Form):
    pass


class DownloadForm(forms.Form):
	url = forms.CharField(max_length = 255, widget=forms.TextInput({
				'class':'form-control',
				'placeholder':'Enter URL to download...',
			}))

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
