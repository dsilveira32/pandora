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
)

urlpatterns = [
    # New urls / views

    path('contests/', admin_contest_home_view, name='manager_contests_home'),
    # TODO: make a create view and replace below
    path('contests/create', admin_contest_home_view, name='manager_contests_create'),

    path('contests/<int:id>/', admin_contest_detail_dashboard_view, name='manager_contests_detail_dashboard'),
    path('contests/<int:id>/tests/', admin_contest_detail_tests_view, name='manager_contests_detail_tests'),
    path('contests/<int:id>/tests/create', admin_contest_detail_tests_create_view, name='manager_contests_detail_tests_create'),
    path('contests/<int:id>/teams/', admin_contest_detail_teams_view, name='manager_contests_detail_teams'),

    # Old

    path('contests/<int:id>/admin-view/test/chooser/', admin_choose_test),
    path('contests/<int:id>/admin-view/test/<int:t_id>/editor/', admin_test_editor),
    path('contests/<int:c_id>/admin-view/team/<int:t_id>/status/', admin_view_teams_status),
    path('admin-view/contest-creation/', admin_contest_creation),

]
