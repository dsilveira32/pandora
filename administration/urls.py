from django.urls import path

from .views import contest_views, group_views, user_views
from .views.contests import team_views, test_views


def users_views(args):
    pass


urlpatterns = [
    # New urls / views

    # CONTESTS
    path('contests/', contest_views.dashboard_view, name='manager_contests_home'),
    path('contests/create/', contest_views.create_view, name='manager_contests_create'),
    path('contests/<int:contest_id>/', contest_views.detail_dashboard_view,
         name='manager_contests_detail_dashboard'),
    path('contests/<int:contest_id>/specification', contest_views.detail_specification_view,
         name="manager_contest_detail_specification"),
    path('contests/<int:contest_id>/tests/', test_views.dashboard_view,
         name='manager_contests_detail_tests'),
    path('contests/<int:contest_id>/tests/create', test_views.create_view,
         name='manager_contests_detail_tests_create'),
    path('contests/<int:contest_id>/tests/<int:test_id>', test_views.detail_view,
         name='manager_contests_detail_tests_edit'),
    path('contests/<int:contest_id>/tests/<int:test_id>/specification',
         test_views.detail_specification_view, name='manager_contest_detail_test_detail_specification'),
    path('contests/<int:contest_id>/tests/<int:test_id>/edit',
         test_views.detail_edit_view, name='manager_contest_detail_test_detail_edit'),
    path('contests/<int:contest_id>/teams/', team_views.dashboard_view,
         name='manager_contests_detail_teams'),
    path('contests/<int:contest_id>/teams/<int:team_id>', team_views.detail_dashboard_view,
         name='manager_contests_detail_team_edit'),

    # GROUPS
    path('groups/', group_views.dashboard_view, name="admin_groups_home"),
    path('groups/create', group_views.create_view, name='admin_group_create'),
    path('groups/<int:group_id>/', group_views.detail_dashboard_view, name='admin_group_detail_dashboard'),

    # USERS
    path('users/', user_views.dashboard_view, name="admin_users_home"),
    path('users/<int:user_id>/', user_views.user_form_view, name="admin_users_user_form"),
    path('users/create/', user_views.user_form_create_view, name="admin_users_user_form_create"),

    # Old

    # path('contests/<int:id>/admin-view/test/chooser/', admin_choose_test),
    # path('contests/<int:id>/admin-view/test/<int:t_id>/editor/', admin_test_editor),
    # path('contests/<int:c_id>/admin-view/team/<int:t_id>/status/', admin_view_teams_status),
    # path('admin-view/contest-creation/', admin_contest_creation),

]
