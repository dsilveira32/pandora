from django.urls import path

from .admin_views import (
    admin_choose_test,
    admin_contest_creation,
    admin_test_creation,
    admin_test_editor,
    admin_view_teams_status,
    extract_grades,
    extract_zip, admin_contest_detail_tests_view, admin_contest_detail_teams_view, admin_contest_detail_dashboard_view,
    admin_contest_home_view,

)
from .views import (
    contest_list_view,
    contest_detail_view,
    user_contest_detail_dashboard_view,
    contest_attempt_form_view,
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
    # ADMIN
    path('manager/contests/', admin_contest_home_view, name='manager_contests_home'),
    # TODO: make a create view and replace below
    path('manager/contests/create', admin_contest_home_view, name='manager_contests_create'),

    path('manager/contests/<int:id>/', admin_contest_detail_dashboard_view, name='manager_contests_detail_dashboard'),
    path('manager/contests/<int:id>/tests/', admin_contest_detail_tests_view, name='manager_contests_detail_tests'),
    path('manager/contests/<int:id>/tests/create', admin_contest_detail_tests_view, name='manager_contests_detail_tests'),
    path('manager/contests/<int:id>/teams/', admin_contest_detail_teams_view, name='manager_contests_detail_teams'),

    # USER
    path('contests/', user_contest_home_view, name='user_contests_home'),
    path('contests/<int:id>/', user_contest_detail_dashboard_view, name='user_contests_detail_dashboard'),

    # Old
    path('', user_contest_home_view, name='home'),
    path('contests/<int:id>/attempt/', contest_attempt_form_view),
    path('contests/<int:id>/team/', team_create_view),
    path('contests/<int:id>/team/join/', team_join_view),
    path('contests/<int:id>/my_team/', team_detail_view),
    path('contests/<int:id>/attempt/<int:attempt_id>/', attempt_view),
    path('contests/<int:id>/status/', attempt_list_view),
    path('contests/<int:id>/ranking/', ranking_view),
    path('contests/<int:id>/admin-view/test/chooser/', admin_choose_test),
    path('contests/<int:id>/admin-view/test/<int:t_id>/editor/', admin_test_editor),
    path('contests/<int:c_id>/admin-view/team/<int:t_id>/status/', admin_view_teams_status),

    path('contests/<int:id>/grades-downloader/', extract_grades),
    path('contests/<int:id>/zip-downloader/', extract_zip),
    path('admin-view/contest-creation/', admin_contest_creation),
    path('admin-view/test-creation/', admin_test_creation),

    path('complete_profile/', complete_profile_view, name='complete_profile'),
    path('nonactive/', nonactive_view, name='not_active'),
    path('profile/', profile_view, name='profile')
]
