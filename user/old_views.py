import sys

from coolname import generate_slug
from django.contrib import messages
from django.contrib.auth import logout  # last 2 imported
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.encoding import smart_text

from shared.forms import AttemptModelForm, TeamMemberApprovalForm, \
    ProfileEditForm, UserEditForm, TeamJoinForm, GroupJoinForm, TeamCreateForm
from shared.models import Contest, UserContestDateException
from contest.routines import *
from .context_functions import *


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

    template_name = 'views/contest_detail_home.html'

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
        template_name = 'contest/closed_error.html'
    else:
        template_name = 'contest/details.html'

    context = {"contest": obj}
    return render(request, template_name, context)


# profile
@login_required
def profile_view(request):
    template_name = 'profile.html'
    context = {'user': request.user, 'title': "My Information"}
    return render(request, template_name, context)


# ranking
@login_required
def ranking_view(request, id):
    if not request.user.profile.number:
        return redirect('complete_profile')
    if not request.user.profile.valid:
        return redirect('not_active')

    template_name = 'contest/rankings.html'

    contest_obj = get_object_or_404(Contest, id=id)
    context = {'contest': contest_obj}

    atempts = getAllContestAttemptsRanking(contest_obj)

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

    template_name = 'components/contests/form.html'
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

    template_name = 'components/contests/teams/team_join.html'
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

# TEAM DETAIL
@login_required
def team_detail_view(request, id):
    checkUserProfileInRequest(request)
    template_name = 'views/contests/teams/team.html'
    contest = getContestByID(id)
    context = getContestDetailLayoutContext(contest)
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

        if team_member_obj.approved:  # TODO: Is this duplicated check necessary?
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



