from shared.routines import *


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

# For admin_contest_list.html
def getAdminContestListContext(contests):
    """Context for admin_contest_list.html
    REQUIRED IN ALL VIEWS THAT EXTEND admin_contest_list.html
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
def getContestListContext(contests):
    """Context for list.html
    REQUIRED IN ALL VIEWS THAT EXTEND list.html
    Parameters
    ----------
        contests : list of Contest
    return
    ----------
        contest_list
    """
    return {
        'contest_list': {
            'contests': contests,
        }
    }


# For details.html
def getContestDetailsContext(contest):
    """Context for details.html
    REQUIRED IN ALL VIEWS THAT EXTEND details.html
    Parameters
    ----------
        contest : Contest
    return
    ----------
        contest_details
    """
    return {
        'contest_details': {
            'contest': contest,
        }
    }


# For contest_detail_layout.html
# REQUIRED IN ALL VIEWS THAT EXTEND contest_detail_layout.html
def getContestDetailLayoutContext(contest):
    """Context for contest_detail_layout.html
    REQUIRED IN ALL VIEWS THAT EXTEND contest_detail_layout.html
    Parameters
    ----------
        contest : Contest

    return
    ----------
        contest_detail_layout
    """
    context = {
        'contest_detail_layout': {
            'contest': contest
        }
    }
    return context


# For admin_contest_detail_layout.html
# REQUIRED IN ALL VIEWS THAT EXTEND contest_detail_layout.html
def getAdminContestDetailLayoutContext(contest):
    """Context for contest_detail_layout.html
    REQUIRED IN ALL VIEWS THAT EXTEND admin_contest_detail_layout.html
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


# For closed_error.html
# Probably not necessary since it is only used in Detail Layout but let's keep it here until we are sure
def getContestClosedErrorContext(contest):
    """Context for closed_error.html
    REQUIRED IN ALL VIEWS THAT EXTEND closed_error.html
    Parameters
    ----------
        contest : Contest
    return
    ----------
        contest_closed_error
    """
    return {
        'contest_closed_error': {
            'contest': contest
        }
    }


# For members.html
def getTeamMembersContext(team):
    """Context for members.html
    REQUIRED IN ALL VIEWS THAT EXTEND members.html
    Parameters
    ----------
        team : Team
    return
    ----------
        team_members
    """
    return {
        'team_members': {
            'team': team
        }
    }


# For history.html
def getTeamSubmissionHistoryContext(attempts):
    """Context for history.html
    REQUIRED IN ALL VIEWS THAT EXTEND history.html
    Parameters
    ----------
        attempts : list of Attempt
    return
    ----------
        team_submission_history
    """
    return {
        'team_submission_history': {
            'attempts': attempts
        }
    }


# For status.html
def getTeamSubmissionStatusContext(attempts):
    """Context for status.html
    REQUIRED IN ALL VIEWS THAT EXTEND status.html
    Parameters
    ----------
        attempts : list of Attempt
    return
    ----------
       team_submission_status
    """
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


# For rankings.html
def getContestRankingsContext(attempts):
    """Context for rankings.html
    REQUIRED IN ALL VIEWS THAT EXTEND rankings.html
    Parameters
    ----------
        attempts : array of Attempt
    return
    ----------
       contest_rankings
    """
    return {
        'contest_rankings': {
            'attempts': attempts
        }
    }


# For rankings.html
def getContestSingleRankingContext(attempt, rank):
    """Context for single_ranking.html
    REQUIRED IN ALL VIEWS THAT EXTEND single_ranking.html
    Parameters
    ----------
        attempt : Attempt
        rank: int
    return
    ----------
       contest_rankings
    """
    return {
        'single_ranking': {
            'attempt': attempt,
            'rank': rank
        }
    }


# For test_chooser.html
def getTestChooserContext(tests):
    """Context for test_chooser.html
    REQUIRED IN ALL VIEWS THAT EXTEND test_chooser.html
    Parameters
    ----------
        tests : array of Test
    return
    ----------
       test_chooser
    """
    return {
        'test_chooser': {
            'tests': tests
        }
    }


# For team_list.html
def getTeamListContext(teams):
    """Context for team_list.html
    REQUIRED IN ALL VIEWS THAT EXTEND team_list.html
    Parameters
    ----------
        teams : array of Team
    return
    ----------
       team_list
    """
    return {
        'team_list': {
            'teams': teams
        }
    }


# For form.html
# REQUIRED IN ALL VIEWS THAT EXTEND submission.html
def getContestFormContext(contest, form):
    """Context for form.html
    REQUIRED IN ALL VIEWS THAT EXTEND form.html
    Parameters
    ----------
        request
        contest : Contest
        form
    return
    ----------
        contest_form
    """
    context = {
        'contest_form': {
            'contest': contest,
            'form': form
        }
    }
    return context


# For constest_detail_tests.html
# REQUIRED IN ALL VIEWS THAT EXTEND constest_detail_tests.html
def getContestDetailTestsContext(contest, form):
    """Context for constest_detail_tests.html
    REQUIRED IN ALL VIEWS THAT EXTEND constest_detail_tests.html
    Parameters
    ----------
        contest : Contest
        form
    return
    ----------
        user_has_access
        constest_detail_tests
    """
    context = {
        'constest_detail_tests': {
            'contest': contest,
            'form': form
        }
    }
    return context


# For test_creation.html
# REQUIRED IN ALL VIEWS THAT EXTEND test_creation.html
def getTestCreationContext(contest, form):
    """Context for test_creation.html
    REQUIRED IN ALL VIEWS THAT EXTEND test_creation.html
    Parameters
    ----------
        contest : Contest
        form
    return
    ----------
        test_creation
    """
    return {
        'test_creation': {
            'contest': contest,
            'form': form
        }
    }


# REQUIRED IN ALL VIEWS THAT EXTEND submit_button.html
def getContestSubmitAttemptButton(contest, team):
    """Context for test_creation.html
    REQUIRED IN ALL VIEWS THAT EXTEND submit_button.html
    Parameters
    ----------
        contest : Contest
        team: Team
    return
    ----------
        contest_submit_attempt_button
    """
    return {
        'contest_submit_attempt_button': {
            'team': team,
            'contest': contest
        }
    }


# REQUIRED IN ALL VIEWS THAT EXTEND contest_team_join.html
def getContestTeamJoinContext(contest, teams, form):
    """Context for contest_team_join.html
    REQUIRED IN ALL VIEWS THAT EXTEND contest_team_join.html
    Parameters
    ----------
        contest : Contest
        teams: Teams
        form: TeamMemberForm
    return
    ----------
        contest_team_join
    """
    return {
        'contest_team_join': {
            'contest': contest,
            'form': form,
            'teams': teams
        }
    }

# For details.html
# REQUIRED IN ALL VIEWS THAT EXTEND submission.html
def getTeamSubmissionDetailsContext(contest, user, attempt, n_passed, n_tests, mandatory_passed, n_mandatory, passed_diff, n_diff, results, min_passed_grade):
    return {
        'team_submission_details': {
            'contest': contest,
            'user': user,
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
# REQUIRED IN ALL VIEWS THAT EXTEND list.html
def getUserGroupListContext(groups):
    """Context for list.html
    REQUIRED IN ALL VIEWS THAT EXTEND list.html
    Parameters
    ----------
        groups: list of Group
    return
    ----------
        context
    """
    return {
        'user_group_list': {
            'groups': groups
        }
    }

# REQUIRED IN ALL VIEWS THAT EXTEND user_group_detail_layout.html
def getUserGroupDetailLayout(group):
    """Context for user_group_detail_layout.html
    REQUIRED IN ALL VIEWS THAT EXTEND user_group_detail_layout.html
    Parameters
    ----------
        group: Group
    return
    ----------
        context
    """
    return {
        'user_group_detail_layout': {
            'group': group
        }
    }

# REQUIRED IN ALL VIEWS THAT EXTEND view_sow_button.html
def getContestViewSowButtonContext(contest):
    """Context for view_sow_button.html
    REQUIRED IN ALL VIEWS THAT EXTEND view_sow_button.html
    Parameters
    ----------
        contest: Contest
    return
    ----------
        context
    """
    return {
        'contest_view_sow_button': {
            'contest': contest
        }
    }


# REQUIRED IN ALL VIEWS THAT EXTEND join_form.html
def getUserGroupJoinFormContext(form):
        """Context for join_form.html
        REQUIRED IN ALL VIEWS THAT EXTEND join_form.html
        Parameters
        ----------
            form: GroupJoinForm
        return
        ----------
            context
        """
        return {
            'user_group_join_form': {
                'form': form
            }
        }


# REQUIRED IN ALL VIEWS THAT EXTEND join_form.html
def getTeamJoinFormContext(create_form,join_form):
        """Context for join_form.html
        REQUIRED IN ALL VIEWS THAT EXTEND join_form.html
        Parameters
        ----------
            create_form: TeamCreateForm
            join_form: TeamJoinForm
        return
        ----------
            context
        """
        return {
            'team_join_form': {
                'create_form': create_form,
                'join_form': join_form
            }
        }

# REQUIRED IN ALL VIEWS THAT EXTEND user_grades_dashboard.html
def getUserGradesDasboardContext(labels, datasets):
        """Context for user_grades_dashboard.html
        REQUIRED IN ALL VIEWS THAT EXTEND user_grades_dashboard.html
        Parameters
        ----------
            labels: List
            datasets: List
        return
        ----------
            context
        """
        return {
            'user_grades_dashboard': {
                'labels': labels,
                'datasets': datasets
            }
        }

# REQUIRED IN ALL VIEWS THAT EXTEND profile_form.html
def getUserProfileFormContext(userForm, profileForm):
        """Context for profile_form.html
        REQUIRED IN ALL VIEWS THAT EXTEND profile_form.html
        Parameters
        ----------
            userForm: ModelForm
            profileForm: ModelForm
        return
        ----------
            context
        """
        return {
            'user_profile_form': {
                'userForm': userForm,
                'profileForm': profileForm
            }
        }

# REQUIRED IN ALL VIEWS THAT EXTEND number_card.html
def getUserContestsNumberCardContext(activeContestsNumber):
        """Context for number_card.html
        REQUIRED IN ALL VIEWS THAT EXTEND number_card.html
        Parameters
        ----------
            activeContestsNumber: int
        return
        ----------
            context
        """
        return {
            'user_contests_number_card': {
                'active_contests': activeContestsNumber
            }
        }