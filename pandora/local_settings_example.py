import os

# you need to change this!
# go to your github account and create a new application. Copy and paste your key and secret here
SOCIAL_AUTH_GITHUB_KEY = '123456fakekey1234567'
SOCIAL_AUTH_GITHUB_SECRET = '123456fake123github456secret789123456789'

# user and password of the database
# not needed if you will use sqlite
DB_USER = 'django'
DB_PASSWORD = 'fakepassword'

# SECURITY WARNING: keep the secret key used in production secret!
# django key. You can make one up.
SECRET_KEY = '123456super_fake_key_with_strange_chars_#@!(%*$)##'

# hosts allowed. For production you need to add the server hostname
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.sqlite3',
		'NAME': os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db.sqlite3'),
#		for deployment use mysql or other engine
#		'ENGINE': 'django.db.backends.mysql',
#		'NAME': 'pandora',
#		'USER' : DB_USER,
#		'PASSWORD' : DB_PASSWORD,
#		'HOST' : 'localhost',
#		'PORT' : '3306'
	}
}
