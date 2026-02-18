import requests
from PySide6.QtCore import QThread, Signal, QSettings
from core.config import BASE_API_URL

def get_api_headers():
    settings = QSettings("MySaaS", "DesktopClient")
    settings.sync()
    token = settings.value("auth_token", "")
    return {"Authorization": str(token).strip() if token else ""}

class ApiFetchProfileThread(QThread):
    finished_signal = Signal(bool, dict) 
    def run(self):
        try:
            response = requests.get(f"{BASE_API_URL}/users/me", headers=get_api_headers(), timeout=5)
            if response.status_code == 200: self.finished_signal.emit(True, response.json()) 
            else: self.finished_signal.emit(False, {})
        except: self.finished_signal.emit(False, {})

class ApiCreateServerThread(QThread):
    finished_signal = Signal(bool, str, str) 
    def __init__(self, server_name):
        super().__init__(); self.server_name = server_name
    def run(self):
        try:
            headers = get_api_headers()
            res_server = requests.post(f"{BASE_API_URL}/servers", json={"name": self.server_name}, headers=headers, timeout=5)
            
            # JSON decode hatasını önlemek için kontrol
            try:
                data = res_server.json()
            except:
                data = {}

            if res_server.status_code not in [200, 201]:
                if res_server.status_code == 401: self.finished_signal.emit(False, "", "UNAUTHORIZED")
                elif res_server.status_code == 403: self.finished_signal.emit(False, "", "LIMIT_EXCEEDED")
                else: self.finished_signal.emit(False, f"Hata: {res_server.status_code}", "GENERAL")
                return
            
            server_id = data.get("id") or data.get("server_id")

            if not server_id:
                self.finished_signal.emit(True, f"'{self.server_name}' oluşturuldu! (ID alınamadı)", "NONE")
                return

            # Default kanalları oluştur (Hata olsa bile devam et)
            try:
                url_channel = f"{BASE_API_URL}/servers/{server_id}/channels"
                requests.post(url_channel, json={"name": "genel-sohbet", "type": 0}, headers=headers, timeout=3)
                res_kanban = requests.post(url_channel, json={"name": "Proje Panosu", "type": 3}, headers=headers, timeout=3)
            except: pass
                    
            self.finished_signal.emit(True, f"'{self.server_name}' çalışma alanı hazır!", "NONE")
        except Exception as e: self.finished_signal.emit(False, f"Bağlantı koptu: {e}", "GENERAL")

class ApiFetchMyServersThread(QThread):
    finished_signal = Signal(bool, list, str) 
    def run(self):
        try:
            response = requests.get(f"{BASE_API_URL}/servers", headers=get_api_headers(), timeout=5)
            if response.status_code == 200: 
                try: self.finished_signal.emit(True, response.json(), "NONE")
                except: self.finished_signal.emit(False, [], "GENERAL")
            elif response.status_code == 401: self.finished_signal.emit(False, [], "UNAUTHORIZED")
            else: self.finished_signal.emit(False, [], "GENERAL")
        except: self.finished_signal.emit(False, [], "GENERAL")

class ApiJoinServerThread(QThread):
    finished_signal = Signal(bool, str, str)
    def __init__(self, invite_code):
        super().__init__(); self.invite_code = invite_code
    def run(self):
        try:
            response = requests.post(f"{BASE_API_URL}/servers/join", json={"invite_code": self.invite_code}, headers=get_api_headers(), timeout=5)
            if response.status_code in [200, 201]: self.finished_signal.emit(True, "Sunucuya başarıyla katıldınız!", "NONE")
            elif response.status_code == 401: self.finished_signal.emit(False, "", "UNAUTHORIZED")
            else: self.finished_signal.emit(False, "Geçersiz veya süresi dolmuş davet kodu!", "INVALID")
        except: self.finished_signal.emit(False, "Sunucuya ulaşılamadı.", "GENERAL")

class ApiSearchUsersThread(QThread):
    finished_signal = Signal(bool, list)
    def __init__(self, search_query):
        super().__init__(); self.search_query = search_query
    def run(self):
        try:
            if not self.search_query: return self.finished_signal.emit(True, [])
            response = requests.get(f"{BASE_API_URL}/users/search?q={self.search_query}", headers=get_api_headers(), timeout=5)
            if response.status_code == 200: self.finished_signal.emit(True, response.json())
            else: self.finished_signal.emit(False, [])
        except: self.finished_signal.emit(False, [])

class ApiAddFriendThread(QThread):
    finished_signal = Signal(bool, str)
    def __init__(self, target_user_id):
        super().__init__(); self.target_user_id = target_user_id
    def run(self):
        try:
            # 405 Hatası genellikle yanlış metod (GET/POST) veya URL sonundaki '/' karakterinden kaynaklanır.
            # Burada POST kullanıyoruz.
            response = requests.post(f"{BASE_API_URL}/friends/add", json={"friend_id": self.target_user_id}, headers=get_api_headers(), timeout=5)
            
            if response.status_code == 200: 
                self.finished_signal.emit(True, "İstek gönderildi.")
            elif response.status_code == 405:
                self.finished_signal.emit(False, "Sunucu Metod Hatası (405). API kontrol edilmeli.")
            else: 
                self.finished_signal.emit(False, f"Reddedildi ({response.status_code})")
        except Exception as e: 
            self.finished_signal.emit(False, f"Bağlantı hatası: {str(e)}")

# --- KANAL CRUD İŞLEMLERİ THREADLERİ ---

class ApiFetchChannelsThread(QThread):
    finished_signal = Signal(bool, list)
    def __init__(self, server_id):
        super().__init__(); self.server_id = server_id
    def run(self):
        try:
            res = requests.get(f"{BASE_API_URL}/servers/{self.server_id}/channels", headers=get_api_headers(), timeout=5)
            if res.status_code == 200: self.finished_signal.emit(True, res.json())
            else: self.finished_signal.emit(False, [])
        except: self.finished_signal.emit(False, [])

class ApiCreateChannelThread(QThread):
    finished_signal = Signal(bool, str)
    def __init__(self, server_id, name, type_id):
        super().__init__(); self.server_id = server_id; self.name = name; self.type_id = type_id
    def run(self):
        try:
            payload = {"name": self.name, "type": self.type_id}
            res = requests.post(f"{BASE_API_URL}/servers/{self.server_id}/channels", json=payload, headers=get_api_headers(), timeout=5)
            if res.status_code in [200, 201]: self.finished_signal.emit(True, "Kanal oluşturuldu.")
            else: self.finished_signal.emit(False, "Kanal oluşturulamadı.")
        except: self.finished_signal.emit(False, "Bağlantı hatası.")

class ApiUpdateChannelThread(QThread):
    finished_signal = Signal(bool, str)
    def __init__(self, channel_id, name, type_id):
        super().__init__(); self.channel_id = channel_id; self.name = name; self.type_id = type_id
    def run(self):
        try:
            payload = {"name": self.name, "type": self.type_id}
            res = requests.put(f"{BASE_API_URL}/channels/{self.channel_id}", json=payload, headers=get_api_headers(), timeout=5)
            if res.status_code == 200: self.finished_signal.emit(True, "Kanal güncellendi.")
            else: self.finished_signal.emit(False, "Güncelleme başarısız.")
        except: self.finished_signal.emit(False, "Bağlantı hatası.")

class ApiDeleteChannelThread(QThread):
    finished_signal = Signal(bool, str)
    def __init__(self, channel_id):
        super().__init__(); self.channel_id = channel_id
    def run(self):
        try:
            res = requests.delete(f"{BASE_API_URL}/channels/{self.channel_id}", headers=get_api_headers(), timeout=5)
            if res.status_code == 200: self.finished_signal.emit(True, "Kanal silindi.")
            else: self.finished_signal.emit(False, "Silme başarısız.")
        except: self.finished_signal.emit(False, "Bağlantı hatası.")

class ApiFetchFriendRequestsThread(QThread):
    finished_signal = Signal(bool, list)
    def run(self):
        try:
            res = requests.get(f"{BASE_API_URL}/friends/requests", headers=get_api_headers(), timeout=5)
            if res.status_code == 200: self.finished_signal.emit(True, res.json())
            else: self.finished_signal.emit(False, [])
        except: self.finished_signal.emit(False, [])

class ApiHandleRequestThread(QThread):
    finished_signal = Signal(bool, str)
    def __init__(self, req_id, endpoint_suffix, action="accept"):
        super().__init__()
        self.req_id = req_id
        self.endpoint_suffix = endpoint_suffix 
        self.action = action 
    def run(self):
        try:
            url = f"{BASE_API_URL}/{self.endpoint_suffix}/requests/{self.req_id}/{self.action}"
            res = requests.post(url, headers=get_api_headers(), timeout=5)
            if res.status_code == 200: self.finished_signal.emit(True, "İşlem başarılı.")
            else: self.finished_signal.emit(False, f"Hata: {res.status_code}")
        except: self.finished_signal.emit(False, "Bağlantı hatası.")

class ApiFetchServerInvitesThread(QThread):
    finished_signal = Signal(bool, list)
    def run(self):
        try:
            res = requests.get(f"{BASE_API_URL}/servers/invites", headers=get_api_headers(), timeout=5)
            if res.status_code == 200: self.finished_signal.emit(True, res.json())
            else: self.finished_signal.emit(False, [])
        except: self.finished_signal.emit(False, [])