# -*- coding: utf-8 -*-
import json
import re
from functools import lru_cache
from html import escape
from typing import Any, AnyStr, Callable, List, Tuple
from xml.dom import minidom

from decorator import decorator
from requests import Response
from robot.api import logger
from robot.utils import unic

"""
Library for logging HTTP requests and responses, based on [ http://docs.python-requests.org/en/latest| requests ] library.
"""


def write_log(response: Response) -> None:
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
    response_data = ''
    # log formatted response body
    if converted_string:
        response_data = escape(converted_string, quote=False)

    data = '<details><summary>{0}</summary><p>{1}\n{2}</p></details>'.format(escape(msg[0], quote=False),
                                                                             escape('\n'.join(msg), quote=False),
                                                                             response_data)

    logger.info(data, html=True)


@lru_cache(maxsize=2)
def get_formatted_response(response: Response) -> Tuple[List[str], str]:
    """Format response for http-request.

    *Args:*\n
      _response_ - response for http-request.\n

    *Returns:*\n
      Formatted response for http-request.
    """
    msg: List[str] = list()
    # request info
    msg.append(f'> {response.request.method} {response.request.url}')
    for header_name, header_value in response.request.headers.items():
        msg.append(f'> {header_name}: {header_value}')
    msg.append('>')
    if response.request.body:
        msg.append(unic(response.request.body))
    msg.append(f'* Elapsed time: {response.elapsed}')
    msg.append('>')
    # response info
    msg.append(f'< {response.status_code} {response.reason}')
    for header_name, header_value in response.headers.items():
        msg.append(f'< {header_name}: {header_value}')
    # response body
    msg.append('<')
    converted_string = ''
    response_content_type = response.headers.get('content-type') if response.content else None
    if response_content_type:
        # get response Content-Type header
        if 'application/json' in response_content_type:
            response_content = get_decoded_response_body(response.content, response_content_type)
            try:
                converted_string = json.loads(response_content)
                converted_string = json.dumps(converted_string, sort_keys=True,
                                              ensure_ascii=False, indent=4,
                                              separators=(',', ': '))
            except ValueError:
                msg.append(response_content)
                logger.error(f"Incorrect response content type (not application/JSON): "
                             f"{response.request.method} {response.request.url}")

        elif 'application/xml' in response_content_type:
            xml = minidom.parseString(response.content)
            converted_string = xml.toprettyxml()
        else:
            response_content = get_decoded_response_body(response.content, response_content_type)
            msg.append(response_content)

    return msg, converted_string


def get_decoded_response_body(response_content: AnyStr, response_content_type: str, encoding: str = 'utf-8') -> str:
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
    if isinstance(response_content, str):
        return response_content
    elif len(match) == 0:
        try:
            return response_content.decode(encoding)
        except UnicodeDecodeError:
            return unic(response_content)
    else:
        response_charset = match[0]
        return response_content.decode(response_charset)


@decorator
def log_decorator(func: Callable[..., Response], *args: Any, **kwargs: Any) -> Response:
    """
    Decorator for http-requests. Logging request and response.
    Decorated function must return response object [ http://docs.python-requests.org/en/latest/api/#requests | Response ]

    *Args:*\n
      _func_: function.\n
      _*args_: arguments for function.\n
      _**kwargs_: arguments for function.\n

    *Returns:*\n
    Response of function call.

    *Example:*

    | @RequestsLogger.log_decorator
    | def get_data(alias, uri)
    |     response = _request_lib_instance().get_request(alias, uri)
    |     return response

    *Output:*
    Formatted output of request and response in test log
    """

    response = func(*args, **kwargs)
    write_log(response)
    return response
