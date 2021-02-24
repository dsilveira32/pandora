#############################
#      CONTEXT FUNCTIONS    #
#############################

# Create one of these for each component that requires data,
# then call this and update context with the function
# return in the view in order to use the component

# TODO:
#   The following components doesnt have context Getter:
#       contest_admin_menu - Doesnt need context
#       contest_chooser - Dont know what is it
#       contest_creation
#       error_message_dialog_box
#       team_detail
#       team_join
#       test_edition

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


# For detail_layout.html
# REQUIRED IN ALL VIEWS THAT EXTEND contest_detail_layout.html
def getAdminContestDetailLayoutContext(contest):
    """Context for contest_detail_layout.html
    REQUIRED IN ALL VIEWS THAT EXTEND detail_layout.html
    Parameters
    ----------
        contest : Contest
    return
    ----------
        admin_contest_detail_layout
    """
    context = {
        'admin_contest_detail_layout': {
            'contest': contest,
        }
    }
    return context

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

# For detail_layout.html
def getAdminGroupDetailLayoutContext(group):
    """Context for detail_layout.html
       REQUIRED IN ALL VIEWS THAT INCLUDE detail_layout.html
       Parameters
       ----------
           group : Group
       """
    return {
        'admin_group_detail_layout': {
            'group': group
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
def getAdminSpecificationFormContext(form, test):
    return {
        'admin_test_specification_form': {
            'test': test,
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

# For admin/users/form.html
def getAdminUserDetailLayoutContext(user):
    return {
        'admin_user_detail_layout': {
            'user': user
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
def getAdminContestSubmissionChartContext(submissions):
    return {
        'admin_contests_submissions_chart': {
            'submissions': list(submissions.values()),
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

def getAdminTestsNonDetailLayoutContext(contest):
    context = {}
    context.update(getAdminContestDetailLayoutContext(contest))
    return context