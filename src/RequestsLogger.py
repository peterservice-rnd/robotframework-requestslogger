# -*- coding: utf-8 -*-
import json
import re
from html import escape
from xml.dom import minidom

import decorator
from robot.api import logger
from robot.utils import unic
from six import binary_type, text_type

try:
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache

"""
Library for logging HTTP requests and responses, based on [ http://docs.python-requests.org/en/latest| requests ] library.
"""


def write_log(response):
    """
    Logging of http-request and response

    *Args:*\n
      _response_ - object [ http://docs.python-requests.org/en/latest/api/#requests.Response | "Response" ]

    *Response:*\n
      Formatted output of request and response in test log

    *Example:*\n
    | *Test cases* | *Action*                          | *Argument*            | *Argument*                | *Argument*  |
    | Simple Test  | RequestsLibrary.Create session    | Alias                 | http://www.example.com    |             |
    |              | ${response}=                      | RequestsLibrary.Get request       | Alias         | /           |
    |              | RequestsLogger.Write log          | ${response}           |                           |             |
    """
    msg, converted_string = get_formatted_response(response)
    response_data = u''
    # log formatted response body
    if converted_string:
        response_data = escape(converted_string, quote=False)

    data = u'<details><summary>{0}</summary><p>{1}\n{2}</p></details>'.format(escape(msg[0], quote=False),
                                                                              escape(u'\n'.join(msg), quote=False),
                                                                              response_data)
    logger.info(data, html=True)


@lru_cache(maxsize=2)
def get_formatted_response(response):
    """Format response for http-request.

    *Args:*\n
      _response_ - response for http-request.\n

    *Returns:*\n
      Formatted response for http-request.
    """
    msg = list()
    # request info
    msg.append(
        u'> {0} {1}'.format(response.request.method, response.request.url))
    for req_key, req_value in response.request.headers.items():
        msg.append(u'> {header_name}: {header_value}'.format(header_name=req_key,
                                                             header_value=req_value))
    msg.append(u'>')
    if response.request.body:
        req_body = response.request.body
        if isinstance(req_body, binary_type):
            req_body = unic(req_body)
        msg.append(req_body)
    msg.append(u'* Elapsed time: {0}'.format(response.elapsed))
    msg.append(u'>')
    # response info
    msg.append(u'< {0} {1}'.format(response.status_code, response.reason))
    for res_key, res_value in response.headers.items():
        msg.append(u'< {header_name}: {header_value}'.format(header_name=res_key,
                                                             header_value=res_value))
    # response body
    msg.append(u'<')
    converted_string = u''
    if response.content:
        # get response Content-Type header
        response_content_type = response.headers.get('content-type')
        if 'application/json' in response_content_type:
            response_content = get_decoded_response_body(response.content, response_content_type)
            try:
                converted_string = json.loads(response_content)
                converted_string = json.dumps(converted_string, sort_keys=True,
                                              ensure_ascii=False, indent=4,
                                              separators=(',', ': '))
            except ValueError:
                msg.append(response_content)
                logger.error(u"Incorrect response content type (not application/JSON): {method} {url}".format(
                    method=response.request.method,
                    url=response.request.url))

        elif 'application/xml' in response_content_type:
            xml = minidom.parseString(response.content)
            converted_string = xml.toprettyxml()
        else:
            response_content = get_decoded_response_body(response.content, response_content_type)
            msg.append(response_content)

    return msg, converted_string


def get_decoded_response_body(response_content, response_content_type, encoding='utf-8'):
    """ Decode body response.

    *Args:*\n
      _response_content_: response.\n
      _response_content_type_: response type.\n
      _encoding_: default encoding used when there is no charset in response.\n

    *Returns:*\n
      Decoded response.
    """
    match = re.findall(re.compile('charset=(.*)'), response_content_type)
    # try to decode response body according to encoding provided in response Content-Type header.
    if isinstance(response_content, text_type):
        return response_content
    elif len(match) == 0:
        try:
            return response_content.decode(encoding)
        except UnicodeError:
            return unic(response_content)
    else:
        response_charset = match[0]
        return response_content.decode(response_charset)


def _log_decorator(func, *args, **kwargs):
    """ Write to log.

    *Args:*\n
      _func_: function.\n
      _*args_: arguments for function.\n
      _**kwargs_: arguments for function.\n

    *Returns:*\n
    Response of function call.
    """
    response = func(*args, **kwargs)
    write_log(response)
    return response


def log_decorator(func):
    """
    Decorator for http-requests. Logging request and response.
    Decorated function must return response object [ http://docs.python-requests.org/en/latest/api/#requests | Response ]

    *Args:*\n
      _func_: function.\n

    *Returns:*\n
    Decorated function.\n

    *Example:*

    | @RequestsLogger.log_decorator
    | def get_data(alias, uri)
    |     response = _request_lib_instance().get_request(alias, uri)
    |     return response

    *Output:*
    Formatted output of request and response in test log
    """

    func.cache = {}
    return decorator.decorator(_log_decorator, func)
