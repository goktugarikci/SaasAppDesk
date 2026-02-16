# api/auth_api.py
import requests

BASE_URL = "http://localhost:8080/api"

def login(email, password):
    """C++ Sunucusuna giriş isteği atar ve yanıtı döndürür."""
    try:
        url = f"{BASE_URL}/auth/login"
        payload = {"email": email, "password": password}
        response = requests.post(url, json=payload, timeout=5)

        if response.status_code == 200:
            # ÖNEMLİ: C++'dan gelen tüm JSON yanıtını (Token dahil) geri döndür
            return True, response.json()
        else:
            return False, f"Giriş başarısız. Lütfen bilgilerinizi kontrol edin. (Hata: {response.status_code})"
    except Exception as e:
        return False, f"Sunucuya bağlanılamadı: {e}"

def register(name, email, password):
    try:
        url = f"{BASE_URL}/auth/register"
        payload = {"name": name, "email": email, "password": password}
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code in [200, 201]:
            return True, "Kayıt başarılı! Lütfen giriş yapın."
        else:
            return False, f"Kayıt başarısız. (Hata: {response.status_code})"
    except Exception as e:
        return False, f"Sunucu hatası: {e}"

# Google Auth kısımları (Eğer kullanıyorsanız dokunmayın, aynı kalsın)
def get_google_auth_url():
    return None

def verify_google_code(code):
    return False, "Google Auth henüz backend'e bağlanmadı."