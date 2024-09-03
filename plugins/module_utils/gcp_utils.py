# -*- coding: utf-8 -*-

# Copyright: (c) 2018, Google Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import os
import json
import time

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import google.auth
    import google.auth.compute_engine
    from google.oauth2 import service_account, credentials as oauth2
    from google.auth.transport.requests import AuthorizedSession
    HAS_GOOGLE_LIBRARIES = True
except ImportError:
    HAS_GOOGLE_LIBRARIES = False

from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible.module_utils._text import to_text


def remove_nones(obj):
    """Remove empty values in complex object.

    Args:
        obj: obj, the initial object.

    Returns:
        obj, the resulting object with all empty values removed.
    """
    if isinstance(obj, list):
        new_obj = []
        for item in obj:
            value = remove_nones(item)
            if value or value is False or value == '':
                new_obj.append(value)
        return new_obj
    elif isinstance(obj, dict):
        new_obj = {}
        for key in obj:
            value = remove_nones(obj[key])
            if value or value is False or value == '':
                new_obj[key] = value
        return new_obj
    else:
        new_obj = None
        if obj or obj is False or obj == '':
            new_obj = obj
        return new_obj


def navigate_hash(source, path, default=None):
    """Return values along a dictionary tree.

    Args:
        source: dict, the dictionary to query.
        path: tuple, the list of nodes to follow in the dictionary.
        default: str, the default return value. defaults to None.

    Returns:
        dict, the found value along the navigated dictionary tree.
    """
    if not source:
        return None

    key = path[0]
    path = path[1:]
    if key not in source:
        return default
    result = source[key]
    if path:
        return navigate_hash(result, path, default)
    return result


def wait_for_operation(module, response, api):
    """Return the final response of an operation.

    Args:
        module: AnsibleModule, the ansible module.
        response: requests.Response, the initial operation response.
        api: str, the api URL supporting the operation.

    Returns:
        dict, the resource info after the operation has ended.
    """
    op_result = return_if_object(module, response)['result']
    if not op_result:
        return {}
    status = navigate_hash(op_result, ['done'])
    wait_done = wait_for_completion(status, op_result, module, api)
    raise_if_errors(wait_done, ['error'], module)
    return navigate_hash(wait_done, ['response'])


def wait_for_completion(status, op_result, module, api):
    """Wait for an operation to end.

    Args:
        status: bool, wether the operation is done or not.
        op_result: dict, the current operation info.
        module: AnsibleModule, the ansible module.
        api: str, the api URL supporting the operation.

    Returns:
        dict, the final operation info after completion.
    """
    op_id = navigate_hash(op_result, ['name'])
    op_uri = async_op_url({'op_id': op_id}, api)
    while not status:
        raise_if_errors(op_result, ['error'], module)
        time.sleep(1.0)
        op_result = fetch_resource(module, op_uri, False)['result']
        status = navigate_hash(op_result, ['done'])
    return op_result


def async_op_url(extra_data=None, api=None):
    """Return the URL to call for operations info.

    Args:
        module: AnsibleModule, the ansible module.
        extra_data: dict, any data.
        api: str, the api URL supporting the operation.

    Returns:
        dict, the URL to call.
    """
    if extra_data is None:
        extra_data = {}
    url = "{api}/{op_id}".format(api=api, **extra_data)
    return url


def raise_if_errors(response, err_path, module):
    """Raise errors in response.

    Args:
        response: dict, the response object.
        err_path: tuple, the path to look for errors in form of a tuple of keys.
        module: AnsibleModule, the ansible module.
    """
    errors = navigate_hash(response, err_path)
    if errors is not None:
        module.fail_json(msg=errors)


def fetch_resource(module, link, allow_not_found=False):
    """Return the resource info.

    Args:
        module: AnsibleModule, the ansible module.
        link: str, the URL to call for the resource.
        allow_not_found: bool, wether the not found response should be a valid response.

    Returns:
        dict, the resource info.
    """
    auth = GcpSession(module, 'gcp')
    return return_if_object(module, auth.get(link), allow_not_found=allow_not_found)


def return_if_object(module, response, err_path=('error', 'message'), allow_not_found=False):
    """Return the object of the response if no errors found.

    Args:
        module: AnsibleModule, the ansible module.
        response: requests.Response, the response.
        err_path: tuple, the path to look for errors in form of a tuple of keys.
        allow_not_found: bool, wether the not found response should be a valid response.

    Returns:
        dict, the returned object.
    """
    # If not found, return nothing.
    if allow_not_found and response.status_code == 404:
        return {
            'result': None,
            'status_code': response.status_code,
            'url': response.url
        }

    # If no content, return nothing.
    if response.status_code == 204:
        return {
            'result': None,
            'status_code': response.status_code,
            'url': response.url
        }

    # SQL only: return on 403 if not exist
    # if allow_not_found and response.status_code == 403:
    #     return None

    # Any other error status code should raise an exception
    module.raise_for_status(response)

    try:
        result = response.json()
    except getattr(json.decoder, 'JSONDecodeError', ValueError) as inst:
        module.fail_json(msg="Invalid JSON response with error: %s" % inst)

    if navigate_hash(result, err_path):
        module.fail_json(msg=navigate_hash(result, err_path))

    full_result = {
        'result': result,
        'status_code': response.status_code,
        'url': response.url
    }

    return full_result


def list_differences(request, response):
    """List the differences between two objects.

    Args:
        request: dict, the request object.
        response: dict, the response object.

    Returns:
        dict, the differences as a dictionary with 'add' and 'remove' entries.
    """
    adding_list = GcpRequest(request).difference(GcpRequest(response))
    removing_list = GcpRequest(response).difference(GcpRequest(request))

    difference = {}
    difference.update({'remove': removing_list} if removing_list else {})
    difference.update({'add': adding_list} if adding_list else {})

    return difference


class GcpSession(object):
    """Handles all authentication and HTTP sessions for GCP API calls.

    For each request, the class sets the authentication and REST method.

    Attributes:
        module: AnsibleModule, the ansible module.
        product: the GCP product reference.
    """
    def __init__(self, module, product):
        """Initializes the instance based on attributes.

        Args:
            module: AnsibleModule, the ansible module.
            product: the GCP product reference.
        """
        self.module = module
        self.product = product
        self._validate()

    def get(self, url, body=None, **kwargs):
        """This method should be avoided in favor of full_get
        """
        kwargs.update({'json': body})
        return self.full_get(url, **kwargs)

    def post(self, url, body=None, headers=None, **kwargs):
        """Implement the POST method for the session request.

        Args:
            url: str, the URL to call for the request.
            body: dict, the body for the request.
            headers: dict, the headers for the request.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            requests.Response, the response from the request.
        """
        kwargs.update({'json': body, 'headers': headers})
        return self.full_post(url, **kwargs)

    def post_contents(self, url, file_contents=None, headers=None, **kwargs):
        """This method should be avoided in favor of full_post
        """
        kwargs.update({'data': file_contents, 'headers': headers})
        return self.full_post(url, **kwargs)

    def delete(self, url, body=None):
        """This method should be avoided in favor of full_delete
        """
        kwargs = {'json': body}
        return self.full_delete(url, **kwargs)

    def put(self, url, body=None, params=None):
        """Implement the PUT method for the sessions request.

        Args:
            url: str, the URL to call for the request.
            body: dict, the body for the request.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            requests.Response, the response from the request.
        """
        kwargs = {'json': body}
        return self.full_put(url, params=params, **kwargs)

    def patch(self, url, body=None, **kwargs):
        """Implement the PATCH method for the sessions request.

        Args:
            url: str, the URL to call for the request.
            body: dict, the body for the request.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            requests.Response, the response from the request.
        """
        kwargs.update({'json': body})
        return self.full_patch(url, **kwargs)

    def list(self, url, callback, params=None, array_name='items',
             pageToken='nextPageToken', **kwargs):
        """Calls for an API with a LIST format.

        Args:
            url: str, the URL to call for the request.
            callback: func, the function to decode the response.
            params: dict, query-parameters for the request.
            array_name: str, the resource name to look for the list in the API
                response. Defaults to 'data'.
            pageToken: str, the name of the token to follow the page ordering.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            dict, the list response from the API.
        """
        resp = callback(self.module, self.full_get(url, params, **kwargs))['result']
        items = resp.get(array_name) if resp.get(array_name) else []
        while resp.get(pageToken):
            if params:
                params['pageToken'] = resp.get(pageToken)
            else:
                params = {'pageToken': resp[pageToken]}

            resp = callback(self.module, self.full_get(url, params, **kwargs))['result']
            if resp.get(array_name):
                items = items + resp.get(array_name)
        return items

    def search(self, url, callback, data=None, array_name='items', pageToken='nextPageToken', **kwargs):
        """Calls for an API with a SEARCH format.

        Args:
            url: str, the URL to call for the request.
            callback: func, the function to decode the response.
            data: dict, the data to POST in the request. Defaults to None.
            array_name: str, the resource name to look for the list in the API
                response. Defaults to 'items'.
            pageToken: str, the name of the token to follow the page ordering.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            dict, the list response from the API.
        """
        resp = callback(self.module, self.full_post(url, data, **kwargs))['result']
        items = resp.get(array_name) if resp.get(array_name) else []
        while resp.get(pageToken):
            if data:
                data['pageToken'] = resp.get(pageToken)
            else:
                data = {'pageToken': resp[pageToken]}

            resp = callback(self.module, self.full_post(url, data, **kwargs))['result']
            if resp.get(array_name):
                items = items + resp.get(array_name)
        return items

    def full_get(self, url, params=None, **kwargs):
        """Implement the GET method for the session request.

        Args:
            url: str, the URL to call for the request.
            params: dict, query-parameters for the reuqest.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            requests.Response, the response from the request.
        """
        kwargs['headers'] = self._set_headers(kwargs.get('headers'))
        try:
            return self.session().get(url, params=params, **kwargs)
        except getattr(requests.exceptions, 'RequestException') as inst:
            # Only log the message to avoid logging any sensitive info.
            self.module.fail_json(msg=inst.message)

    def full_post(self, url, data=None, json=None, **kwargs):
        kwargs['headers'] = self._set_headers(kwargs.get('headers'))

        try:
            return self.session().post(url, data=data, json=json, **kwargs)
        except getattr(requests.exceptions, 'RequestException') as inst:
            self.module.fail_json(msg=inst.message)

    def full_put(self, url, data=None, **kwargs):
        kwargs['headers'] = self._set_headers(kwargs.get('headers'))

        try:
            return self.session().put(url, data=data, **kwargs)
        except getattr(requests.exceptions, 'RequestException') as inst:
            self.module.fail_json(msg=inst.message)

    def full_patch(self, url, data=None, **kwargs):
        kwargs['headers'] = self._set_headers(kwargs.get('headers'))

        try:
            return self.session().patch(url, data=data, **kwargs)
        except getattr(requests.exceptions, 'RequestException') as inst:
            self.module.fail_json(msg=inst.message)

    def full_delete(self, url, **kwargs):
        """Implement the DELETE method for the sessions request.

        Args:
            url: str, the URL to call for the request.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            requests.Response, the response from the request.
        """
        kwargs['headers'] = self._set_headers(kwargs.get('headers'))

        try:
            return self.session().delete(url, **kwargs)
        except getattr(requests.exceptions, 'RequestException') as inst:
            self.module.fail_json(msg=inst.message)

    def _set_headers(self, headers):
        """Generates all basic HTTP headers.

        Returns:
            dict, the basic HTTP headers.
        """
        if headers:
            return self._merge_dictionaries(headers, self._headers())
        return self._headers()

    def session(self):
        """Generates an HTTP session.

        Returns:
            requests.Session, the HTTP session.
        """
        return AuthorizedSession(
            self._credentials())

    def _validate(self):
        """Verify if module has proper dependencies.
        """
        if not HAS_REQUESTS:
            self.module.fail_json(msg="Please install the requests library")

        if not HAS_GOOGLE_LIBRARIES:
            self.module.fail_json(msg="Please install the google-auth library")

        if self.module.params.get('service_account_email') is not None and self.module.params['auth_kind'] != 'machineaccount':
            self.module.fail_json(
                msg="Service Account Email only works with Machine Account-based authentication"
            )

        if (self.module.params.get('service_account_file') is not None or
                self.module.params.get('service_account_contents') is not None) and self.module.params['auth_kind'] != 'serviceaccount':
            self.module.fail_json(
                msg="Service Account File only works with Service Account-based authentication"
            )

        if self.module.params.get('access_token') is not None and self.module.params['auth_kind'] != 'accesstoken':
            self.module.fail_json(
                msg='Supplying access_token requires auth_kind set to accesstoken'
            )

    def _credentials(self):
        cred_type = self.module.params['auth_kind']

        if cred_type == 'application':
            credentials, project_id = google.auth.default(scopes=self.module.params['scopes'])
            return credentials

        if cred_type == 'serviceaccount':
            service_account_file = self.module.params.get('service_account_file')
            service_account_contents = self.module.params.get('service_account_contents')
            if service_account_file is not None:
                path = os.path.realpath(os.path.expanduser(service_account_file))
                try:
                    svc_acct_creds = service_account.Credentials.from_service_account_file(path)
                except OSError as e:
                    self.module.fail_json(
                        msg="Unable to read service_account_file at %s: %s" % (path, e.strerror)
                    )
            elif service_account_contents is not None:
                try:
                    info = json.loads(service_account_contents)
                except json.decoder.JSONDecodeError as e:
                    self.module.fail_json(
                        msg="Unable to decode service_account_contents as JSON: %s" % e
                    )
                svc_acct_creds = service_account.Credentials.from_service_account_info(info)
            else:
                self.module.fail_json(
                    msg='Service Account authentication requires setting either service_account_file or service_account_contents'
                )
            return svc_acct_creds.with_scopes(self.module.params['scopes'])

        if cred_type == 'machineaccount':
            email = self.module.params['service_account_email']
            email = email if email is not None else "default"
            return google.auth.compute_engine.Credentials(email)

        if cred_type == 'accesstoken':
            access_token = self.module.params['access_token']
            if access_token is None:
                self.module.fail_json(
                    msg='An access token must be supplied when auth_kind is accesstoken'
                )
            return oauth2.Credentials(access_token, scopes=self.module.params['scopes'])

        self.module.fail_json(msg="Credential type '%s' not implemented" % cred_type)

    def _headers(self):
        user_agent = "Google-Ansible-MM-{0}".format(self.product)
        if self.module.params.get('env_type'):
            user_agent = "{0}-{1}".format(user_agent, self.module.params.get('env_type'))
        return {
            'User-Agent': user_agent
        }

    def _merge_dictionaries(self, a, b):
        """Merge two dictionaries into one.

        Args:
            a: dict, the first dictionary.
            b: dict, the second dictionary.

        Returns:
            dict, the result dictionary.
        """
        new = a.copy()
        new.update(b)
        return new


class GcpModule(AnsibleModule):
    """A class to handle all basic features for HCP Terraform modules.

    Inherits from the AnsibleModule class.
    """
    def __init__(self, *args, **kwargs):
        """Initializes the instance based on attributes.

        Args:
            *args: Arbitrary arguments.
            **kwargs: Arbitrary keyword arguments.
        """
        arg_spec = kwargs.get('argument_spec', {})

        kwargs['argument_spec'] = self._merge_dictionaries(
            arg_spec,
            dict(
                project=dict(
                    required=False,
                    type='str',
                    fallback=(env_fallback, ['GCP_PROJECT'])),
                auth_kind=dict(
                    required=True,
                    fallback=(env_fallback, ['GCP_AUTH_KIND']),
                    choices=['machineaccount', 'serviceaccount', 'accesstoken', 'application'],
                    type='str'),
                service_account_email=dict(
                    required=False,
                    fallback=(env_fallback, ['GCP_SERVICE_ACCOUNT_EMAIL']),
                    type='str'),
                service_account_file=dict(
                    required=False,
                    fallback=(env_fallback, ['GCP_SERVICE_ACCOUNT_FILE']),
                    type='path'),
                service_account_contents=dict(
                    required=False,
                    fallback=(env_fallback, ['GCP_SERVICE_ACCOUNT_CONTENTS']),
                    no_log=True,
                    type='jsonarg'),
                access_token=dict(
                    required=False,
                    fallback=(env_fallback, ['GCP_ACCESS_TOKEN']),
                    no_log=True,
                    type='str'),
                scopes=dict(
                    required=False,
                    fallback=(env_fallback, ['GCP_SCOPES']),
                    type='list',
                    elements='str'),
                env_type=dict(
                    required=False,
                    fallback=(env_fallback, ['GCP_ENV_TYPE']),
                    type='str')
            )
        )

        mutual = kwargs.get('mutually_exclusive', [])

        kwargs['mutually_exclusive'] = mutual.append(
            ['service_account_email', 'service_account_file', 'service_account_contents']
        )

        AnsibleModule.__init__(self, *args, **kwargs)

    def raise_for_status(self, response):
        """Raises an HTTP exception from the response, if any.

        Args:
            response: requests.Response, the response to parse.
        """
        try:
            response.raise_for_status()
        except getattr(requests.exceptions, 'RequestException'):
            self.fail_json(
                msg="GCP returned error: %s" % response.json(),
                request={
                    "url": response.request.url,
                    "body": response.request.body,
                    "method": response.request.method,
                }
            )

    def _merge_dictionaries(self, a, b):
        """Merge two dictionaries into one.

        Args:
            a: dict, the first dictionary.
            b: dict, the second dictionary.

        Returns:
            dict, the result dictionary.
        """
        new = a.copy()
        new.update(b)
        return new


class GcpRequest(object):
    """A class to difference checking two API objects.

    This will be primarily used for checking dictionaries.
    In an equivalence check, the left-hand dictionary will be the request and
    the right-hand side will be the response.
    Extra keys in response will be ignored.
    Ordering of lists does not matter. Exception: lists of dictionaries are
    assumed to be in sorted order.

    Attributes:
        request: obj, the request to check.
    """
    def __init__(self, request):
        """Initializes the instance based on attributes.

        Args:
            request: obj, the request to check.
        """
        self.request = request

    def __eq__(self, other):
        """Defines the equality relationship.

        Args:
            other: obj, the object to compare to self.

        Returns:
            bool, True if self and other are equal.
        """
        return not self.difference(other) and not other.difference(self)

    def __ne__(self, other):
        """Defines the non-equality relationship.

        Args:
            other: obj, the object to compare to self.

        Returns:
            bool, True if self and other are different.
        """
        return not self.__eq__(other)

    def difference(self, response):
        """Returns the difference between a request and a response.

        While this is used under the hood for __eq__ and __ne__, it is useful
        for debugging.

        Args:
            response: obj, the object to compare to self.

        Returns:
            obj, the differential comparison between self and response.
        """
        return self._compare_value(self.request, response.request)

    def _compare_dicts(self, req_dict, resp_dict):
        """Compares two dictionaries.

        Args:
            req_dict: dict, the request dictionary.
            resp_dict: dict, the response dictionary.

        Returns:
            dict, the differential comparison between request and response.
        """
        difference = {}
        for key in req_dict:
            resp_value = resp_dict.get(key)
            if resp_value is not None:
                difference[key] = self._compare_value(req_dict.get(key), resp_value)
            else:
                difference[key] = req_dict.get(key)

        # Remove all empty values from difference.
        sanitized_difference = {}
        for key in difference:
            if difference[key]:
                sanitized_difference[key] = difference[key]

        return sanitized_difference

    def _compare_lists(self, req_list, resp_list):
        """Compares two lists.

        All things in the list should be identical (even if a dictionary)

        Args:
            req_list: list, the request list.
            resp_list: list, the response list.

        Returns:
            list, the differential comparison between request and response.
        """
        # Have to convert each thing over to unicode.
        # Python doesn't handle equality checks between unicode + non-unicode well.
        difference = []
        new_req_list = self._convert_value(req_list)
        new_resp_list = self._convert_value(resp_list)

        # We have to compare each thing in the request to every other thing
        # in the response.
        # This is because the request value will be a subset of the response value.
        # The assumption is that these lists will be small enough that it won't
        # be a performance burden.
        for req_item in new_req_list:
            found_item = False
            for resp_item in new_resp_list:
                # Looking for a None value here.
                if not self._compare_value(req_item, resp_item):
                    found_item = True
            if not found_item:
                difference.append(req_item)

        difference2 = []
        for value in difference:
            if value:
                difference2.append(value)

        return difference2

    def _compare_value(self, req_value, resp_value):
        """Compare two values of arbitrary types.

        Args:
            req_value: obj, the request object.
            resp_value: obj, the response object.

        Returns:
            obj, the differential comparison between request and response.
        """
        diff = None
        # If response is None, the difference is set to req_value, which may still be None
        if resp_value is None:
            return req_value

        # Can assume non-None types at this point.
        try:
            if isinstance(req_value, list):
                diff = self._compare_lists(req_value, resp_value)
            elif isinstance(req_value, dict):
                diff = self._compare_dicts(req_value, resp_value)
            elif isinstance(req_value, bool):
                diff = self._compare_boolean(req_value, resp_value)
            # Always use to_text values to avoid unicode issues.
            elif to_text(req_value) != to_text(resp_value):
                diff = req_value
        # to_text may throw UnicodeErrors.
        # These errors shouldn't crash Ansible and should be hidden.
        except UnicodeError:
            pass

        return diff

    # Compare two boolean values.
    def _compare_boolean(self, req_value, resp_value):
        """Compare two boolean values.

        Args:
            req_value: bool, the request boolean.
            resp_value: bool, the response boolean.

        Returns:
            bool, True if boolean are different, None otherwise.
        """
        try:
            # Both True
            if req_value and isinstance(resp_value, bool) and resp_value:
                return None
            # Value1 True, resp_value 'true'
            if req_value and to_text(resp_value) == 'true':
                return None
            # Both False
            if not req_value and isinstance(resp_value, bool) and not resp_value:
                return None
            # Value1 False, resp_value 'false'
            if not req_value and to_text(resp_value) == 'false':
                return None
            return True

        # to_text may throw UnicodeErrors.
        # These errors shouldn't crash Ansible and should be hidden.
        except UnicodeError:
            return None

    def _convert_value(self, value):
        """Convert to standard format.

        Python (2 esp.) doesn't do comparisons between unicode and non-unicode
        well. This leads to a lot of false positives when diffing values. The
        Ansible to_text() function is meant to get all strings into a standard
        format.

        Args:
            value: obj, the object to format.

        Returns:
            obj, the formatted object.
        """
        if isinstance(value, list):
            new_list = []
            for item in value:
                new_list.append(self._convert_value(item))
            return new_list
        if isinstance(value, dict):
            new_dict = {}
            for key in value:
                new_dict[key] = self._convert_value(value[key])
            return new_dict
        return to_text(value)
