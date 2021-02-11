from django.urls import path

from .views import (
    admin_choose_test,
    admin_contest_creation,
    admin_test_creation_old,
    admin_test_editor,
    admin_view_teams_status,
    extract_grades,
    extract_zip, admin_contest_detail_tests_view, admin_contest_detail_teams_view, admin_contest_detail_dashboard_view,
    admin_contest_home_view, admin_contest_detail_tests_create_view,
    admin_group_home_view, admin_group_detail_dashboard_view, admin_group_create_view,
    admin_contest_detail_test_detail_view, admin_contest_detail_team_edit_view, admin_contest_create_view,
    admin_contest_detail_specification_view,
    admin_contest_detail_test_detail_specification_view, admin_contest_detail_test_detail_edit_view
)

urlpatterns = [
    # New urls / views

    # CONTESTS

    path('contests/', admin_contest_home_view, name='manager_contests_home'),
    # TODO: make a create view and replace below
    path('contests/create/', admin_contest_create_view, name='manager_contests_create'),

    path('contests/<int:contest_id>/', admin_contest_detail_dashboard_view, name='manager_contests_detail_dashboard'),
    path('contests/<int:contest_id>/tests/', admin_contest_detail_tests_view, name='manager_contests_detail_tests'),
    path('contests/<int:contest_id>/tests/create', admin_contest_detail_tests_create_view, name='manager_contests_detail_tests_create'),
    path('contests/<int:contest_id>/tests/<int:test_id>', admin_contest_detail_test_detail_view, name='manager_contests_detail_tests_edit'),
    path('contests/<int:contest_id>/tests/<int:test_id>/specification',
         admin_contest_detail_test_detail_specification_view, name='manager_contest_detail_test_detail_specification'),
    path('contests/<int:contest_id>/tests/<int:test_id>/edit',
         admin_contest_detail_test_detail_edit_view, name='manager_contest_detail_test_detail_edit'),
    path('contests/<int:contest_id>/teams/', admin_contest_detail_teams_view, name='manager_contests_detail_teams'),
    path('contests/<int:contest_id>/teams/<int:team_id>', admin_contest_detail_team_edit_view, name='manager_contests_detail_team_edit'),
    path('contests/<int:contest_id>/specification', admin_contest_detail_specification_view, name="manager_contest_detail_specification"),
    # GROUPS
    path('groups/', admin_group_home_view, name="admin_groups_home"),
    path('groups/create', admin_group_create_view, name='admin_group_create'),
    path('groups/<int:id>/', admin_group_detail_dashboard_view, name='admin_group_detail_dashboard'),

    # Old

    path('contests/<int:id>/admin-view/test/chooser/', admin_choose_test),
    path('contests/<int:id>/admin-view/test/<int:t_id>/editor/', admin_test_editor),
    path('contests/<int:c_id>/admin-view/team/<int:t_id>/status/', admin_view_teams_status),
    path('admin-view/contest-creation/', admin_contest_creation),

]
