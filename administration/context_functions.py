#############################
#      CONTEXT FUNCTIONS    #
#############################

#############################
#          LAYOUTS          #
#############################

# CONTESTS #
from datetime import timedelta, datetime

from shared.models import Contest, Profile, Team


def getAdminContestNonDetailLayoutContext():
    return {}

def getAdminContestDetailLayoutContext(contest):
    context = {
        'admin_contest_detail_layout': {
            'contest': contest,
        }
    }
    context.update(getAdminContestNonDetailLayoutContext())
    return context

# TESTS #

def getAdminTestsNonDetailLayoutContext(contest):
    context = {
        'admin_test_non_detail_layout': {
            'contest': contest
        }
    }
    context.update(getAdminContestDetailLayoutContext(contest))
    return context

def getAdminTestDetailLayoutContext(contest, test):
    context = {
        'admin_test_detail_layout': {
            'test': test
        }
    }
    context.update(getAdminTestsNonDetailLayoutContext(contest))
    return context

# TEAMS #

def getAdminTeamNonDetailLayoutContext(contest):
    context = {
        'admin_team_non_detail_layout': {
            'contest': contest
        }
    }
    context.update(getAdminContestDetailLayoutContext(contest))
    return context

def getAdminTeamDetailLayoutContext(contest, team):
    context = {
        'admin_team_detail_layout': {
            'team': team
        }
    }
    context.update(getAdminTeamNonDetailLayoutContext(contest))
    return context

# SUBMISSIONS #

def getAdminSubmissionNonDetailLayoutContext(contest):
    context = {
        'admin_submission_non_detail_layout': {
            'contest': contest
        }
    }
    context.update(getAdminContestDetailLayoutContext(contest))
    return context

def getAdminSubmissionDetailLayoutContext(contest, submission):
    context = {
        'admin_submission_detail_layout': {
            'submission': submission
        }
    }
    context.update(getAdminSubmissionNonDetailLayoutContext(contest))
    return context

# GROUPS #

def getAdminGroupDetailLayoutContext(group):
    return {
        'admin_group_detail_layout': {
            'group': group
        }
    }

# USERS #

def getAdminUserDetailLayoutContext(user):
    return {
        'admin_user_detail_layout': {
            'user': user
        }
    }

#############################
#         COMPONENTS        #
#############################

# For list.html
def getAdminContestListContext(contests):
    """Context for list.html
    REQUIRED IN ALL VIEWS THAT EXTEND list.html
    Parameters
    ----------
        contests : list of Contest
    return
    ----------
        admin_contest_list
    """
    return {
        'admin_contest_list': {
            'contests': contests,
        }
    }



# For list.html
def getAdminTeamListContext(teams):
    """Context for list.html
    REQUIRED IN ALL VIEWS THAT EXTEND list.html
    Parameters
    ----------
        teams : array of Team
    return
    ----------
       team_list
    """
    return {
        'admin_team_list': {
            'teams': teams
        }
    }


# For detail.html
def getAdminContestsTeamsDetailContext(team):
    """Context for detail.html
    REQUIRED IN ALL VIEWS THAT EXTEND detail.html
    Parameters
    ----------
        team : Team
    return
    ----------
       team_list
    """
    return {
        'admin_contests_teams_detail': {
            'team': team,
        }
    }

# For form.html
def getAdminTestFormContext(contest, form):
    """Context for form.html
    REQUIRED IN ALL VIEWS THAT EXTEND form.html
    Parameters
    ----------
        contest : Contest
        form
    return
    ----------
        admin_test_form
    """
    return {
        'admin_test_form': {
            'contest': contest,
            'form': form
        }
    }

def getAdminTestListContext(tests):
    return {
        'admin_test_list': {
            'tests': tests
        }
    }



# For list.html
def getAdminGroupListContext(groups):
    """Context for list.html
       REQUIRED IN ALL VIEWS THAT INCLUDE list.html
       Parameters
       ----------
           group : list of Group
       """
    return {
        'admin_group_list': {
            'groups': groups
        }
    }

# For list.html
def getAdminGroupUserListContext(user_profiles):
    """Context for list.html
           REQUIRED IN ALL VIEWS THAT INCLUDE list.html
           Parameters
           ----------
               user_profiles : list of Profile
           """
    return {
        'admin_group_users_list': {
            'user_profiles': user_profiles
        }
    }

# For form.html
def getAdminCreateGroupFormContext(form):
    return {
        'admin_create_group_form': {
            'form': form
        }
    }


# For form.html
def getAdminCreateContestFormContext(form):
    return {
        'admin_contest_create_form': {
            'form': form
        }
    }


# For admin_test_specification_form.html
def getAdminSpecificationFormContext(form):
    return {
        'admin_test_specification_form': {
            'form': form
        }
    }

# For admin/users/list.html
def getAdminUsersListContext(users):
    return {
        'admin_users_list': {
            'users': users
        }
    }

# For admin/users/form.html
def getAdminUsersFormContext(userForm, profileForm):
    return {
        'admin_users_form': {
            'userForm': userForm,
            'profileForm': profileForm
        }
    }


# For admin/components/groups/contests_manager
def getAdminGroupsContestsManagerContext(contests, contests_in):
    return {
        'admin_group_contests_manager': {
            'contests': contests,
            'contests_in': contests_in
        }
    }


# For admin/components/groups/user_manager.html
def getAdminGroupUserManagerContext(users_not_in_group, users_in_group):
    return {
        'admin_groups_user_manager': {
            'users_not_in_group': users_not_in_group,
            'users_in_group': users_in_group
        }
    }

# For admin/components/groups/dashboard_cards.html
def getAdminGroupDashboardCardsContext(group, user_count, open_contest_count, closed_contest_count):
    return {
        'admin_groups_dashboard_cards': {
            'group': group,
            'user_count': user_count,
            'open_contest_count': open_contest_count,
            'closed_contest_count': closed_contest_count,
        }
    }

# For /contests/teams/form.html
def getAdminContestsTeamsFormContext(form):
    return {
        'admin_contests_teams_form': {
            'form': form
        }
    }

# For /contests/teams/manager.html
def getAdminContestsTeamsManagerContext(users_out, users_in, team):
    return {
        'admin_contests_teams_manager': {
            'users_out': users_out,
            'users_in': users_in,
            'team': team
        }
    }






# For admin/components/contests/dashboard_cards.html
def getAdminContestDashboardCardsContext(contest, submission_count, team_count, test_count, user_count):
    return {
        'admin_contests_dashboard_cards': {
            'contest': contest,
            'submission_count': submission_count,
            'team_count': team_count,
            'test_count': test_count,
            'user_count': user_count,
        }
    }


# For admin/components/contests/submissions/list.html
def getAdminContestSubmissionListContext(submissions):
    return {
        'admin_contests_submissions_list': {
            'submissions': submissions,
        }
    }

# For admin/components/contests/submissions/chart.html
def getAdminContestSubmissionChartContext(submissions, contest):
    return {
        'admin_contests_submissions_chart': {
            'submissions': list(submissions.values()),
            'contest': contest
        }
    }



# For admin/components/contests/submissions/details.html
def getAdminContestSubmissionDetailsContext(contest, user, team, attempt, n_passed, n_tests, mandatory_passed,
                                            n_mandatory, passed_diff, n_diff, results, min_passed_grade):
    return {
        'admin_contests_submissions_details': {
            'contest': contest,
            'user': user,
            'team': team,
            'team_members': team.getUsers(),
            'attempt': attempt,
            'maxsize': 2147483647,
            'n_passed': n_passed,
            'n_total': n_tests,
            'mandatory_passed': mandatory_passed,
            'mandatory_total': n_mandatory,
            'general_passed': passed_diff,
            'n_general': n_diff,
            'results': results,
            'min_grade': min_passed_grade
        }
    }

def getAdminTestsListEditFormContext(tests):
    return {
        'admin_list_edit_form': {
            'tests': tests
        }
    }


def getAdminTestDetailsContext(test):
    return {
        'admin_test_details': {
            'test': test
        }
    }


def getAdminTestMassCreateFormContext(form):
    return {
        'admin_test_mass_create_form': {
            'form': form
        }
    }

# For rankings.html
def getAdminContestRankingsContext(attempts):
    return {
        'admin_contest_rankings': {
            'attempts': attempts
        }
    }

def getAdminDashboardActiveContestsCardContext():
    return {
        'admin_dashboard_active_contests': {
            'number': Contest.getActiveContests().count()
        }
    }

def getAdminDashboardLastWeekSubmissionsCardContext():
    teams = Team.objects.all()
    oneWeek = datetime.today() - timedelta(days=7)
    subsSum = 0
    if teams:
        for team in teams:
            for s in team.getAttempts().filter(date__gt=oneWeek):
                subsSum += team.getAttempts().count()
    return {
        'admin_dashboard_last_week_submissions': {
            'number': subsSum
        }
    }

def getAdminDashboardActiveUsersCardContext():
    return {
        'admin_dashboard_active_users': {
            'number': Profile.getActiveUsers().count()
        }
    }

def getAdminDashboardGradesAvgContext():
    labels = []
    data = []
    contests = Contest.objects.all().order_by("end_date")[:5]
    for contest in contests:
        labels.append(contest.getName())
        gradeSum = 0
        for team in contest.getTeams():
            submissions = team.getAttempts()
            if submissions:
                for sub in submissions:
                    gradeSum += sub.getGrade()

        data.append(gradeSum / len(contests))

    return {
        'admin_dashboard_grades_avg': {
            'labels': labels,
            'data': data
        }
    }