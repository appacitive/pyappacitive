from pyappacitive.utilities import http, urlfactory
__author__ = 'sathley'

from pyappacitive.entity import AppacitiveEntity
from pyappacitive.error import *
from utilities import customjson
from response import AppacitiveResponse, PagingInfo

# add file upload support using urllib2
# logging with custom data and filters
# file.py response structuring 
# call set self in init
# complete object base 
# incrementally build get dict
# add license file
# run pylint, pyflakes, sphynx
# give graph response proper structure
# session token management
# add code for baseobject
# query and utilities don't have to be modules- remove init.py


class AppacitiveObject(AppacitiveEntity):

    def __init__(self, obj):

        self.type = None
        self.type_id = 0

        if isinstance(obj, str):
            super(AppacitiveObject, self).__init__()
            self.type = obj
            return
        if isinstance(obj, int):
            super(AppacitiveObject, self).__init__()
            self.type_id = obj
            return

        super(AppacitiveObject, self).__init__(obj)
        if obj is not None:
            self.type = obj.get('__type', None)
            self.type_id = int(obj.get('__typeid', 0))

    def __set_self(self, obj):

        super(AppacitiveObject, self)._set_self(obj)

        self.type = obj.get('__type', None)
        self.type_id = int(obj.get('__typeid', 0))

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

    def create(self):

        if self.type is None and self.type_id <= 0:
            raise ValidationError('Provide at least one among type name or type id.')

        url = urlfactory.object_urls["create"](self.type if self.type is not None else self.type_id)
        headers = urlfactory.get_headers()

        api_resp = http.put(url, headers, customjson.serialize(self.get_dict()))

        response = AppacitiveResponse(api_resp['status'])

        if response.status.code == '200':
            self.__set_self(api_resp['object'])
            self._reset_update_commands()

        return response

    def delete(self):

        if self.type is None and self.type_id <= 0:
            raise ValidationError('Provide at least one among type name or type id.')

        if self.id <= 0:
            raise ValidationError('Object id is missing.')

        url = urlfactory.object_urls["delete"](self.type if self.type is not None else self.type_id, self.id)
        headers = urlfactory.get_headers()

        api_resp = http.delete(url, headers)
        response = AppacitiveResponse(api_resp['status'])
        return response

    def delete_with_connections(self):

        if self.type is None and self.type_id <= 0:
            raise ValidationError('Provide at least one among type name or type id.')

        if self.id <= 0:
            raise ValidationError('Object id is missing.')

        url = urlfactory.object_urls["delete_with_connections"](self.type if self.type is not None else self.type_id,
                                                               self.id)
        headers = urlfactory.get_headers()
        api_resp = http.delete(url, headers)
        response = AppacitiveResponse(api_resp['status'])
        return response

    @classmethod
    def multi_delete(cls, object_type, object_ids):

        if object_type is None:
            raise ValidationError('Type is missing.')

        if object_ids is None:
            raise ValidationError('Object ids are missing.')

        url = urlfactory.object_urls["multidelete"](object_type)
        headers = urlfactory.get_headers()

        payload = {"idlist": []}
        for object_id in object_ids:
            payload["idlist"].append(str(object_id))

        api_resp = http.post(url, headers, customjson.serialize(payload))
        response = AppacitiveResponse(api_resp['status'])
        return response

    def update(self, with_revision=False):

        if self.type is None and self.type_id <= 0:
            raise ValidationError('Provide at least one among type name or type id.')

        if self.id <= 0:
            raise ValidationError('Object id is missing.')
        url = urlfactory.object_urls["update"](self.type if self.type is not None else self.type_id, self.id)

        if with_revision:
            url += '?revision=' + self.revision

        headers = urlfactory.get_headers()
        payload = self.get_update_command()

        api_resp = http.post(url, headers, customjson.serialize(payload))
        response = AppacitiveResponse(api_resp['status'])

        if response.status.code == '200':
            updated_object = api_resp['object']
            self.__set_self(updated_object)

        return response

    @classmethod
    def get(cls, object_type, object_id, fields=None):

        if object_type is None:
            raise ValidationError('Type is missing.')

        if object_id is None:
            raise ValidationError('Object id is missing.')

        url = urlfactory.object_urls["get"](object_type, object_id, fields)
        if fields is not None:
            url += '?fields=' + ','.join(fields)
        headers = urlfactory.get_headers()
        api_response = http.get(url, headers)

        response = AppacitiveResponse(api_response['status'])

        if response.status.code == '200':
            obj = api_response['object']
            response.object = cls(obj)
        return response

    def fetch_latest(self):
        url = urlfactory.object_urls["get"](self.type, self.id)
        headers = urlfactory.get_headers()
        api_response = http.get(url, headers)
        response = AppacitiveResponse(api_response['status'])
        if response.status.code == '200':
            self._set_self(api_response['object'])
            self._reset_update_commands()
        return response

    @classmethod
    def multi_get(cls, object_type, object_ids, fields=None):

        if object_type is None:
            raise ValidationError('Type is missing.')

        if object_ids is None:
            raise ValidationError('Object ids are missing.')

        url = urlfactory.object_urls["multiget"](object_type, object_ids, fields)

        headers = urlfactory.get_headers()
        api_response = http.get(url, headers)

        response = AppacitiveResponse(api_response['status'])
        if response.status.code == '200':

            api_objects = api_response.get('objects', None)

            return_objects = []
            for obj in api_objects:
                appacitive_object = cls(obj)
                return_objects.append(appacitive_object)
            response.objects = return_objects
            return response

    @classmethod
    def find(cls, object_type, query, fields=None):

        if object_type is None:
            raise ValidationError('Type is missing.')

        url = urlfactory.object_urls["find_all"](object_type, query, fields)
        headers = urlfactory.get_headers()
        api_response = http.get(url, headers)

        response = AppacitiveResponse(api_response['status'])
        if response.status.code == '200':

            api_objects = api_response.get('objects', None)

            return_objects = []
            for obj in api_objects:
                appacitive_object = cls(obj)
                return_objects.append(appacitive_object)
            response.objects = return_objects
            response.paging_info = PagingInfo(api_response['paginginfo'])
            return response

    @classmethod
    def find_in_between_two_objects(cls, object_type, object_a_id, relation_a, label_a, object_b_id, relation_b, label_b, fields=None):

        if object_type is None:
            raise ValidationError('Type is missing.')

        url = urlfactory.object_urls["find_between_two_objects"](object_type, object_a_id, relation_a, label_a, object_b_id, relation_b, label_b, fields)

        headers = urlfactory.get_headers()
        api_response = http.get(url, headers)

        response = AppacitiveResponse(api_response['status'])
        if response.status.code == '200':

            api_objects = api_response.get('objects', None)

            return_objects = []
            for obj in api_objects:
                appacitive_object = cls(obj)
                return_objects.append(appacitive_object)
            response.objects = return_objects
            response.paging_info = PagingInfo(api_response['paginginfo'])
            return response


