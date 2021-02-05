from django.urls import path

from .views import (
    contest_list_view,
    contest_detail_view,
    user_contest_detail_dashboard_view,
    contest_attempt_form_view,
    user_contest_team_join_view,
    team_create_view,
    team_join_view,
    team_detail_view,
    attempt_view,
    attempt_list_view,
    ranking_view,
    profile_view,
    nonactive_view,
    complete_profile_view,
    user_contest_home_view
)

urlpatterns = [
    # New urls / views

    path('contests/', user_contest_home_view, name='user_contests_home'),
    path('contests/<int:id>/', user_contest_detail_dashboard_view, name='user_contests_detail_dashboard'),
    path('contests/<int:id>/team/join/', user_contest_team_join_view, name='user_contest_team_join_view'),
    # TODO: Create general home view
    path('', user_contest_home_view, name='home'),


    # Old
    path('contests/<int:id>/attempt/', contest_attempt_form_view),
    path('contests/<int:id>/team/', team_create_view),

    path('contests/<int:id>/my_team/', team_detail_view),
    path('contests/<int:id>/attempt/<int:attempt_id>/', attempt_view),
    path('contests/<int:id>/status/', attempt_list_view),
    path('contests/<int:id>/ranking/', ranking_view),


    path('complete_profile/', complete_profile_view, name='complete_profile'),
    path('nonactive/', nonactive_view, name='not_active'),
    path('profile/', profile_view, name='profile')
]
