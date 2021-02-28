import base64


def generate_basic_auth(username, password):
    basic_auth = f'{username}:{password}'
    basic_auth_creds = bytes(basic_auth, encoding='utf-8')
    creds = str(base64.b64encode(basic_auth_creds), encoding='utf-8')
    return f'basic {creds}'
