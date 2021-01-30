from .routines import *

#############################
#      CONTEXT FUNCTIONS    #
#############################

# Create one of these for each component that requires data,
# then call this and update context with the function
# return in the view in order to use the component

# For contest_list.html
def getContestListContext(contests):
    return {
        'contest_list': {
            'contests': contests,
        }
    }

# For admin_contest_list.html
def getAdminContestListContext(contests):
    return {
        'admin_contest_list': {
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
        'contest_detail_layout': {
            'contest': contest,
            'user_has_access': checkIfUserHasAccessToContest(request, contest),
        }
    }
    context.update(getContestClosedErrorContext(contest))
    return context


# For admin_contest_detail_layout.html
# REQUIRED IN ALL VIEWS THAT EXTEND contest_detail_layout.html
def getAdminContestDetailLayoutContext(request, contest):
    context = {
        'admin_contest_detail_layout': {
            'contest': contest,
        }
    }
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

# For test_chooser.html
def getTestChooserContext(tests):
	return {
		'test_chooser': {
			'tests': tests
		}
	}

# For team_list.html
def getTeamListContext(teams):
    return {
        'team_list': {
            'teams': teams
        }
    }

# For team_submission_details.html
# REQUIRED IN ALL VIEWS THAT EXTEND contest_attempt.html
def getTeamSubmissionDetailsContext(request, contest, attempt):
    context = {
        'user_has_access': checkIfUserHasAccessToContest(request, contest),
        'team_submission_details': {
            'attempt': attempt
        }
    }
    return context


# For contest_form.html
# REQUIRED IN ALL VIEWS THAT EXTEND contest_attempt.html
def getContestFormContext(request, contest, form):
    context = {
        'user_has_access': checkIfUserHasAccessToContest(request, contest),
        'contest_form': {
            'contest': contest,
            'form': form
        }
    }
    return context

# For constest_detail_tests.html
# REQUIRED IN ALL VIEWS THAT EXTEND constest_detail_tests.html
def getContestDetailTestsContext(request, contest, form):
    context = {
        'constest_detail_tests': {
            'contest': contest,
            'form': form
        }
    }
    return context

# For test_creation.html
# REQUIRED IN ALL VIEWS THAT EXTEND test_creation.html
def getTestCreationContext(request, contest, form):
    return {
        'test_creation': {
            'contest': contest,
            'form': form
        }
    }