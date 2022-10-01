from django.urls import path

from . import api_views 

urlpatterns = [
    path('contests/', api_views.contest_list_create_view, name='contest-list'),
    path('contests/<int:pk>/update/', api_views.contest_update_view, name='contest-edit'),
    path('contests/<int:pk>/delete/', api_views.contest_destroy_view),
    path('contests/<int:pk>/', api_views.contest_detail_view, name='contest-detail'),
	#
	path('users/', api_views.profile_list_create_view, name='user-list-create'),
	path('users/<int:pk>/', api_views.user_detail_update_view, name='user-detail-update'),
	#
	path('groups/', api_views.group_list_view, name='group-list'),
	path('groups/<int:pk>/', api_views.group_detail_view, name='group-detail'),
	path('groups/<int:pk>/update/', api_views.group_update_view, name='group-update'),
	path('groups/create/', api_views.group_create_view, name='group-create'),
	path('groups/delete/', api_views.group_destroy_view, name='group-destroy'),
	#
	path('teams/', api_views.team_list_view, name='team-list'),
	path('teams/<int:pk>/', api_views.team_detail_view, name='team-detail'),
]