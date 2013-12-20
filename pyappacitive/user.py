__author__ = 'sathley'

from object import AppacitiveObject
from entity import Entity, object_system_properties
from error import ValidationError, UserAuthError
from utilities import http, urlfactory, customjson
from utilities.appcontext import ApplicationContext
from response import Response


def user_auth_required(func):

        def inner(*args, **kwargs):

            if ApplicationContext.get_user_token() is None:
                raise UserAuthError('No logged in user found. Call authenticate first.')
            return func(*args, **kwargs)

        return inner


class AppacitiveUser(Entity):

    def __init__(self, user=None):
        super(AppacitiveUser, self).__init__(user)
        self.type = 'user'
        self.type_id = 0

        if user is not None:
            self.type = user.get('__type', None)
            self.type_id = int(user.get('__typeid', 0))

    user_auth_header_key = 'Appacitive-User-Auth'

    def __set_self(self, user):
        super(AppacitiveUser, self)._set_self(user)
        self.type = user.get('__type', None)
        self.type_id = int(user.get('__typeid', 0))

    def get_dict(self):

        native = {}
        if self.type is not None:
            native['__type'] = self.type

        if self.type_id is not None:
            native['__typeid'] = str(self.type_id)

        if self.id is not None:
            native['__id'] = str(self.id)

        if self.revision is not 0:
            native['__revision'] = str(self.revision)

        if self.created_by is not None:
            native['__createdby'] = self.created_by

        if self.last_modified_by is not None:
            native['__lastmodifiedby'] = self.last_modified_by

        if self.utc_date_created is not None:
            native['__utcdatecreated'] = self.utc_date_created

        if self.utc_last_updated_date is not None:
            native['__utclastupdateddate'] = self.utc_last_updated_date

        tags = self.get_all_tags()
        if tags is not None:
            native['__tags'] = tags

        attributes = self.get_all_attributes()
        if attributes is not None:
            native['__attributes'] = attributes

        native.update(self.get_all_properties())
        return native

    @property
    def username(self):
        return self.get_property('username')

    @username.setter
    def username(self, value):
        self.set_property('username', value)

    @property
    def location(self):
        return self.get_property('location')

    @location.setter
    def location(self, value):
        self.set_property('location', value)

    @property
    def email(self):
        return self.get_property('email')

    @email.setter
    def email(self, value):
        self.set_property('email', value)

    @property
    def firstname(self):
        return self.get_property('firstname')

    @firstname.setter
    def firstname(self, value):
        self.set_property('firstname', value)

    @property
    def lastname(self):
        return self.get_property('lastname')

    @lastname.setter
    def lastname(self, value):
        self.set_property('lastname', value)

    @property
    def birthdate(self):
        return self.get_property('birthdate')

    @birthdate.setter
    def birthdate(self, value):
        self.set_property('birthdate', value)

    @property
    def isemailverified(self):
        return self.get_property('isemailverified')

    @isemailverified.setter
    def isemailverified(self, value):
        self.set_property('isemailverified', value)

    @property
    def isenabled(self):
        return self.get_property('isenabled')

    @isenabled.setter
    def isenabled(self, value):
        self.set_property('isenabled', value)

    @property
    def isonline(self):
        return self.get_property('isonline')

    @isonline.setter
    def isonline(self, value):
        self.set_property('isonline', value)

    @property
    def connectionid(self):
        return self.get_property('connectionid')

    @connectionid.setter
    def connectionid(self, value):
        self.set_property('connectionid', value)

    @property
    def secretquestion(self):
        return self.get_property('secretquestion')

    @secretquestion.setter
    def secretquestion(self, value):
        self.set_property('secretquestion', value)

    @property
    def secretanswer(self):
        return self.get_property('secretanswer')

    @secretanswer.setter
    def secretanswer(self, value):
        self.set_property('secretanswer', value)

    @property
    def password(self):
        return self.get_property('password')

    @password.setter
    def password(self, value):
        self.set_property('password', value)

    @property
    def phone(self):
        return self.get_property('phone')

    @phone.setter
    def phone(self, value):
        self.set_property('phone', value)

    def create(self):
        mandatory_fields = ['username', 'email', 'firstname', 'password']
        for field in mandatory_fields:
            if self.__getattribute__(field) is None:
                raise ValidationError('{0} is a mandatory field.'.format(field))

        url = urlfactory.user_urls["create"]()
        headers = urlfactory.get_user_headers()

        api_resp = http.put(url, headers, customjson.serialize(self.get_dict()))

        response = Response(api_resp['status'])

        if response.status_code == '200':
            self.__set_self(api_resp['user'])
        return response

    @classmethod
    @user_auth_required
    def get_by_id(cls, user_id):

        if user_id is None:
            raise ValidationError('User id is missing.')

        url = urlfactory.user_urls["get"]('user', user_id)

        headers = urlfactory.get_user_headers()

        api_response = http.get(url, headers)

        response = Response(api_response['status'])

        if response.status_code == '200':
            response.user = cls(api_response['user'])

        return response

    @classmethod
    @user_auth_required
    def get_by_username(cls, username):

        if username is None:
            raise ValidationError('Username is missing.')

        url = urlfactory.user_urls["get"]('user', username, 'username')
        headers = urlfactory.get_user_headers()

        api_response = http.get(url, headers)

        response = Response(api_response['status'])

        if response.status_code == '200':
            response.user = cls(api_response['user'])

        return response

    @classmethod
    @user_auth_required
    def get_logged_in_user(cls):

        if ApplicationContext.get_logged_in_user() is not None:
            return ApplicationContext.get_logged_in_user()

        if ApplicationContext.get_user_token() is None:
            raise UserAuthError('No logged in user found.')

        url = urlfactory.user_urls["get"]('user', 'me', 'token')

        headers = urlfactory.get_user_headers()

        api_response = http.get(url, headers)

        response = Response(api_response['status'])

        if response.status_code == '200':
            response.user = cls(api_response['user'])

        return response

    @staticmethod
    def authenticate(cls, username, password, expiry=None, attempts=None):

        url = urlfactory.user_urls['authenticate']()
        headers = urlfactory.get_headers()
        payload = {
            'username': username,
            'password': password
        }
        if expiry is not None:
            payload['expiry'] = expiry
        if attempts is not None:
            payload['attempts'] = attempts

        api_response = http.post(url, headers, customjson.serialize(payload))

        response = Response(api_response['status'])
        if response.status_code == '200':
            response.token = api_response['token']
            ApplicationContext.set_user_token(response.token)
            response.user = cls(api_response['user'])
            ApplicationContext.set_logged_in_user(response.user)
        return response

    @classmethod
    def multi_get(cls, user_ids):

        if user_ids is None:
            raise ValidationError('User ids are missing.')

        url = urlfactory.user_urls["multiget"](user_ids)
        headers = urlfactory.get_headers()
        api_response = http.get(url, headers)

        response = Response(api_response['status'])
        if response.status_code == '200':

            api_users = api_response.get('users', None)

            return_users = []
            for user in api_users:
                appacitive_user = cls(user)
                return_users.append(appacitive_user)
            response.users = return_users
            return response

    @classmethod
    @user_auth_required
    def delete_by_id(cls, user_id, delete_connections=False):

        if user_id is None:
            raise ValidationError('User id is missing.')

        url = urlfactory.user_urls["delete"]('user', user_id, delete_connections)

        headers = urlfactory.get_user_headers()

        api_resp = http.delete(url, headers)
        response = Response(api_resp['status'])
        return response

    @classmethod
    @user_auth_required
    def delete_by_username(cls, username, delete_connections=False):

        if username is None:
            raise ValidationError('Username is missing.')

        url = urlfactory.user_urls["delete"]('user', username, 'username', delete_connections)

        headers = urlfactory.get_user_headers()

        api_resp = http.delete(url, headers)
        response = Response(api_resp['status'])
        return response

    @classmethod
    @user_auth_required
    def delete_logged_in_user(cls, delete_connections=False):

        url = urlfactory.user_urls["delete"]('user', 'me', 'token', delete_connections)

        headers = urlfactory.get_user_headers()

        api_resp = http.delete(url, headers)
        response = Response(api_resp['status'])
        return response

    def delete(self, delete_connections=False):
        return AppacitiveUser.delete_by_id(self.id, delete_connections)

    @user_auth_required
    def update(self, with_revision=False):
        if self.type is None and self.type_id <= 0:
            raise ValidationError('Provide at least one among type name or type id.')

        if self.id <= 0:
            raise ValidationError('User id is missing.')

        url = urlfactory.user_urls["update"](self.id)
        if with_revision:
            url += '?revision=' + self.revision

        headers = urlfactory.get_user_headers()

        payload = self.get_update_command()
        api_resp = http.post(url, headers, payload)
        response = Response(api_resp['status'])

        if response.status_code == '200':
            self.__set_self(api_resp['user'])
        return response

    @user_auth_required
    def update_password(self, old_password, new_password):

        url = urlfactory.user_urls["update_password"](self.id)

        headers = urlfactory.get_user_headers()
        headers[AppacitiveUser.user_auth_header_key] = ApplicationContext.get_user_token()

        payload = {
            "oldpassword": old_password,
            "newpassword": new_password
        }

        json_payload = customjson.serialize(payload)
        api_response = http.post(url, headers, json_payload)
        return Response(api_response['status'])

    @staticmethod
    def send_reset_password_email(username, email_subject):

        url = urlfactory.user_urls["send_reset_password_email"]()
        headers = urlfactory.get_headers()

        payload = {
            "username": username,
            "subject": email_subject
        }

        json_payload = customjson.serialize(payload)
        api_response = http.post(url, headers, json_payload)
        return Response(api_response['status'])

    @staticmethod
    @user_auth_required
    def validate_session():
        url = urlfactory.user_urls["validate_session"]()
        headers = urlfactory.get_user_headers()
        payload = {}

        api_response = http.post(url, headers, customjson.serialize(payload))
        response = Response(api_response['status'])
        if response.status_code == '200':
            response.result = api_response['result']
        return response

    @staticmethod
    @user_auth_required
    def invalidate_session():
        url = urlfactory.user_urls["invalidate_session"]()
        headers = urlfactory.get_user_headers()
        payload = {}

        api_response = http.post(url, headers, customjson.serialize(payload))
        response = Response(api_response['status'])
        if response.status_code == '200':
            response.result = api_response['result']
        return response

    @user_auth_required
    def checkin(self, latitude, longitude):
        url = urlfactory.user_urls["checkin"](self.id, latitude, longitude)
        headers = urlfactory.get_user_headers()
        payload = {}

        api_response = http.post(url, headers, customjson.serialize(payload))
        return Response(api_response['status'])

    @classmethod
    @user_auth_required
    def find(cls, query):

        url = urlfactory.user_urls["find_all"](query)

        headers = urlfactory.get_user_headers()

        api_response = http.get(url, headers)
        response = Response(api_response['status'])
        if response.status_code == '200':

            api_users = api_response.get('users', None)

            return_users = []
            for user in api_users:
                appacitive_user = cls(user)
                return_users.append(appacitive_user)
            response.users = return_users
            return response

