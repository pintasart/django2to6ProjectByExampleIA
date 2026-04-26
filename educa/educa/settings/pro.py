'''
pro.py: Custom settings for the production environment

'''

from .base import *

#Setting DEBUG to False should be mandatory for any production environment
DEBUG = False


# When DEBUG is False and a view raises an exception, all informationwill be 
# sent by email to the people listed in the ADMINS setting. 
ADMINS = (
	('Antonio M', 'email@mydomain.com'),
)

# will only allow the hosts included in this list to serve the application
# ALLOWED_HOSTS = ['*']
ALLOWED_HOSTS = ['.educaproject.com']


DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql',
		'NAME': 'educa',
		'USER': 'educa',
		'PASSWORD': '*****',
	}
}