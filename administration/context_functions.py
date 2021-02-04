from contest.routines import *


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


# For contest_list.html
def getContestListContext(contests):
    """Context for contest_list.html
    REQUIRED IN ALL VIEWS THAT EXTEND contest_list.html
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


# For contest_details.html
def getContestDetailsContext(contest):
    """Context for contest_details.html
    REQUIRED IN ALL VIEWS THAT EXTEND contest_details.html
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
def getContestDetailLayoutContext(request, contest):
    """Context for contest_detail_layout.html
    REQUIRED IN ALL VIEWS THAT EXTEND contest_detail_layout.html
    Parameters
    ----------
        request
        contest : Contest
    return
    ----------
        contest_details
    """
    context = {
        'contest_detail_layout': {
            'contest': contest,
            'user_has_access': checkIfUserHasAccessToContest(request, contest),
        }
    }
    context.update(getContestClosedErrorContext(contest))
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


# For contest_closed_error.html
# Probably not necessary since it is only used in Detail Layout but let's keep it here until we are sure
def getContestClosedErrorContext(contest):
    """Context for contest_closed_error.html
    REQUIRED IN ALL VIEWS THAT EXTEND contest_closed_error.html
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


# For team_members.html
def getTeamMembersContext(team):
    """Context for team_members.html
    REQUIRED IN ALL VIEWS THAT EXTEND team_members.html
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


# For team_submission_history.html
def getTeamSubmissionHistoryContext(attempts):
    """Context for team_submission_history.html
    REQUIRED IN ALL VIEWS THAT EXTEND team_submission_history.html
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


# For team_submission_status.html
def getTeamSubmissionStatusContext(attempts):
    """Context for team_submission_status.html
    REQUIRED IN ALL VIEWS THAT EXTEND team_submission_status.html
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


# For contest_rankings.html
def getContestRankingsContext(attempts):
    """Context for contest_rankings.html
    REQUIRED IN ALL VIEWS THAT EXTEND contest_rankings.html
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


# For team_submission_details.html
# REQUIRED IN ALL VIEWS THAT EXTEND contest_attempt.html
def getTeamSubmissionDetailsContext(request, contest, attempt):
    """Context for team_submission_details.html
    REQUIRED IN ALL VIEWS THAT EXTEND team_submission_details.html
    Parameters
    ----------
        request
        contest : Contest
        attempt: Attempt
    return
    ----------
        user_has_access
        team_submission_details
    """
    context = {
        'user_has_access': checkIfUserHasAccessToContest(request, contest),
        'team_submission_details': {
            'attempt': attempt
        }
    }
    return context


# For contest_form.html
# REQUIRED IN ALL VIEWS THAT EXTEND contest_attempt.html
def getContestFormContext(contest, form):
    """Context for contest_form.html
    REQUIRED IN ALL VIEWS THAT EXTEND contest_form.html
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
