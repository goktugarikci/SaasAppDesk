# api/auth_api.py
from core.api_client import ApiClient
from core import config

api = ApiClient()

def login(email, password):
    response = api.post("auth/login", data={"email": email, "password": password})
    if response.status_code == 200:
        data = response.json()
        config.CURRENT_TOKEN = data.get("token")
        return True, data
    return False, response.text if response.text else "E-posta veya şifre hatalı."

def register(name, email, password):
    response = api.post("auth/register", data={"name": name, "email": email, "password": password})
    if response.status_code == 201:
        return True, "Kayıt başarılı! Şimdi giriş yapabilirsiniz."
    return False, "Kayıt başarısız. Bu e-posta zaten kullanımda olabilir."

def get_google_auth_url():
    response = api.get("auth/google/url")
    if response.status_code == 200:
        return response.json().get("url")
    return None

def verify_google_code(auth_code):
    response = api.post("auth/google/callback", data={"code": auth_code})
    if response.status_code == 200:
        data = response.json()
        config.CURRENT_TOKEN = data.get("token")
        return True, data
    return False, "Google doğrulaması başarısız oldu."