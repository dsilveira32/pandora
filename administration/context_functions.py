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
def getAdminTeamDetailContext(team):
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
        'admin_team_detail': {
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
def getAdminSpecificationFormContext(form):
    return {
        'admin_test_specification_form': {
            'form': form
        }
    }

# For admin_test_specification_form.html
def getAdminUsersListContext(users):
    return {
        'admin_users_list': {
            'users': users
        }
    }