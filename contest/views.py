import sys

from django.contrib import messages
from django.contrib.auth import logout  # last 2 imported
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.encoding import smart_text

from .forms import AttemptModelForm, TeamModelForm, TeamMemberForm, TeamMemberApprovalForm, \
    ProfileEditForm, UserEditForm
from .models import Contest, UserContestDateException
from .routines import *


# attempt
@login_required
def attempt_list_view(request, id):
    if not request.user.profile.number:
        return redirect('complete_profile')
    if not request.user.profile.valid:
        return redirect('not_active')

    template_name = 'components/teams/team_submission_list.html'

    contest_obj = get_object_or_404(Contest, id=id)
    context = {'contest': contest_obj}

    team_obj, members = get_user_team(request, contest_obj.id)
    if not team_obj:
        return redirect(os.path.join(contest_obj.get_absolute_url(), 'team/join/'))

    atempts = get_team_attempts(team_obj)

    if atempts:
        context.update({'number_of_submitions': atempts.count()})
        context.update({'last_classification': atempts.first().grade})
        context.update({'last_execution_time': atempts.first().time_benchmark})
        context.update({'last_memory_usage': atempts.first().memory_benchmark})
        if os.path.isfile(atempts.first().file.path):
            context.update({'download': atempts.first().file})
        else:
            context.update({'download': 0})
    else:
        context.update({'number_of_submitions': 0})
        context.update({'last_classification': 0})
        context.update({'last_execution_time': 0})
        context.update({'last_memory_usage': 0})
        context.update({'download': 0})

    team_obj.members = members
    context.update({'team': team_obj})
    context.update({'atempts': atempts})
    context.update({'title': "Status"})

    return render(request, template_name, context)



# contest
@login_required
def contest_list_view(request):
    if not request.user.profile.number:
        return redirect('complete_profile')
    if not request.user.profile.valid:
        return redirect('not_active')

    template_name = 'pages/home.html'

    if request.user.is_superuser:
        contests_qs = Contest.objects.all()
    else:
        contests_qs = Contest.objects.filter(visible=True)

    qs = TeamMember.objects.select_related('team').filter(user=request.user)

    context = {'object_list': contests_qs,
               'team_contests': qs,
               'title': 'Contests',
               'description': 'PANDORA is an Automated Assement Tool.'}
    return render(request, template_name, context)


@login_required
def contest_detail_view(request, id):
    if not request.user.profile.number:
        return redirect('complete_profile')
    if not request.user.profile.valid:
        return redirect('not_active')

    obj = get_object_or_404(Contest, id=id)

    present = timezone.now()
    if present < obj.start_date:
        # contest is not yet open. Don't let anyone see a dam thing.
        template_name = 'contest/contest_closed_error.html'
    else:
        template_name = 'contest/contest_details.html'

    context = {"contest": obj}
    return render(request, template_name, context)


# profile
@login_required
def profile_view(request):
    template_name = 'contest/user_profile.html'
    context = {'user': request.user, 'title': "My Information"}
    return render(request, template_name, context)


# ranking
@login_required
def ranking_view(request, id):
    if not request.user.profile.number:
        return redirect('complete_profile')
    if not request.user.profile.valid:
        return redirect('not_active')

    template_name = 'contest/contest_rankings.html'

    contest_obj = get_object_or_404(Contest, id=id)
    context = {'contest': contest_obj}

    # TODO Make it better
    query = "SELECT ca.*, maxs.atempts, maxs.team_id FROM (" \
            "select max(id) as id," \
            "count(id) as atempts," \
            "team_id from " \
            "contest_atempt" \
            " where contest_id = " + str(contest_obj.id) + \
            "   group by team_id)" \
            "       maxs inner join contest_atempt ca on ca.id = maxs.id" \
            "           order by grade desc, atempts asc, time_benchmark asc, memory_benchmark asc, elapsed_time asc," \
            "                       cpu_time asc"
    # select contest_atempt.id as id, max(date), grade, count(contest_atempt.id) as number_of_atempts, time_benchmark, memory_benchmark elapsed_time, cpu_time from contest_atempt where contest_id = " + str(contest_obj.id) + " group by (team_id) order by grade desc, time_benchmark asc, memory_benchmark asc, number_of_atempts asc"

    atempts = Atempt.objects.raw(query)

    context.update({'atempts': atempts})
    context.update({'title': "Ranking"})
    return render(request, template_name, context)


# team
@login_required
def team_create_view(request, id):
    if not request.user.profile.number:
        return redirect('complete_profile')
    if not request.user.profile.valid:
        return redirect('not_active')

    template_name = 'contest/contest_form.html'
    contest_obj = get_object_or_404(Contest, id=id)
    context = {'contest': contest_obj}

    user_team = TeamMember.objects.select_related('team').filter(team__contest=contest_obj.id,
                                                                 user=request.user).first()

    if user_team:
        # this user already has a team
        return redirect(os.path.join(contest_obj.get_absolute_url(), 'my_team/'))

    # in case individual submition - Create a team with the username with only one member
    if contest_obj.max_team_members == 1:
        t = Team(name=request.user.username, contest=contest_obj)
        t.save()
        tm = TeamMember(team=t, user=request.user, approved=True)
        tm.save()
        return redirect(os.path.join(contest_obj.get_absolute_url(), 'my_team/'))

    form = TeamModelForm(request.POST or None)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.contest = contest_obj
        obj.save()
        team_member_obj = TeamMember()
        team_member_obj.user = request.user
        team_member_obj.approved = True
        team_member_obj.team = obj
        team_member_obj.save()
        return redirect(os.path.join(contest_obj.get_absolute_url(), 'my_team/'))

    context.update({'form': form})
    context.update({"title": 'Create New Team'})
    return render(request, template_name, context)

@login_required
def team_join_view(request, id):
    if not request.user.profile.number:
        return redirect('complete_profile')
    if not request.user.profile.valid:
        return redirect('not_active')

    template_name = 'contest/team_join.html'
    contest_obj = get_object_or_404(Contest, id=id)
    context = {'contest': contest_obj}

    user_team, members = get_user_team(request, contest_obj.id)
    user_team.members = members
    # TeamMember.objects.select_related('team').filter(team__contest = contest_obj.id, user = request.user).first()

    if user_team:
        return redirect(os.path.join(contest_obj.get_absolute_url(), 'my_team/'))

    # in case individual submition - Create a team with the username with only one member
    if contest_obj.max_team_members == 1:
        t = Team(name=request.user.username, contest=contest_obj)
        t.save()
        tm = TeamMember(team=t, user=request.user, approved=True)
        tm.save()
        return redirect(os.path.join(contest_obj.get_absolute_url(), 'my_team/'))

    # get all teams active in this contenst
    teams = Team.objects.filter(contest__id=id)  # get all teams associated with this contest

    # set the members details and the amount of new member that can join
    for obj in teams:
        obj.members = TeamMember.objects.filter(team=obj)
        obj.room_left = obj.contest.max_team_members - obj.members.count()

    # update the contenxt to send to the team_join.html
    context.update({'teams': teams})

    # no idea what it does
    form = TeamMemberForm(request.POST or None)

    if form.is_valid():
        team_id = form.cleaned_data.get("team_id")
        team_member = TeamMember()

        team = Team.objects.get(id=team_id)

        qs = team.teammember_set.all()
        if qs.count() > team.contest.max_team_members:
            messages.error(request, "Error! This team can not accept new members")
        else:
            team_member.team = team
            team_member.user = request.user
            team_member.approved = False
            team_member.save()
            return redirect(os.path.join(contest_obj.get_absolute_url(), 'my_team/'))
        form = TeamMemberForm()

    # context.update({'form': form})
    return render(request, template_name, context)


# ------------------------------------------------------ The rest ------------------------------------------------------
# page logout
def pagelogout(request):
    if request.method == "POST":
        logout(request)
        return redirect('home')


# non active view
def nonactive_view(request):
    template_name = 'contest/error_message_dialog_box.html'
    context = {'title': 'Not active',
               'description': 'Your account is not active. Please wait for the administrator to activate your account.'}
    return render(request, template_name, context)


@login_required
def complete_profile_view(request):
    profile_form = ProfileEditForm(request.POST or None, instance=request.user.profile)
    user_form = UserEditForm(request.POST or None, instance=request.user)

    if all((profile_form.is_valid(), user_form.is_valid())):
        profile_form.save()
        user_form.save()
        return redirect('home')
    else:
        user_form = UserEditForm(request.POST or None, instance=request.user)
        profile_form = ProfileEditForm(request.POST or None, instance=request.user.profile)

    context = {'form': user_form,
               'form2': profile_form,
               'title': 'Complete Information'}
    return render(request, 'form.html', context)


@login_required
def home_view_old(request):
    template_name = 'contest/dashboard.html'
    context = {'title': "Dashboard"}
    return render(request, template_name, context)


#############################
#         NEW VIEWS         #
#############################
# ATTEMPT PROCESS
@login_required
def attempt_view(request, id, attempt_id):
    print("Contest ID: %i | Attempt ID: %i" % (id, attempt_id))
    checkUserProfileInRequest(request)
    template_name = 'pages/contest_attempt_submission.html'
    atempt_obj = get_object_or_404(Atempt, id=attempt_id)
    contest = atempt_obj.contest
    context = getContestDetailLayoutContext(request, contest)
    team = atempt_obj.team

    # check if request.user is a member of atempt team OR admin
    if not team.teammember_set.filter(user=request.user, approved=True) and not request.user.is_superuser:
        raise Http404

    results = atempt_obj.classification_set.all()
    n_tests = contest.test_set.count()
    n_mandatory = contest.test_set.filter(mandatory=True).count()
    n_general = n_tests - n_mandatory
    n_passed = atempt_obj.classification_set.filter(passed=True).count()
    mandatory_passed = atempt_obj.classification_set.filter(passed=True, test__mandatory=True).count()
    general_passed = atempt_obj.classification_set.filter(passed=True, test__mandatory=False).count()

    #	print('number of results ' + str(results.count()))
    #	print('number of tests ' + str(n_tests))
    #	print('number of mandatory tests ' + str(n_mandatory))
    #	print('number of general tests ' + str(n_general))
    #	print('number of general passed tests ' + str(general_passed))
    #	print('number of mandatory passed tests ' + str(mandatory_passed))

    for res in results:
        res.expected_output = smart_text(res.test.output_file.read(), encoding='utf-8', strings_only=False,
                                         errors='strict')
        if res.output and os.path.isfile(res.output.path):
            res.obtained_output = smart_text(res.output.read(), encoding='utf-8', strings_only=False, errors='strict')
        else:
            res.obtained_output = ''

        res.input = smart_text(res.test.input_file.read(), encoding='utf-8', strings_only=False,
                               errors='strict')
    # res.diff = ' '.join(map(str, res.diff))
    context.update({'team': team})
    context.update({'team_members': team.teammember_set.all()})
    context.update({'atempt': atempt_obj})
    context.update({'maxsize': 2147483647})
    context.update({'n_passed': n_passed})
    context.update({'n_total': n_tests})
    context.update({'mandatory_passed': mandatory_passed})
    context.update({'mandatory_total': n_mandatory})
    context.update({'general_passed': general_passed})
    context.update({'n_general': n_general})
    context.update({'results': results})
    context.update({'title': "Atempt Detail"})
    return render(request, template_name, context)



#TEAM DETAIL
@login_required
def team_detail_view(request, id):
    checkUserProfileInRequest(request)
    template_name = 'pages/team.html'
    contest = get_object_or_404(Contest, id=id)
    context = getContestDetailLayoutContext(request, contest)
    # qs = TeamMember.objects.select_related('team').filter(team__contest = contest_obj.id, user = request.user).first()
    team = getUserTeamFromContest(request, contest)
    if not team:
        return redirect(os.path.join(contest.get_absolute_url(), 'team/join/'))

    team_member_obj = TeamMember.objects.get(team=team, user=request.user)

    can_be_deleted = True
    if team.members.count() > 1 or not team_member_obj.approved or get_team_attempts(team):
        can_be_deleted = False

    form = TeamMemberApprovalForm(request.POST or None)
    if form.is_valid():
        if "team_delete" in request.POST and can_be_deleted:
            team_member_obj.delete()
            team.delete()
            return redirect(os.path.join(contest.get_absolute_url(), 'team/join/'))

        if team_member_obj.approved: #TODO: Is this duplicated check necessary?
            if "member_id" in request.POST:
                team_member_obj2 = TeamMember.objects.get(id=form.cleaned_data.get("member_id"))
                team_member_obj2.approved = True
                team_member_obj2.save()

        if team.members.count() > 1 and "member_id_remove" in request.POST:
            team_member_obj2 = TeamMember.objects.get(id=form.cleaned_data.get("member_id_remove"))
            if (team_member_obj2 == team_member_obj and not team_member_obj2.approved) or team_member_obj.approved:
                team_member_obj2.delete()
                return redirect(os.path.join(contest.get_absolute_url(), 'team/join/'))

        form = TeamMemberApprovalForm()
        team.members = team.teammember_set.all()

    team.members = team.teammember_set.all()

    context.update({'team': team})
    context.update({'can_delete': can_be_deleted})  # it it only has one member, it can be deleted
    context.update({'can_approve': team_member_obj.approved})  # it it only has one member, it can be deleted
    context.update({'form': form})
    print_variables_debug([
        "Context: " + str(context),
    ])
    return render(request, template_name, context)

#SUMISSION VIEW
@login_required
def attempt_submission_view(request, id):
    checkUserProfileInRequest(request)
    template_name = 'pages/contest_attempt_submission.html'
    contest = get_object_or_404(Contest, id=id)
    context = getContestDetailLayoutContext(request, contest)

    can_submit = True

    start_date = contest.start_date
    end_date = contest.end_date

    # this is to allow specific users to submit outside the scheduled dates
    # example is a user that was sick
    #TODO: Make this without being an exception, and being part of the normal process
    #### EXCEPTIONS START ####
    try:
        user_excep = UserContestDateException.objects.get(user=request.user, contest=contest)
    except UserContestDateException.DoesNotExist:
        user_excep = None
    if user_excep:
        start_date = user_excep.start_date
        end_date = user_excep.end_date

    present = timezone.now()
    # present = datetime.datetime.now()
    if not request.user.is_superuser:
        if present < start_date or present > end_date:
            # contest is not opened
            return redirect(os.path.join(contest.get_absolute_url()))
    #### EXCEPTIONS END ####

    #Check team members
    team = getUserTeamFromContest(request, contest)
    if not team:
        if contest.max_team_members == 1:
            team = Team(name=request.user.username, contest=contest)
            team.save()
            tm = TeamMember(team=team, user=request.user, approved=True)
            tm.save()
            team.members = team.teammember_set.all()
        else:
            return redirect(os.path.join(contest.get_absolute_url(), 'team/join/'))

    #Check attempts
    atempts = get_team_attempts(team)
    if contest.max_submitions > 0:
        if atempts and atempts.count() >= contest.max_submitions:
            messages.error(request, "You have reached the maximum number of submissions for this contest.")
            can_submit = False

    #Check contest
    if not contest.is_open:
        messages.error(request, "This contest is not active.")
        can_submit = False

    # Check team
    if not team.active or not team.members.filter(user=request.user).first().approved or not request.user.profile.valid:
        messages.error(request,
                       "You need to be an Active member and approved member of an active team to make submitions")
        can_submit = False

    #Form OnSubmit()
    form = AttemptModelForm(request.POST or None, request.FILES or None)
    if can_submit and form.is_valid():
        obj = form.save(commit=False)
        obj.user = request.user
        obj.contest = contest
        obj.team = team
        obj.save()
        print_variables_debug([
            "Object: " + str(obj),
            "Object file: " + str(obj.file),
            "Object file path: " + str(obj.file.path),
            "Contest object: " + str(contest)
        ])
        handle_uploaded_file(obj, obj.file, contest)
        return redirect(obj.get_absolute_url())
    context.update(getTeamSubmissionHistoryContext(get_team_attempts(team)))
    context.update({'form': form, 'title': "Submit", "subpage":"Submission"})
    return render(request, template_name, context)


# HOME VIEW
@login_required
def home_view(request):
    checkUserProfileInRequest(request)
    template_name = 'pages/home.html'
    context = {'title': 'Contests',
               'description': 'PANDORA is an Automated Assessment Tool.',
               # TODO: FIND OUT WHAT THIS WAS FOR - PERG AO PROF 'team_contests': getTeamContests(request),
               }
    contests = getContests(request)
    context.update(getContestListContext(contests))

    return render(request, template_name, context)


# CONTEST VIEW
@login_required
def contest_view(request, id):
    checkUserProfileInRequest(request)
    template_name = 'pages/contest.html'

    # Get required data
    contest = getContestByID(id)
    has_access = checkIfUserHasAccessToContest(request, contest)
    team = getUserTeamFromContest(request, contest)
    team_attempts = get_team_attempts(team)
    ranked_attempts = getAllContestAttemptsRanking(contest)

    # Update context
    context = {
        'user_has_access': has_access
    }
    context.update(getContestDetailLayoutContext(request, contest))
    context.update(getTeamMembersContext(team))
    context.update(getTeamSubmissionHistoryContext(team_attempts))
    context.update(getContestDetailsContext(contest))
    context.update(getContestRankingsContext(ranked_attempts))
    context.update(getTeamSubmissionStatusContext(team_attempts))
    return render(request, template_name, context)


#############################
#      HELPER FUCTIONS      #
#############################



def checkIfUserIsSuperUser(request):
    return request.user.is_superuser


def getContestByID(id):
    return get_object_or_404(Contest, id=id)


def getContests(request):
    if checkIfUserIsSuperUser(request):
        return Contest.objects.all()
    else:
        return Contest.objects.filter(visible=True)


def getTeamContests(request):
    return TeamMember.objects.select_related('team').filter(user=request.user)


def checkUserProfileInRequest(request):
    if not request.user.profile.number:
        return redirect('complete_profile')
    if not request.user.profile.valid:
        return redirect('not_active')


def checkIfUserHasAccessToContest(request, contest):
    present = timezone.now()
    # TODO: When groups are implemented, check if contest belongs to groups user is a part of
    if not checkIfUserIsSuperUser(request) and present < contest.start_date:
        return False
    else:
        return True


def getUserTeamFromContest(request, contest):
    team, members = get_user_team(request, contest.id)
    team.members = members
    return team


def getAllContestAttemptsRanking(contest):
    # TODO Make it better
    query = "SELECT ca.*, maxs.atempts, maxs.team_id FROM (" \
            "select max(id) as id," \
            "count(id) as atempts," \
            "team_id from " \
            "contest_atempt" \
            " where contest_id = " + str(contest.id) + \
            "   group by team_id)" \
            "       maxs inner join contest_atempt ca on ca.id = maxs.id" \
            "           order by grade desc, atempts asc, time_benchmark asc, memory_benchmark asc, elapsed_time asc," \
            "                       cpu_time asc"
    # select contest_atempt.id as id, max(date), grade, count(contest_atempt.id) as number_of_atempts, time_benchmark, memory_benchmark elapsed_time, cpu_time from contest_atempt where contest_id = " + str(contest_obj.id) + " group by (team_id) order by grade desc, time_benchmark asc, memory_benchmark asc, number_of_atempts asc"

    return Atempt.objects.raw(query)


#############################
#      CONTEXT FUNCTIONS    #
#############################

# For contest_list.html
def getContestListContext(contests):
    return {
        'contest_list': {
            'contests': contests,
        }
    }


# For contest_details.html
def getContestDetailsContext(contest):
    return {
        'contest_details': {
            'contest': contest,
        }
    }


# For contest_detail_layout.html
# REQUIRED IN ALL VIEWS THAT EXTEND contest_detail_layout.html
def getContestDetailLayoutContext(request, contest):
    context = {
        'user_has_access': checkIfUserHasAccessToContest(request, contest),
        'contest_detail_layout': {
            'contest': contest
        }
    }
    context.update(getContestClosedErrorContext(contest))
    return context


# For contest_closed_error.html
# Probably not necessary since it is only used in Detail Layout but let's keep it here until we are sure
def getContestClosedErrorContext(contest):
    return {
        'contest_closed_error': {
            'contest': contest
        }
    }


# For team_members.html
def getTeamMembersContext(team):
    return {
        'team_members': {
            'team': team
        }
    }


# For team_submission_history.html
def getTeamSubmissionHistoryContext(attempts):
    return {
        'team_submission_history': {
            'attempts': attempts
        }
    }


# For team_submission_status.html
def getTeamSubmissionStatusContext(attempts):
    context = {}
    if attempts:
        context.update({'number_of_submitions': attempts.count()})
        context.update({'last_classification': attempts.first().grade})
        context.update({'last_execution_time': attempts.first().time_benchmark})
        context.update({'last_memory_usage': attempts.first().memory_benchmark})
        if os.path.isfile(attempts.first().file.path):
            context.update({'download': attempts.first().file})
        else:
            context.update({'download': 0})
    else:
        context.update({'number_of_submitions': 0})
        context.update({'last_classification': 0})
        context.update({'last_execution_time': 0})
        context.update({'last_memory_usage': 0})
        context.update({'download': 0})
    return {
        'team_submission_status': context
    }


# For contest_rankings.html
def getContestRankingsContext(attempts):
    return {
        'contest_rankings': {
            'attempts': attempts
        }
    }
