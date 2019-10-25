from django.urls import path, re_path

from .views import (
	contest_list_view,
	signup_view,
	contest_detail_view,
	atempt_create_view,
	team_create_view,
	team_join_view,
	team_detail_view,
	atempt_view,
	atempt_list_view,
	ranking_view,
	change_password_view,
	profile_view,
	notactive_view
)

urlpatterns = [
	path('',contest_list_view, name='home'),
        path('contests/<int:id>/', contest_detail_view),
        path('contests/<int:id>/atempt/', atempt_create_view),
        path('contests/<int:id>/team/', team_create_view),
        path('contests/<int:id>/team/join/', team_join_view),
        path('contests/<int:id>/myteam/', team_detail_view),
        path('contests/atempt/<int:id>/', atempt_view),
        path('contests/<int:id>/status/', atempt_list_view),
        path('contests/<int:id>/ranking/', ranking_view),
	path('signup/', signup_view, name='signup'),
	path('notactive/', notactive_view, name='not_active'),
	path('profile/password/', change_password_view, name='password'),
	path('profile/', profile_view, name='profile')
]
