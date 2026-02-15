# ui/views/dashboard_view.py
import os
import webbrowser
import requests
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QStackedWidget, QListWidget, 
                               QListWidgetItem, QComboBox, QDialog, QLineEdit, QMessageBox,
                               QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize, QSettings, QThread, Signal, QTimer
from PySide6.QtGui import QIcon, QFont, QColor

DASHBOARD_LANGS = {
    'TR': {
        'logo': "☁️ MySaaS Workspace", 'menu_title': "SUNUCULARIM",
        'status_online': "🟢 Çevrimiçi", 'status_offline': "⚫ Çevrimdışı", 'logout_tip': "Çıkış Yap",
        'theme_dark': "🌙 Koyu Tema", 'theme_light': "☀️ Açık Tema",
        'select_title': "Çalışma Modelinizi Seçin", 'select_sub': "İhtiyaçlarınıza en uygun kullanım türünü belirleyerek başlayın.",
        'std_card_title': "Standart Kullanıcı", 'std_card_desc': "Bireysel kullanım için temel özellikler ve 1 sunucu hakkı.", 'btn_continue': "Ücretsiz Devam Et",
        'ent_card_title': "Enterprise (Premium)", 'ent_card_desc': "Ekipler ve şirketler için sınırsız erişim ve gelişmiş özellikler.", 'btn_examine': "Paketi İncele",
        'welcome_title': "MySaaS'a Hoş Geldiniz!", 'welcome_sub': "Çalışmaya başlamak için aşağıdaki seçeneklerden birini seçin.",
        'card_create_title': "Sunucu Oluştur", 'card_create_desc': "Kendi topluluğunuzu veya özel çalışma alanınızı kurun.", 'card_create_btn': "Oluştur",
        'card_join_title': "Sunucuya Katıl", 'card_join_desc': "Elinizdeki davet bağlantısı ile mevcut bir sunucuya katılın.", 'card_join_btn': "Katıl",
        'card_friend_title': "Arkadaş Ekle", 'card_friend_desc': "Arkadaşlarınızı ekleyerek anında direkt mesajlaşmaya başlayın.", 'card_friend_btn': "Ekle",
        'ent_pay_title': "Enterprise Paket İçeriği", 'ent_pay_price': "$9.99 / Aylık",
        'ent_f1': "★ Sınırsız Sunucu ve Çalışma Panosu", 'ent_f2': "★ Gelişmiş Görüntülü Arama & Sesli Sohbet",
        'ent_f3': "★ Sınırsız Dosya Yükleme Kapasitesi", 'ent_f4': "★ 7/24 Öncelikli Teknik Destek",
        'btn_pay': "💳 Ödeme Yap", 'btn_back': "⬅ Geri Dön",
        'dlg_join_title': "Bir Sunucuya Katıl", 'dlg_join_sub': "Arkadaşınızdan aldığınız davet kodunu veya bağlantısını aşağıya girin.",
        'dlg_join_ph': "Davet Kodu veya URL", 'dlg_btn_cancel': "İptal",
        'dlg_create_title': "Sunucu Oluştur", 'dlg_create_sub': "Yeni çalışma alanınıza bir isim verin ve ekibinizi toplamaya başlayın.",
        'dlg_create_ph': "Sunucu Adı (Örn: Proje X Ekibi)", 'dlg_btn_create': "Sunucuyu Kur",
        'search_title': "Arkadaş Bul & Ekle", 'search_sub': "Kullanıcı adı veya e-posta adresi ile arkadaşlarınızı arayın.",
        'search_ph': "Kullanıcı Adı veya E-posta...", 'search_no_result': "Kullanıcı bulunamadı.", 'search_btn_add': "Ekle", 'search_btn_close': "Kapat",
        'err_invalid_invite': "Geçersiz veya süresi dolmuş bir davet kodu girdiniz!",
        'err_freemium_limit': "Ücretsiz planda maksimum sunucu limitinize (1) ulaştınız. Lütfen Enterprise pakete yükseltin.",
        'err_401': "Oturum süreniz dolmuş veya geçersiz (401). Lütfen tekrar giriş yapın."
    },
    'EN': {
        'logo': "☁️ MySaaS Workspace", 'menu_title': "MY SERVERS",
        'status_online': "🟢 Online", 'status_offline': "⚫ Offline", 'logout_tip': "Logout",
        'theme_dark': "🌙 Dark Mode", 'theme_light': "☀️ Light Mode",
        'select_title': "Choose Your Working Model", 'select_sub': "Start by selecting the plan that best fits your needs.",
        'std_card_title': "Standard User", 'std_card_desc': "Basic features for individual use and 1 server limit.", 'btn_continue': "Continue for Free",
        'ent_card_title': "Enterprise (Premium)", 'ent_card_desc': "Unlimited access and advanced features for teams and companies.", 'btn_examine': "View Package",
        'welcome_title': "Welcome to MySaaS!", 'welcome_sub': "Choose one of the options below to get started.",
        'card_create_title': "Create Server", 'card_create_desc': "Set up your own community or private workspace.", 'card_create_btn': "Create",
        'card_join_title': "Join Server", 'card_join_desc': "Join an existing server using an invite link.", 'card_join_btn': "Join",
        'card_friend_title': "Add Friend", 'card_friend_desc': "Add your friends to start direct messaging instantly.", 'card_friend_btn': "Add Friend",
        'ent_pay_title': "Enterprise Package Details", 'ent_pay_price': "$9.99 / Month",
        'ent_f1': "★ Unlimited Servers and Workspaces", 'ent_f2': "★ Advanced Video & Voice Chat",
        'ent_f3': "★ Unlimited File Upload Capacity", 'ent_f4': "★ 24/7 Priority Technical Support",
        'btn_pay': "💳 Make Payment", 'btn_back': "⬅ Go Back",
        'dlg_join_title': "Join a Server", 'dlg_join_sub': "Enter an invite code or link provided by your friend below.",
        'dlg_join_ph': "Invite Code or URL", 'dlg_btn_cancel': "Cancel",
        'dlg_create_title': "Create Server", 'dlg_create_sub': "Give your new workspace a name and start gathering your team.",
        'dlg_create_ph': "Server Name (e.g. Project X Team)", 'dlg_btn_create': "Create Server",
        'search_title': "Find & Add Friends", 'search_sub': "Search for friends using their username or email address.",
        'search_ph': "Username or Email...", 'search_no_result': "No users found.", 'search_btn_add': "Add", 'search_btn_close': "Close",
        'err_invalid_invite': "You have entered an invalid or expired invite code!",
        'err_freemium_limit': "You have reached your maximum server limit (1) on the free plan. Please upgrade.",
        'err_401': "Session expired or invalid (401). Please log in again."
    },
    'GER': {
        'logo': "☁️ MySaaS Workspace", 'menu_title': "MEINE SERVER",
        'status_online': "🟢 Online", 'status_offline': "⚫ Offline", 'logout_tip': "Abmelden",
        'theme_dark': "🌙 Dunkel", 'theme_light': "☀️ Hell",
        'select_title': "Wählen Sie Ihr Arbeitsmodell", 'select_sub': "Beginnen Sie mit der Auswahl des Plans.",
        'std_card_title': "Standardbenutzer", 'std_card_desc': "Grundlegende Funktionen für Einzelpersonen (1 Server-Limit).", 'btn_continue': "Kostenlos fortfahren",
        'ent_card_title': "Enterprise (Premium)", 'ent_card_desc': "Unbegrenzter Zugang und erweiterte Funktionen für Teams.", 'btn_examine': "Paket ansehen",
        'welcome_title': "Willkommen bei MySaaS!", 'welcome_sub': "Wählen Sie eine der untenstehenden Optionen, um zu beginnen.",
        'card_create_title': "Server erstellen", 'card_create_desc': "Richten Sie Ihre eigene Community oder Ihren Arbeitsbereich ein.", 'card_create_btn': "Erstellen",
        'card_join_title': "Server beitreten", 'card_join_desc': "Treten Sie einem Server mit einem Einladungslink bei.", 'card_join_btn': "Beitreten",
        'card_friend_title': "Freund hinzufügen", 'card_friend_desc': "Fügen Sie Freunde hinzu, um Direktnachrichten zu senden.", 'card_friend_btn': "Hinzufügen",
        'ent_pay_title': "Enterprise-Paket Details", 'ent_pay_price': "$9.99 / Monat",
        'ent_f1': "★ Unbegrenzte Server und Arbeitsbereiche", 'ent_f2': "★ Erweiterter Video- & Voice-Chat",
        'ent_f3': "★ Unbegrenzte Datei-Upload-Kapazität", 'ent_f4': "★ 24/7 Priority Technischer Support",
        'btn_pay': "💳 Bezahlen", 'btn_back': "⬅ Zurück",
        'dlg_join_title': "Einem Server beitreten", 'dlg_join_sub': "Geben Sie unten einen Einladungscode oder -link ein.",
        'dlg_join_ph': "Einladungscode oder URL", 'dlg_btn_cancel': "Abbrechen",
        'dlg_create_title': "Server erstellen", 'dlg_create_sub': "Geben Sie Ihrem neuen Arbeitsbereich einen Namen.",
        'dlg_create_ph': "Servername (z.B. Projekt X)", 'dlg_btn_create': "Server erstellen",
        'search_title': "Freunde finden & hinzufügen", 'search_sub': "Suchen Sie nach Freunden anhand ihres Benutzernamens oder E-Mail.",
        'search_ph': "Benutzername oder E-Mail...", 'search_no_result': "Keine Benutzer gefunden.", 'search_btn_add': "Hinzufügen", 'search_btn_close': "Schließen",
        'err_invalid_invite': "Sie haben einen ungültigen Einladungscode eingegeben!",
        'err_freemium_limit': "Sie haben das maximale Serverlimit erreicht. Bitte upgraden Sie auf Enterprise.",
        'err_401': "Sitzung abgelaufen oder ungültig (401). Bitte loggen Sie sich erneut ein."
    }
}

# ==========================================
# 401 HATASINI ÇÖZECEK YENİ API HEADER FONKSİYONU
# ==========================================
def get_api_headers():
    settings = QSettings("MySaaS", "DesktopClient")
    token = settings.value("auth_token", "")
    token_str = str(token).strip() if token else ""
    
    # --- RADAR (Terminalde Görünecek Hata Ayıklama Bilgisi) ---
    print("\n[API YETKİLENDİRME KONTROLÜ]")
    print(f"Sistemdeki Kayıtlı Token: '{token_str}'")

    if not token_str or token_str == "None":
        print("🚨 KRİTİK HATA: Token boş veya 'None' geldi!")
        print("ÇÖZÜM: C++ backendinizdeki '/api/auth/login' endpoint'iniz başarılı girişten sonra JSON içerisinde {'token': 'mock-jwt-token-X'} dönmüyor olabilir. Lütfen login JSON yanıtınızı kontrol edin.")
        return {"Authorization": ""}

    # Sizin dokümanınıza uygun olarak "Bearer" KELİMESİ EKLENMEDEN oluşturulur
    header_val = token_str
    if not header_val.startswith("mock-jwt-token-"):
        header_val = f"mock-jwt-token-{token_str}"

    print(f"Sunucuya Giden Header -> Authorization: {header_val}\n")
    
    # NOT: Eğer C++ tarafınız 'Bearer ' kelimesini şart koşuyorsa, 
    # üstteki kodu silip doğrudan return {"Authorization": f"Bearer {header_val}"} yapabilirsiniz.
    return {"Authorization": header_val}


# ==========================================
# C++ API İŞ PARÇACIKLARI (ARKA PLAN)
# ==========================================
class ApiCreateServerThread(QThread):
    finished_signal = Signal(bool, str, str) 
    def __init__(self, server_name):
        super().__init__()
        self.server_name = server_name
    def run(self):
        try:
            url = "http://localhost:8080/api/servers" 
            payload = {"name": self.server_name}
            response = requests.post(url, json=payload, headers=get_api_headers(), timeout=5)
            
            if response.status_code in [200, 201]:
                self.finished_signal.emit(True, f"'{self.server_name}' başarıyla oluşturuldu!", "NONE")
            elif response.status_code == 401:
                self.finished_signal.emit(False, "", "UNAUTHORIZED") 
            elif response.status_code == 403: 
                self.finished_signal.emit(False, "", "LIMIT_EXCEEDED")
            else:
                self.finished_signal.emit(False, f"Hata Kodu: {response.status_code}", "GENERAL")
        except Exception as e:
            self.finished_signal.emit(False, f"Sunucuya ulaşılamadı. ({e})", "GENERAL")

class ApiFetchMyServersThread(QThread):
    finished_signal = Signal(bool, list, str) 
    def run(self):
        try:
            url = "http://localhost:8080/api/servers" 
            response = requests.get(url, headers=get_api_headers(), timeout=5)
            if response.status_code == 200:
                self.finished_signal.emit(True, response.json(), "NONE") 
            elif response.status_code == 401:
                self.finished_signal.emit(False, [], "UNAUTHORIZED")
            else:
                self.finished_signal.emit(False, [], "GENERAL")
        except:
            self.finished_signal.emit(False, [], "GENERAL")

class ApiJoinServerThread(QThread):
    finished_signal = Signal(bool, str, str)
    def __init__(self, invite_code):
        super().__init__()
        self.invite_code = invite_code
    def run(self):
        try:
            url = "http://localhost:8080/api/servers/join" 
            payload = {"invite_code": self.invite_code}
            response = requests.post(url, json=payload, headers=get_api_headers(), timeout=5)
            if response.status_code in [200, 201]:
                self.finished_signal.emit(True, "Sunucuya başarıyla katıldınız!", "NONE")
            elif response.status_code == 401:
                self.finished_signal.emit(False, "", "UNAUTHORIZED")
            else:
                self.finished_signal.emit(False, "Geçersiz veya süresi dolmuş davet kodu!", "INVALID")
        except:
            self.finished_signal.emit(False, "Sunucuya ulaşılamadı.", "GENERAL")

class ApiSearchUsersThread(QThread):
    finished_signal = Signal(bool, list)
    def __init__(self, search_query):
        super().__init__()
        self.search_query = search_query
    def run(self):
        try:
            if not self.search_query:
                self.finished_signal.emit(True, [])
                return
            url = f"http://localhost:8080/api/users/search?q={self.search_query}" 
            response = requests.get(url, headers=get_api_headers(), timeout=5)
            if response.status_code == 200: self.finished_signal.emit(True, response.json())
            else: self.finished_signal.emit(False, [])
        except:
            self.finished_signal.emit(False, [])

class ApiAddFriendThread(QThread):
    finished_signal = Signal(bool, str)
    def __init__(self, target_user_id):
        super().__init__()
        self.target_user_id = target_user_id
    def run(self):
        try:
            url = "http://localhost:8080/api/friends/add" 
            payload = {"friend_id": self.target_user_id}
            response = requests.post(url, json=payload, headers=get_api_headers(), timeout=5)
            if response.status_code == 200: self.finished_signal.emit(True, "İstek gönderildi.")
            else: self.finished_signal.emit(False, f"Reddedildi ({response.status_code})")
        except:
            self.finished_signal.emit(False, "Bağlantı hatası.")


# ==========================================
# ORTAK INPUT POP-UP (Sunucu Oluşturma ve Katılma İçin)
# ==========================================
class CustomDialog(QDialog):
    def __init__(self, parent, is_dark_mode, title, sub_text, ph_text, btn_ok_text, btn_cancel_text):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(480, 260) 
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint) 
        self.setAttribute(Qt.WA_TranslucentBackground) 

        self.bg_frame = QFrame(self)
        self.bg_frame.setGeometry(0, 0, 480, 260)
        self.bg_frame.setObjectName("dialog_bg")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25); shadow.setXOffset(0); shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 180 if is_dark_mode else 80)) 
        self.bg_frame.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.bg_frame); layout.setContentsMargins(35, 30, 35, 30); layout.setSpacing(15)
        lbl_title = QLabel(title); lbl_title.setObjectName("dialog_title"); lbl_title.setAlignment(Qt.AlignCenter)
        lbl_sub = QLabel(sub_text); lbl_sub.setObjectName("dialog_sub"); lbl_sub.setAlignment(Qt.AlignCenter); lbl_sub.setWordWrap(True)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(ph_text)
        self.input_field.setMinimumHeight(45) 

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn_layout.addStretch() 
        
        btn_cancel = QPushButton(btn_cancel_text)
        btn_cancel.setObjectName("dialog_btn_cancel")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.setFixedSize(100, 42) 
        btn_cancel.clicked.connect(self.reject) 
        
        btn_ok = QPushButton(btn_ok_text)
        btn_ok.setObjectName("dialog_btn_ok")
        btn_ok.setCursor(Qt.PointingHandCursor)
        btn_ok.setFixedSize(140, 42) 
        btn_ok.clicked.connect(self.accept) 
        
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(btn_ok)

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_sub)
        layout.addSpacing(5)
        layout.addWidget(self.input_field)
        layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.apply_theme(is_dark_mode)

    def apply_theme(self, is_dark_mode):
        if is_dark_mode:
            self.bg_frame.setStyleSheet("""
                QFrame#dialog_bg { background-color: #2b2d31; border-radius: 12px; border: 1px solid #5865f2; }
                QLabel#dialog_title { color: #ffffff; font-size: 22px; font-weight: 800; }
                QLabel#dialog_sub { color: #b5bac1; font-size: 14px; }
                QLineEdit { background-color: #1e1f22; border: 1px solid #444; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #ffffff; }
                QLineEdit:focus { border: 1px solid #5865f2; }
                QPushButton#dialog_btn_cancel { background-color: transparent; color: #f0f2f5; font-size: 14px; font-weight: bold; border-radius: 6px; border: none; }
                QPushButton#dialog_btn_cancel:hover { text-decoration: underline; }
                QPushButton#dialog_btn_ok { background-color: #5865f2; color: white; font-size: 14px; font-weight: bold; border-radius: 6px; border: none; }
                QPushButton#dialog_btn_ok:hover { background-color: #4752c4; }
            """)
        else:
            self.bg_frame.setStyleSheet("""
                QFrame#dialog_bg { background-color: #ffffff; border-radius: 12px; border: 1px solid #1877f2; }
                QLabel#dialog_title { color: #060607; font-size: 22px; font-weight: 800; }
                QLabel#dialog_sub { color: #4e5058; font-size: 14px; }
                QLineEdit { background-color: #f2f3f5; border: 1px solid #ccc; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #060607; }
                QLineEdit:focus { border: 1px solid #1877f2; background-color: #ffffff; }
                QPushButton#dialog_btn_cancel { background-color: transparent; color: #4e5058; font-size: 14px; font-weight: bold; border-radius: 6px; border: none; }
                QPushButton#dialog_btn_cancel:hover { text-decoration: underline; }
                QPushButton#dialog_btn_ok { background-color: #1877f2; color: white; font-size: 14px; font-weight: bold; border-radius: 6px; border: none; }
                QPushButton#dialog_btn_ok:hover { background-color: #166fe5; }
            """)
            
    def get_input_text(self): return self.input_field.text().strip()


# ==========================================
# DİNAMİK ARKADAŞ ARAMA POP-UP'I
# ==========================================
class AddFriendDialog(QDialog):
    def __init__(self, parent, is_dark_mode, lang_dict):
        super().__init__(parent)
        self.lang = lang_dict
        self.is_dark_mode = is_dark_mode
        self.setWindowTitle(self.lang['search_title'])
        self.setFixedSize(500, 500) 
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint) 
        self.setAttribute(Qt.WA_TranslucentBackground) 

        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)

        self.setup_ui()
        self.apply_theme(self.is_dark_mode)

    def setup_ui(self):
        self.bg_frame = QFrame(self)
        self.bg_frame.setGeometry(0, 0, 500, 500)
        self.bg_frame.setObjectName("dialog_bg")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25); shadow.setXOffset(0); shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 180 if self.is_dark_mode else 80))
        self.bg_frame.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.bg_frame); layout.setContentsMargins(30, 30, 30, 30); layout.setSpacing(15)

        lbl_title = QLabel(self.lang['search_title']); lbl_title.setObjectName("dialog_title"); lbl_title.setAlignment(Qt.AlignCenter)
        lbl_sub = QLabel(self.lang['search_sub']); lbl_sub.setObjectName("dialog_sub"); lbl_sub.setAlignment(Qt.AlignCenter); lbl_sub.setWordWrap(True)

        self.search_input = QLineEdit(); self.search_input.setPlaceholderText(self.lang['search_ph'])
        self.search_input.setMinimumHeight(45)
        self.search_input.textChanged.connect(self.on_text_changed)

        self.result_list = QListWidget(); self.result_list.setObjectName("result_list")
        self.result_list.setSelectionMode(QListWidget.NoSelection) 

        btn_close = QPushButton(self.lang['search_btn_close']); btn_close.setObjectName("dialog_btn_cancel")
        btn_close.setFixedSize(120, 40)
        btn_close.setCursor(Qt.PointingHandCursor); btn_close.clicked.connect(self.reject) 

        layout.addWidget(lbl_title); layout.addWidget(lbl_sub); layout.addSpacing(10)
        layout.addWidget(self.search_input); layout.addWidget(self.result_list); layout.addWidget(btn_close, alignment=Qt.AlignCenter)

    def on_text_changed(self, text):
        self.search_timer.start(500) 

    def perform_search(self):
        query = self.search_input.text().strip()
        self.result_list.clear()

        if not query: return
            
        item = QListWidgetItem("Aranıyor...")
        item.setTextAlignment(Qt.AlignCenter)
        self.result_list.addItem(item)
        
        self.search_thread = ApiSearchUsersThread(query)
        self.search_thread.finished_signal.connect(self.on_search_finished)
        self.search_thread.start()

    def on_search_finished(self, success, user_list):
        self.result_list.clear()
        
        if success and isinstance(user_list, list):
            if len(user_list) == 0:
                item = QListWidgetItem(self.lang['search_no_result'])
                item.setTextAlignment(Qt.AlignCenter)
                self.result_list.addItem(item)
            else:
                for user in user_list:
                    self.add_user_row(user)
        else:
            item = QListWidgetItem("Bağlantı hatası veya geçersiz sorgu.")
            item.setTextAlignment(Qt.AlignCenter)
            self.result_list.addItem(item)

    def add_user_row(self, user):
        item = QListWidgetItem(self.result_list)
        item.setSizeHint(QSize(0, 60)) 
        row_widget = QWidget(); row_layout = QHBoxLayout(row_widget); row_layout.setContentsMargins(10, 5, 10, 5)
        
        lbl_avatar = QLabel("👤"); lbl_avatar.setStyleSheet("font-size: 24px;")
        
        info_layout = QVBoxLayout()
        lbl_name = QLabel(user.get('username', 'Bilinmeyen Kullanıcı')); lbl_name.setStyleSheet("font-weight: bold; font-size: 14px;")
        lbl_email = QLabel(user.get('email', '')); lbl_email.setObjectName("row_email") 
        info_layout.addWidget(lbl_name); info_layout.addWidget(lbl_email); info_layout.setAlignment(Qt.AlignVCenter)
        
        btn_add = QPushButton(self.lang['search_btn_add'])
        btn_add.setObjectName("dialog_btn_ok") 
        btn_add.setCursor(Qt.PointingHandCursor); btn_add.setFixedSize(80, 35)
        btn_add.clicked.connect(lambda _, u=user: self.send_friend_request(u))
        
        row_layout.addWidget(lbl_avatar); row_layout.addLayout(info_layout); row_layout.addStretch(); row_layout.addWidget(btn_add)
        self.result_list.setItemWidget(item, row_widget)

    def send_friend_request(self, user):
        target_id = str(user.get('id', ''))
        self.add_req_thread = ApiAddFriendThread(target_id)
        self.add_req_thread.finished_signal.connect(lambda s, m: self.on_request_finished(s, m, user))
        self.add_req_thread.start()
        
    def on_request_finished(self, success, msg, user):
        if success:
            QMessageBox.information(self, "Başarılı", f"@{user.get('username', '')} kullanıcısına istek gönderildi!")
            self.accept()
        else:
            QMessageBox.warning(self, "Hata", msg)

    def apply_theme(self, is_dark_mode):
        if is_dark_mode:
            self.bg_frame.setStyleSheet("""
                QFrame#dialog_bg { background-color: #313338; border-radius: 12px; border: 1px solid #5865f2; }
                QLabel#dialog_title { color: #ffffff; font-size: 20px; font-weight: 800; }
                QLabel#dialog_sub { color: #b5bac1; font-size: 13px; }
                QLineEdit { background-color: #1e1f22; border: 1px solid #444; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #ffffff; }
                QLineEdit:focus { border: 1px solid #5865f2; }
                QListWidget#result_list { background-color: transparent; border: none; outline: none; color: #949ba4;}
                QListWidget#result_list::item { background-color: #1e1f22; border-radius: 8px; margin-bottom: 5px; }
                QListWidget#result_list::item:hover { background-color: #35393f; }
                QLabel#row_email { color: #949ba4; font-size: 11px; }
                QPushButton#dialog_btn_cancel { background-color: transparent; color: #f0f2f5; font-size: 14px; font-weight: bold; border-radius: 6px; padding: 10px; border: 1px solid #444; }
                QPushButton#dialog_btn_cancel:hover { background-color: #444; }
                QPushButton#dialog_btn_ok { background-color: #5865f2; color: white; font-size: 13px; font-weight: bold; border-radius: 6px; padding: 8px; border: none; }
                QPushButton#dialog_btn_ok:hover { background-color: #4752c4; }
            """)
        else:
            self.bg_frame.setStyleSheet("""
                QFrame#dialog_bg { background-color: #ffffff; border-radius: 12px; border: 1px solid #1877f2; }
                QLabel#dialog_title { color: #060607; font-size: 20px; font-weight: 800; }
                QLabel#dialog_sub { color: #4e5058; font-size: 13px; }
                QLineEdit { background-color: #f2f3f5; border: 1px solid #ccc; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #060607; }
                QLineEdit:focus { border: 1px solid #1877f2; background-color: #ffffff; }
                QListWidget#result_list { background-color: transparent; border: none; outline: none; color: #5c5e66;}
                QListWidget#result_list::item { background-color: #f8f9fa; border: 1px solid #e3e5e8; border-radius: 8px; margin-bottom: 5px; }
                QListWidget#result_list::item:hover { background-color: #f2f3f5; }
                QLabel#row_email { color: #5c5e66; font-size: 11px; }
                QPushButton#dialog_btn_cancel { background-color: transparent; color: #4e5058; font-size: 14px; font-weight: bold; border-radius: 6px; padding: 10px; border: 1px solid #ccc; }
                QPushButton#dialog_btn_cancel:hover { background-color: #e3e5e8; }
                QPushButton#dialog_btn_ok { background-color: #1877f2; color: white; font-size: 13px; font-weight: bold; border-radius: 6px; padding: 8px; border: none; }
                QPushButton#dialog_btn_ok:hover { background-color: #166fe5; }
            """)


# ==========================================
# ANA EKRAN (DASHBOARD VIEW)
# ==========================================
class DashboardView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.settings = QSettings("MySaaS", "DesktopClient")
        self.is_dark_mode = self.settings.value("is_dark_mode", False, type=bool)
        self.current_lang = self.settings.value("language", "TR")
        self.is_online = True 
        
        self.setup_ui()
        self.sync_settings()
        self.fetch_my_servers()

    def set_status(self, online_state: bool):
        self.is_online = online_state
        self.update_texts() 
        self.apply_theme()  

    def sync_settings(self):
        self.is_dark_mode = self.settings.value("is_dark_mode", False, type=bool)
        self.current_lang = self.settings.value("language", "TR")
        self.apply_theme()
        self.update_texts()
        self.lang_cb.blockSignals(True)
        self.lang_cb.setCurrentText(self.current_lang)
        self.lang_cb.blockSignals(False)

    def fetch_my_servers(self):
        self.server_list.clear()
        self.servers_thread = ApiFetchMyServersThread()
        self.servers_thread.finished_signal.connect(self.on_servers_fetched)
        self.servers_thread.start()

    def on_servers_fetched(self, success, servers, error_type):
        self.server_list.clear()
        if success and isinstance(servers, list):
            for srv in servers:
                name = srv.get("name", "Bilinmeyen Sunucu")
                item = QListWidgetItem(f"🏢 {name}")
                item.setFont(QFont("Segoe UI", 11))
                self.server_list.addItem(item)
        elif error_type == "UNAUTHORIZED":
            t = DASHBOARD_LANGS[self.current_lang]
            QMessageBox.critical(self, "Oturum Hatası", t['err_401'])
            self.main_window.show_login()
        else:
            item = QListWidgetItem("Bağlantı Bekleniyor...")
            item.setFont(QFont("Segoe UI", 10))
            self.server_list.addItem(item)

    def setup_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 15)
        sidebar_layout.setSpacing(15)

        self.lbl_logo = QLabel(); self.lbl_logo.setObjectName("logo_text"); sidebar_layout.addWidget(self.lbl_logo); sidebar_layout.addSpacing(10)
        self.lbl_menu_title = QLabel(); self.lbl_menu_title.setObjectName("menu_title"); sidebar_layout.addWidget(self.lbl_menu_title)

        self.server_list = QListWidget(); self.server_list.setObjectName("server_list"); sidebar_layout.addWidget(self.server_list)

        self.profile_box = QFrame(); self.profile_box.setObjectName("profile_box")
        profile_layout = QHBoxLayout(self.profile_box); profile_layout.setContentsMargins(10, 10, 10, 10)
        
        self.lbl_avatar = QLabel("👤"); self.lbl_avatar.setStyleSheet("font-size: 24px;")
        user_info_layout = QVBoxLayout()
        self.lbl_username = QLabel("Kullanıcı Adı"); self.lbl_username.setObjectName("username_lbl")
        self.lbl_status = QLabel(); self.lbl_status.setObjectName("status_lbl")
        user_info_layout.addWidget(self.lbl_username); user_info_layout.addWidget(self.lbl_status)
        
        self.btn_logout = QPushButton("🚪"); self.btn_logout.setObjectName("logout_btn"); self.btn_logout.clicked.connect(self.main_window.show_login); self.btn_logout.setFixedSize(30, 30)

        profile_layout.addWidget(self.lbl_avatar); profile_layout.addLayout(user_info_layout); profile_layout.addStretch(); profile_layout.addWidget(self.btn_logout)
        sidebar_layout.addWidget(self.profile_box)

        self.content_area = QFrame(); self.content_area.setObjectName("content_area")
        content_layout = QVBoxLayout(self.content_area); content_layout.setContentsMargins(0, 0, 0, 0); content_layout.setSpacing(0)

        self.header = QFrame(); self.header.setObjectName("header"); self.header.setFixedHeight(65)
        header_layout = QHBoxLayout(self.header); header_layout.setContentsMargins(20, 0, 20, 0)
        
        self.lbl_channel_name = QLabel(); self.lbl_channel_name.setObjectName("channel_name")
        self.btn_theme = QPushButton(); self.btn_theme.setObjectName("theme_btn"); self.btn_theme.setCursor(Qt.PointingHandCursor); self.btn_theme.clicked.connect(self.toggle_theme)

        self.lang_cb = QComboBox(); self.lang_cb.setObjectName("lang_cb"); self.lang_cb.setCursor(Qt.PointingHandCursor)
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        tr_path = os.path.join(base_dir, 'assets', 'tr.png').replace('\\', '/')
        en_path = os.path.join(base_dir, 'assets', 'en.png').replace('\\', '/')
        ger_path = os.path.join(base_dir, 'assets', 'ger.png').replace('\\', '/')
        self.lang_cb.addItem(QIcon(tr_path), "TR"); self.lang_cb.addItem(QIcon(en_path), "EN"); self.lang_cb.addItem(QIcon(ger_path), "GER")
        self.lang_cb.setIconSize(QSize(20, 15)); self.lang_cb.currentTextChanged.connect(self.change_language)
        
        header_layout.addWidget(self.lbl_channel_name); header_layout.addStretch(); header_layout.addWidget(self.btn_theme); header_layout.addWidget(self.lang_cb)
        content_layout.addWidget(self.header)

        self.stacked_widget = QStackedWidget()
        self.page_selection = self.create_selection_page()
        self.page_standard = self.create_standard_page()
        self.page_enterprise = self.create_enterprise_page()

        self.stacked_widget.addWidget(self.page_selection); self.stacked_widget.addWidget(self.page_standard); self.stacked_widget.addWidget(self.page_enterprise)
        
        has_completed_onboarding = self.settings.value("has_completed_onboarding", False, type=bool)
        if has_completed_onboarding: self.stacked_widget.setCurrentWidget(self.page_standard)
        else: self.stacked_widget.setCurrentWidget(self.page_selection) 
        
        content_layout.addWidget(self.stacked_widget)
        self.main_layout.addWidget(self.sidebar); self.main_layout.addWidget(self.content_area)

    def complete_onboarding(self):
        self.settings.setValue("has_completed_onboarding", True); self.stacked_widget.setCurrentWidget(self.page_standard)

    def create_selection_page(self):
        page = QWidget(); layout = QVBoxLayout(page); layout.setAlignment(Qt.AlignCenter); layout.setSpacing(40)
        title_box = QWidget(); title_layout = QVBoxLayout(title_box); title_layout.setAlignment(Qt.AlignCenter)
        self.lbl_sel_title = QLabel(); self.lbl_sel_title.setObjectName("welcome_title"); self.lbl_sel_title.setAlignment(Qt.AlignCenter)
        self.lbl_sel_sub = QLabel(); self.lbl_sel_sub.setObjectName("welcome_sub"); self.lbl_sel_sub.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(self.lbl_sel_title); title_layout.addWidget(self.lbl_sel_sub)

        cards_layout = QHBoxLayout(); cards_layout.setSpacing(30); cards_layout.setAlignment(Qt.AlignCenter)
        self.card_std, self.lbl_std_title, self.lbl_std_desc, self.btn_std = self.create_action_card("👤")
        self.btn_std.setObjectName("primary_btn"); self.btn_std.clicked.connect(self.complete_onboarding)

        self.card_ent, self.lbl_ent_title, self.lbl_ent_desc, self.btn_ent = self.create_action_card("🚀")
        self.btn_ent.setObjectName("success_btn"); self.card_ent.setObjectName("enterprise_card"); self.btn_ent.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.page_enterprise))

        cards_layout.addWidget(self.card_std); cards_layout.addWidget(self.card_ent)
        layout.addStretch(); layout.addWidget(title_box); layout.addLayout(cards_layout); layout.addStretch()
        return page

    def create_standard_page(self):
        page = QWidget(); layout = QVBoxLayout(page); layout.setAlignment(Qt.AlignCenter); layout.setSpacing(20) 
        top_layout = QVBoxLayout(); top_layout.setAlignment(Qt.AlignCenter)
        self.lbl_welcome_title = QLabel(); self.lbl_welcome_title.setObjectName("welcome_title"); self.lbl_welcome_title.setAlignment(Qt.AlignCenter)
        self.lbl_welcome_sub = QLabel(); self.lbl_welcome_sub.setObjectName("welcome_sub"); self.lbl_welcome_sub.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self.lbl_welcome_title); top_layout.addWidget(self.lbl_welcome_sub)

        cards_layout = QHBoxLayout(); cards_layout.setSpacing(25); cards_layout.setAlignment(Qt.AlignCenter)
        self.card_create, self.lbl_c_title, self.lbl_c_desc, self.btn_create = self.create_action_card("➕")
        self.card_join, self.lbl_j_title, self.lbl_j_desc, self.btn_join = self.create_action_card("🔗")
        self.card_friend, self.lbl_f_title, self.lbl_f_desc, self.btn_friend = self.create_action_card("👥")
        
        self.btn_create.clicked.connect(self.show_create_dialog)
        self.btn_join.clicked.connect(self.show_join_dialog)
        self.btn_friend.clicked.connect(self.show_add_friend_dialog)
        
        cards_layout.addWidget(self.card_create); cards_layout.addWidget(self.card_join); cards_layout.addWidget(self.card_friend)
        layout.addStretch(); layout.addLayout(top_layout); layout.addSpacing(20); layout.addLayout(cards_layout); layout.addStretch()
        return page

    def create_enterprise_page(self):
        page = QWidget(); layout = QVBoxLayout(page); layout.setAlignment(Qt.AlignCenter)
        self.payment_box = QFrame(); self.payment_box.setObjectName("payment_box"); self.payment_box.setFixedSize(450, 450)
        box_layout = QVBoxLayout(self.payment_box); box_layout.setContentsMargins(40, 40, 40, 40); box_layout.setSpacing(15)

        self.lbl_pay_title = QLabel(); self.lbl_pay_title.setObjectName("pay_title"); self.lbl_pay_title.setAlignment(Qt.AlignCenter)
        self.lbl_pay_price = QLabel(); self.lbl_pay_price.setObjectName("pay_price"); self.lbl_pay_price.setAlignment(Qt.AlignCenter)
        self.lbl_pf1 = QLabel(); self.lbl_pf1.setObjectName("pay_item")
        self.lbl_pf2 = QLabel(); self.lbl_pf2.setObjectName("pay_item")
        self.lbl_pf3 = QLabel(); self.lbl_pf3.setObjectName("pay_item")
        self.lbl_pf4 = QLabel(); self.lbl_pf4.setObjectName("pay_item")

        self.btn_make_payment = QPushButton(); self.btn_make_payment.setObjectName("success_btn"); self.btn_make_payment.setCursor(Qt.PointingHandCursor)
        self.btn_make_payment.clicked.connect(lambda: webbrowser.open("https://sizin-odeme-linkiniz.com"))
        self.btn_back_from_ent = QPushButton(); self.btn_back_from_ent.setObjectName("text_btn"); self.btn_back_from_ent.setCursor(Qt.PointingHandCursor)
        self.btn_back_from_ent.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.page_selection))

        box_layout.addWidget(self.lbl_pay_title); box_layout.addWidget(self.lbl_pay_price); box_layout.addSpacing(15)
        box_layout.addWidget(self.lbl_pf1); box_layout.addWidget(self.lbl_pf2); box_layout.addWidget(self.lbl_pf3); box_layout.addWidget(self.lbl_pf4)
        box_layout.addStretch(); box_layout.addWidget(self.btn_make_payment); box_layout.addSpacing(5); box_layout.addWidget(self.btn_back_from_ent, alignment=Qt.AlignCenter)
        layout.addWidget(self.payment_box, alignment=Qt.AlignCenter)
        return page

    # ==================== POP-UP GÖSTERME / API İŞLEMLERİ ====================
    def show_create_dialog(self):
        t = DASHBOARD_LANGS[self.current_lang]
        dialog = CustomDialog(
            self, self.is_dark_mode, 
            t['dlg_create_title'], t['dlg_create_sub'], t['dlg_create_ph'], 
            t['dlg_btn_create'], t['dlg_btn_cancel']
        )
        if dialog.exec() == QDialog.Accepted:
            server_name = dialog.get_input_text()
            if server_name:
                self.create_thread = ApiCreateServerThread(server_name)
                self.create_thread.finished_signal.connect(self.on_create_finished)
                self.create_thread.start()
            else:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir sunucu adı girin.")
                
    def on_create_finished(self, success, msg, error_type):
        t = DASHBOARD_LANGS[self.current_lang]
        if success:
            QMessageBox.information(self, "Başarılı", msg)
            self.fetch_my_servers() 
        else:
            if error_type == "LIMIT_EXCEEDED":
                QMessageBox.warning(self, "Limit Uyarısı", t['err_freemium_limit'])
            elif error_type == "UNAUTHORIZED":
                QMessageBox.critical(self, "Oturum Hatası", t['err_401'])
                self.main_window.show_login()
            else:
                QMessageBox.warning(self, "Hata", msg)

    def show_join_dialog(self):
        t = DASHBOARD_LANGS[self.current_lang]
        dialog = CustomDialog(
            self, self.is_dark_mode, 
            t['dlg_join_title'], t['dlg_join_sub'], t['dlg_join_ph'], 
            t['card_join_btn'], t['dlg_btn_cancel']
        )
        if dialog.exec() == QDialog.Accepted:
            invite_code = dialog.get_input_text()
            if invite_code:
                self.join_thread = ApiJoinServerThread(invite_code)
                self.join_thread.finished_signal.connect(self.on_join_finished)
                self.join_thread.start()
            else:
                QMessageBox.warning(self, "Uyarı", "Lütfen bir davet kodu girin.")

    def on_join_finished(self, success, msg, error_type):
        t = DASHBOARD_LANGS[self.current_lang]
        if success: 
            QMessageBox.information(self, "Başarılı", msg)
            self.fetch_my_servers() 
        else: 
            if error_type == "UNAUTHORIZED":
                QMessageBox.critical(self, "Oturum Hatası", t['err_401'])
                self.main_window.show_login()
            else:
                QMessageBox.warning(self, "Hata", t['err_invalid_invite']) 

    def show_add_friend_dialog(self):
        t = DASHBOARD_LANGS[self.current_lang]
        dialog = AddFriendDialog(self, self.is_dark_mode, t)
        dialog.exec() 

    def create_action_card(self, icon_emoji):
        card = QFrame(); card.setObjectName("action_card"); card.setFixedSize(260, 280) 
        layout = QVBoxLayout(card); layout.setAlignment(Qt.AlignCenter); layout.setContentsMargins(20, 30, 20, 20)
        lbl_icon = QLabel(icon_emoji); lbl_icon.setObjectName("card_icon"); lbl_icon.setAlignment(Qt.AlignCenter)
        lbl_title = QLabel(); lbl_title.setObjectName("card_title"); lbl_title.setAlignment(Qt.AlignCenter)
        lbl_desc = QLabel(); lbl_desc.setObjectName("card_desc"); lbl_desc.setAlignment(Qt.AlignCenter); lbl_desc.setWordWrap(True) 
        btn = QPushButton(); btn.setObjectName("primary_btn"); btn.setCursor(Qt.PointingHandCursor)
        layout.addWidget(lbl_icon); layout.addWidget(lbl_title); layout.addWidget(lbl_desc); layout.addStretch(); layout.addWidget(btn)
        return card, lbl_title, lbl_desc, btn

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.settings.setValue("is_dark_mode", self.is_dark_mode)
        self.apply_theme()
        self.update_texts()

    def change_language(self, lang_code):
        self.current_lang = lang_code
        self.settings.setValue("language", self.current_lang)
        self.update_texts()

    def update_texts(self):
        t = DASHBOARD_LANGS[self.current_lang]
        self.lbl_logo.setText(t['logo']); self.lbl_menu_title.setText(t['menu_title'])
        self.lbl_status.setText(t['status_online'] if self.is_online else t['status_offline'])
        self.btn_logout.setToolTip(t['logout_tip']); self.btn_theme.setText(t['theme_light'] if self.is_dark_mode else t['theme_dark'])
        self.lbl_sel_title.setText(t['select_title']); self.lbl_sel_sub.setText(t['select_sub'])
        self.lbl_std_title.setText(t['std_card_title']); self.lbl_std_desc.setText(t['std_card_desc']); self.btn_std.setText(t['btn_continue'])
        self.lbl_ent_title.setText(t['ent_card_title']); self.lbl_ent_desc.setText(t['ent_card_desc']); self.btn_ent.setText(t['btn_examine'])
        self.lbl_welcome_title.setText(t['welcome_title']); self.lbl_welcome_sub.setText(t['welcome_sub'])
        self.lbl_c_title.setText(t['card_create_title']); self.lbl_c_desc.setText(t['card_create_desc']); self.btn_create.setText(t['card_create_btn'])
        self.lbl_j_title.setText(t['card_join_title']); self.lbl_j_desc.setText(t['card_join_desc']); self.btn_join.setText(t['card_join_btn'])
        self.lbl_f_title.setText(t['card_friend_title']); self.lbl_f_desc.setText(t['card_friend_desc']); self.btn_friend.setText(t['card_friend_btn'])
        self.lbl_pay_title.setText(t['ent_pay_title']); self.lbl_pay_price.setText(t['ent_pay_price'])
        self.lbl_pf1.setText(t['ent_f1']); self.lbl_pf2.setText(t['ent_f2']); self.lbl_pf3.setText(t['ent_f3']); self.lbl_pf4.setText(t['ent_f4'])
        self.btn_make_payment.setText(t['btn_pay']); self.btn_back_from_ent.setText(t['btn_back'])

    def apply_theme(self):
        status_color = "#23a559" if self.is_online else "#80848e"
        if self.is_dark_mode:
            self.setStyleSheet(f"""
                QFrame#sidebar {{ background-color: #1e2124; border-right: 1px solid #282b30; }}
                QLabel#logo_text {{ color: #ffffff; font-size: 18px; font-weight: 800; }}
                QLabel#menu_title {{ color: #87909c; font-size: 11px; font-weight: bold; margin-top: 10px; }}
                QListWidget#server_list {{ background: transparent; border: none; outline: none; }}
                QListWidget#server_list::item {{ color: #949ba4; padding: 10px 15px; border-radius: 6px; margin-bottom: 2px;}}
                QListWidget#server_list::item:hover {{ background-color: #35393f; color: #dcddde; }}
                QListWidget#server_list::item:selected {{ background-color: #4752c4; color: #ffffff; font-weight: bold; }}
                QFrame#profile_box {{ background-color: #232428; border-radius: 8px; }}
                QLabel#username_lbl {{ color: #ffffff; font-weight: bold; font-size: 13px; }}
                QLabel#status_lbl {{ color: {status_color}; font-size: 11px; font-weight: bold; }}
                QPushButton#logout_btn {{ background: transparent; border: none; border-radius: 4px; }}
                QPushButton#logout_btn:hover {{ background-color: rgba(240, 71, 71, 0.2); }}
                QFrame#content_area {{ background-color: #313338; }}
                QFrame#header {{ background-color: #313338; border-bottom: 1px solid #282b30; }}
                QLabel#channel_name {{ color: #ffffff; font-size: 20px; font-weight: 800; }}
                QPushButton#theme_btn {{ background-color: #1e2124; color: #dcddde; border: 1px solid #444; border-radius: 6px; padding: 6px 12px; font-weight: bold; }}
                QPushButton#theme_btn:hover {{ background-color: #444; }}
                QComboBox#lang_cb {{ background-color: #1e2124; color: #dcddde; border-radius: 6px; padding: 6px 10px 6px 15px; font-weight: bold; border: 1px solid #444; }}
                QComboBox#lang_cb:hover {{ background-color: #444; }}
                QComboBox#lang_cb::drop-down {{ border: none; width: 25px; }} 
                QComboBox#lang_cb QAbstractItemView {{ background-color: #1e2328; color: #dcddde; border: 1px solid #444; border-radius: 6px; outline: none; padding: 4px; }}
                QComboBox#lang_cb QAbstractItemView::item:hover {{ background-color: #2a3038; color: #4da3ff; }}

                QLabel#welcome_title {{ color: #ffffff; font-size: 32px; font-weight: 900; }}
                QLabel#welcome_sub {{ color: #b5bac1; font-size: 16px; margin-bottom: 20px; }}
                QFrame#action_card {{ background-color: #2b2d31; border: 1px solid #1e1f22; border-radius: 12px; }}
                QFrame#action_card:hover {{ border: 1px solid #5865f2; background-color: #2e3035; }}
                QFrame#enterprise_card {{ border: 1px solid rgba(24,119,242,0.5); background-color: rgba(24,119,242,0.1); }}
                QFrame#enterprise_card:hover {{ border: 1px solid #1877f2; background-color: rgba(24,119,242,0.2); }}
                QLabel#card_icon {{ font-size: 48px; margin-bottom: 10px; }}
                QLabel#card_title {{ color: #ffffff; font-size: 18px; font-weight: bold; margin-bottom: 5px; }}
                QLabel#card_desc {{ color: #949ba4; font-size: 13px; line-height: 1.4; }}
                
                QPushButton#primary_btn {{ background-color: #5865f2; color: white; border-radius: 6px; padding: 12px; font-weight: bold; font-size: 14px; border: none; }}
                QPushButton#primary_btn:hover {{ background-color: #4752c4; }}
                QPushButton#success_btn {{ background-color: #23a559; color: white; border-radius: 6px; padding: 12px; font-weight: bold; font-size: 14px; border: none; }}
                QPushButton#success_btn:hover {{ background-color: #1b8546; }}
                QPushButton#text_btn {{ background: transparent; color: #949ba4; font-weight: bold; font-size: 13px; border: none; }}
                QPushButton#text_btn:hover {{ color: #ffffff; text-decoration: underline; }}
                QFrame#payment_box {{ background-color: #2b2d31; border: 1px solid #4da3ff; border-radius: 16px; }}
                QLabel#pay_title {{ color: #4da3ff; font-size: 22px; font-weight: bold; }}
                QLabel#pay_price {{ color: #ffffff; font-size: 36px; font-weight: 900; }}
                QLabel#pay_item {{ color: #dcddde; font-size: 15px; font-weight: 500; margin-bottom: 8px; }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame#sidebar {{ background-color: #f2f3f5; border-right: 1px solid #e3e5e8; }}
                QLabel#logo_text {{ color: #060607; font-size: 18px; font-weight: 800; }}
                QLabel#menu_title {{ color: #5c5e66; font-size: 11px; font-weight: bold; margin-top: 10px; }}
                QListWidget#server_list {{ background: transparent; border: none; outline: none; }}
                QListWidget#server_list::item {{ color: #4e5058; padding: 10px 15px; border-radius: 6px; margin-bottom: 2px;}}
                QListWidget#server_list::item:hover {{ background-color: #e3e5e8; color: #060607; }}
                QListWidget#server_list::item:selected {{ background-color: #1877f2; color: #ffffff; font-weight: bold; }}
                QFrame#profile_box {{ background-color: #e3e5e8; border-radius: 8px; }}
                QLabel#username_lbl {{ color: #060607; font-weight: bold; font-size: 13px; }}
                QLabel#status_lbl {{ color: {status_color}; font-size: 11px; font-weight: bold; }}
                QPushButton#logout_btn {{ background: transparent; border: none; border-radius: 4px; }}
                QPushButton#logout_btn:hover {{ background-color: rgba(240, 71, 71, 0.1); }}
                QFrame#content_area {{ background-color: #ffffff; }}
                QFrame#header {{ background-color: #ffffff; border-bottom: 1px solid #e3e5e8; }}
                QLabel#channel_name {{ color: #060607; font-size: 20px; font-weight: 800; }}
                QPushButton#theme_btn {{ background-color: #f2f3f5; color: #4e5058; border: 1px solid #ccc; border-radius: 6px; padding: 6px 12px; font-weight: bold; }}
                QPushButton#theme_btn:hover {{ background-color: #e3e5e8; }}
                QComboBox#lang_cb {{ background-color: #f2f3f5; color: #4e5058; border-radius: 6px; padding: 6px 10px 6px 15px; font-weight: bold; border: 1px solid #ccc; }}
                QComboBox#lang_cb:hover {{ background-color: #e3e5e8; }}
                QComboBox#lang_cb::drop-down {{ border: none; width: 25px; }} 
                QComboBox#lang_cb QAbstractItemView {{ background-color: #ffffff; color: #1c1e21; border: 1px solid #ccd0d5; border-radius: 6px; outline: none; padding: 4px; }}
                QComboBox#lang_cb QAbstractItemView::item:hover {{ background-color: #f0f2f5; color: #1877f2; }}

                QLabel#welcome_title {{ color: #060607; font-size: 32px; font-weight: 900; }}
                QLabel#welcome_sub {{ color: #4e5058; font-size: 16px; margin-bottom: 20px; }}
                QFrame#action_card {{ background-color: #ffffff; border: 1px solid #e3e5e8; border-radius: 12px; }}
                QFrame#action_card:hover {{ border: 1px solid #1877f2; background-color: #f8f9fa; }}
                QFrame#enterprise_card {{ border: 1px solid rgba(24,119,242,0.5); background-color: rgba(24,119,242,0.05); }}
                QFrame#enterprise_card:hover {{ border: 1px solid #1877f2; background-color: rgba(24,119,242,0.1); }}
                QLabel#card_icon {{ font-size: 48px; margin-bottom: 10px; }}
                QLabel#card_title {{ color: #060607; font-size: 18px; font-weight: bold; margin-bottom: 5px; }}
                QLabel#card_desc {{ color: #5c5e66; font-size: 13px; line-height: 1.4; }}
                QPushButton#primary_btn {{ background-color: #1877f2; color: white; border-radius: 6px; padding: 12px; font-weight: bold; font-size: 14px; border: none; }}
                QPushButton#primary_btn:hover {{ background-color: #166fe5; }}
                QPushButton#success_btn {{ background-color: #23a559; color: white; border-radius: 6px; padding: 12px; font-weight: bold; font-size: 14px; border: none; }}
                QPushButton#success_btn:hover {{ background-color: #1b8546; }}
                QPushButton#text_btn {{ background: transparent; color: #5c5e66; font-weight: bold; font-size: 13px; border: none; }}
                QPushButton#text_btn:hover {{ color: #1877f2; text-decoration: underline; }}
                QFrame#payment_box {{ background-color: #f8f9fa; border: 1px solid #1877f2; border-radius: 16px; }}
                QLabel#pay_title {{ color: #1877f2; font-size: 22px; font-weight: bold; }}
                QLabel#pay_price {{ color: #060607; font-size: 36px; font-weight: 900; }}
                QLabel#pay_item {{ color: #4e5058; font-size: 15px; font-weight: 500; margin-bottom: 8px; }}
            """)