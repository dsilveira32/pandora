from django.test import TestCase
from rest_framework.test import force_authenticate
from django.test.client import encode_multipart, RequestFactory

from rest_framework.test import force_authenticate, APITestCase, APIRequestFactory
from rest_framework.authtoken.models import Token

# Create your tests here.

from rest_framework.test import APITestCase, APIClient

from django.urls import reverse
from rest_framework import status
import requests
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


class TestListUsers(APITestCase):
	def setUp(self):
		self.factory = APIRequestFactory()
		# If the user must be a superuser use User.objects.create_superuser instead of create_user 
		self.user = User.objects.create_user(username='user', first_name='test', last_name='test', email='user@user.com', password='1234')
		self.admin = User.objects.create_user(username='admin', first_name='admin', last_name='admin', email='admin@admin.com', password='1234', is_superuser=True)
		self.staff = User.objects.create_user(username='staff', first_name='staff', last_name='staff', email='staff@staff.com', password='1234', is_staff=True)

		response = self.client.post(reverse("api_auth"), {'username' : self.user.username, 'password' : '1234'}, format="json")
		self.userToken = response.json()['token']
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		response = self.client.post(reverse("api_auth"), {'username' : self.admin.username, 'password' : '1234'}, format="json")
		self.adminToken = response.json()['token']
		self.assertEqual(response.status_code, status.HTTP_200_OK)

		response = self.client.post(reverse("api_auth"), {'username' : self.staff.username, 'password' : '1234'}, format="json")
		self.staffToken = response.json()['token']
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	def test_unauthenticated_can_not_list_users(self):
		response = self.client.get(reverse("user-list"))
		self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN) 

	def test_admin_can_list_users(self):
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.adminToken}")
		response = self.client.get(reverse("user-list"))
		self.assertEqual(response.status_code, status.HTTP_200_OK) 

	def test_staff_can_list_users(self):
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.staffToken}")
		response = self.client.get(reverse("user-list"))
		self.assertEqual(response.status_code, status.HTTP_200_OK)

	