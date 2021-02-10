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

# For admin_team_list.html
def getAdminTeamListContext(teams):
    """Context for admin_team_list.html
    REQUIRED IN ALL VIEWS THAT EXTEND admin_team_list.html
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


# For admin_team_detail.html
def getAdminTeamDetailContext(team):
    """Context for admin_team_detail.html
    REQUIRED IN ALL VIEWS THAT EXTEND admin_team_detail.html
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

# For admin_test_creation.html
# REQUIRED IN ALL VIEWS THAT EXTEND admin_test_creation.html
def getAdminTestCreationContext(contest, form):
    """Context for admin_test_creation.html
    REQUIRED IN ALL VIEWS THAT EXTEND admin_test_creation.html
    Parameters
    ----------
        contest : Contest
        form
    return
    ----------
        test_creation
    """
    return {
        'admin_test_creation': {
            'contest': contest,
            'form': form
        }
    }

# For admin_test_edition.html
# REQUIRED IN ALL VIEWS THAT EXTEND admin_test_creation.html
def getAdminTestEditionContext(test):
    """Context for admin_test_edition.html
    REQUIRED IN ALL VIEWS THAT EXTEND admin_test_edition.html
    Parameters
    ----------
        contest : Contest
        form
    return
    ----------
        test_creation
    """
    return {
        'admin_test_edition': {
            'test': test
        }
    }


def getAdminTestListContext(tests):
    return {
        'admin_test_list': {
            'tests': tests
        }
    }

# For admin_group_detail_layout.html
def getAdminGroupDetailLayoutContext(group):
    """Context for admin_group_detail_layout.html
       REQUIRED IN ALL VIEWS THAT INCLUDE admin_group_detail_layout.html
       Parameters
       ----------
           group : Group
       """
    return {
        'admin_group_detail_layout': {
            'group': group
        }
    }


# For admin_group_list.html
def getAdminGroupListContext(groups):
    """Context for admin_group_list.html
       REQUIRED IN ALL VIEWS THAT INCLUDE admin_group_list.html
       Parameters
       ----------
           group : list of Group
       """
    return {
        'admin_group_list': {
            'groups': groups
        }
    }

# For admin_group_users_list.html
def getAdminGroupUserListContext(user_profiles):
    """Context for admin_group_users_list.html
           REQUIRED IN ALL VIEWS THAT INCLUDE admin_group_users_list.html
           Parameters
           ----------
               user_profiles : list of Profile
           """
    return {
        'admin_group_users_list': {
            'user_profiles': user_profiles
        }
    }

# For admin_create_group_form.html
def getAdminCreateGroupFormContext(form):
    return {
        'admin_create_group_form': {
            'form': form
        }
    }



# For admin_contest_create_form.html
def getAdminCreateContestFormContext(form):
    return {
        'admin_contest_create_form': {
            'form': form
        }
    }