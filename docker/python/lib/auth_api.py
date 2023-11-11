import requests
import json
import warnings
import urllib3


def api_get(key: str,
            svr_addr: str,
            api_rqst: str,
            svr_port,
            verify_ssl: bool = False) -> dict:
    """
    This function will make the API get to the server and return the results
    as a JSON object.
    :param key: String containing the API key
    :param svr_addr: String containing the server address
    (example: http://localhost)
    :param svr_port: Int containing the server port
    :param api_rqst: String containing the API request including trailing
    slash (example: /core/users/)
    :param verify_ssl: Boolean to ignore SSL errors (For self-signed certs)
    :return:
    """
    s_addr = svr_addr.rstrip('/')
    s_port = ''
    if svr_port != '':
        s_port = f":{svr_port}"
    api_str = "/api/v3"
    rqst_str = f"{s_addr}{s_port}{api_str}{api_rqst}"
    try:
        if not verify_ssl:
            urllib3.disable_warnings()
        rtn = requests.get(rqst_str, headers={'Authorization': f"Bearer "
                                                               f"{key}"},
                           verify=verify_ssl,
                           timeout=3)
    except requests.exceptions.InvalidURL:
        print("Error: Invalid URL.")
        return {'error': 'Invalid URL'}
    except requests.exceptions.SSLError:
        return {'error': 'Invalid SSL/Self-Signed Certificate'}
    if rtn.status_code not in [200, 400, 403]:
        return {'error': rtn}
    rtn_obj = json.loads(rtn.text)
    return rtn_obj


def api_post(key: str,
            put_data: str,
            svr_addr: str,
            api_rqst: str,
            svr_port,
            verify_ssl: bool = False) -> dict:
    """
    This function will make the API put call to the server and return the
    results
    :param key:
    :param put_data:
    :param svr_addr:
    :param api_rqst:
    :param svr_port:
    :param verify_ssl:
    :return:
    """
    s_addr = svr_addr.rstrip('/')
    s_port = ''
    if svr_port != '':
        s_port = f":{svr_port}"
    api_str = "/api/v3"
    put_str = f"{s_addr}{s_port}{api_str}{api_rqst}"
    headers = {
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
    try:
        if not verify_ssl:
            urllib3.disable_warnings()
        rtn = requests.post(put_str, data=put_data, headers=headers)
    except requests.exceptions.InvalidURL:
        return {'error': 'Invalid URL'}
    if rtn.status_code not in [201, 400, 403]:
        return {'error': rtn}
    elif rtn.status_code == 204:
        # To handle when the password is set successfully and the server
        # returns 204
        return {'OK': 'No Content'}
    rtn_obj = json.loads(rtn.text)
    return rtn_obj


def api_delete(key: str,
             svr_addr: str,
             api_rqst: str,
             svr_port,
             verify_ssl: bool = False):
    """
    This function will make the API delete call to the server and return
    result. If successful, it will return None. If unsuccessful, it will
    return the status code in a dict.
    :param key:
    :param svr_addr:
    :param api_rqst:
    :param svr_port:
    :param verify_ssl:
    :return:
    """
    s_addr = svr_addr.rstrip('/')
    s_port = ''
    if svr_port != '':
        s_port = f":{svr_port}"
    api_str = "/api/v3"
    put_str = f"{s_addr}{s_port}{api_str}{api_rqst}"
    headers = {
        'Authorization': f'Bearer {key}'
    }
    try:
        if not verify_ssl:
            urllib3.disable_warnings()
        rtn = requests.delete(put_str, headers=headers)
    except requests.exceptions.InvalidURL:
        print("Error: Invalid URL.")
        return 404
    if rtn.status_code not in [204, 400, 403]:
        print(f"Error: {rtn.status_code}")
        return rtn.status_code
    return None
