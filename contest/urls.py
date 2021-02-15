from django.urls import path

from .admin_views import (
    admin_choose_test,
    admin_contest_creation,
    admin_test_creation,
    admin_test_editor,
    admin_view,
    admin_view_teams_status,
    extract_grades,
    extract_zip,

)
from .views import (
    contest_list_view,
    contest_detail_view,
    attempt_create_view,
    team_create_view,
    team_join_view,
    team_detail_view,
    attempt_view,
    attempt_list_view,
    ranking_view,
    profile_view,
    nonactive_view,
    complete_profile_view,
    home_view, group_list_view, group_join_view
)

urlpatterns = [
    path('', home_view, name='home'),
    path('contests/', contest_list_view, name='contest_list'),
    path('contests/<int:id>/', contest_detail_view),
    path('contests/<int:id>/attempt/', attempt_create_view),
    path('contests/<int:id>/team/', team_create_view),
    path('contests/<int:id>/team/join/', team_join_view),
    path('contests/<int:id>/my_team/', team_detail_view),
    path('contests/attempt/<int:id>/', attempt_view),
    path('contests/<int:id>/status/', attempt_list_view),
    path('contests/<int:id>/ranking/', ranking_view),
    path('contests/<int:id>/admin-view/', admin_view),
    path('contests/<int:id>/admin-view/test/chooser/', admin_choose_test),
    path('contests/<int:id>/admin-view/test/<int:t_id>/editor/', admin_test_editor),
    path('contests/<int:c_id>/admin-view/team/<int:t_id>/status/', admin_view_teams_status),

    path('contests/<int:id>/grades-downloader/', extract_grades),
    path('contests/<int:id>/zip-downloader/', extract_zip),

    path('groups/', group_list_view, name='group_list'),
    path('groups/join', group_join_view, name='group_join'),
    path('admin-view/contest-creation/', admin_contest_creation),
    path('admin-view/test-creation/', admin_test_creation),

    path('complete_profile/', complete_profile_view, name='complete_profile'),
    path('nonactive/', nonactive_view, name='not_active'),
    path('profile/', profile_view, name='profile')
]
