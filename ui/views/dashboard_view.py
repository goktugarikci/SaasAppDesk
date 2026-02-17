# ui/views/dashboard_view.py
import os
import webbrowser
import requests
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QStackedWidget, QListWidget, 
                               QListWidgetItem, QComboBox, QDialog, QLineEdit, QMessageBox,
                               QGraphicsDropShadowEffect, QScrollArea)
from PySide6.QtCore import Qt, QSize, QSettings, QThread, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QFont, QColor, QPixmap

# YENİ: Dil dosyasını harici dosyadan çekiyoruz
from ui.resources.languages import DASHBOARD_LANGS

def get_api_headers():
    settings = QSettings("MySaaS", "DesktopClient")
    settings.sync()
    token = settings.value("auth_token")
    if token is None: return {"Authorization": ""}
    token_str = str(token).strip()
    if not token_str or token_str == "None": return {"Authorization": ""}
    return {"Authorization": token_str}

# ... (API THREADLERİ AYNI KALACAK, SADECE CSS KISMI DEĞİŞTİ) ...
# (Kodun çok uzun olmaması için API Thread'lerini yukarıdaki gibi varsayıyorum, 
#  fakat CSS'i aşağıda KOMPLE veriyorum, lütfen eskisiyle değiştirin)

# ==========================================
# GÜNCELLENMİŞ API THREADLERİ (BURAYI KOPYALAYIN)
# ==========================================
class ApiFetchProfileThread(QThread):
    finished_signal = Signal(bool, dict) 
    def run(self):
        try:
            response = requests.get("http://localhost:8080/api/users/me", headers=get_api_headers(), timeout=5)
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
            res_server = requests.post("http://localhost:8080/api/servers", json={"name": self.server_name}, headers=headers, timeout=5)
            
            if res_server.status_code not in [200, 201]:
                if res_server.status_code == 401: self.finished_signal.emit(False, "", "UNAUTHORIZED")
                elif res_server.status_code == 403: self.finished_signal.emit(False, "", "LIMIT_EXCEEDED")
                else: self.finished_signal.emit(False, f"Hata: {res_server.status_code}", "GENERAL")
                return
            
            # JSON GÜVENLİK KONTROLÜ
            server_id = None
            if res_server.text.strip():
                try:
                    server_data = res_server.json()
                    server_id = server_data.get("id") or server_data.get("server_id")
                except ValueError: pass

            if not server_id:
                self.finished_signal.emit(True, f"'{self.server_name}' oluşturuldu!", "NONE")
                return

            url_channel = f"http://localhost:8080/api/servers/{server_id}/channels"
            requests.post(url_channel, json={"name": "genel-sohbet", "type": 0}, headers=headers, timeout=3)
            res_kanban = requests.post(url_channel, json={"name": "Proje Panosu", "type": 3}, headers=headers, timeout=3)
            
            if res_kanban.status_code in [200, 201] and res_kanban.text.strip():
                try:
                    kanban_id = res_kanban.json().get("id") or res_kanban.json().get("channel_id")
                    if kanban_id:
                        url_lists = f"http://localhost:8080/api/boards/{kanban_id}/lists"
                        requests.post(url_lists, json={"title": "📋 Yapılacaklar"}, headers=headers, timeout=3)
                        requests.post(url_lists, json={"title": "⏳ Devam Edenler"}, headers=headers, timeout=3)
                        requests.post(url_lists, json={"title": "✅ Tamamlananlar"}, headers=headers, timeout=3)
                except ValueError: pass
                    
            self.finished_signal.emit(True, f"'{self.server_name}' çalışma alanı hazır!", "NONE")
        except Exception as e: self.finished_signal.emit(False, f"Bağlantı koptu: {e}", "GENERAL")

class ApiFetchMyServersThread(QThread):
    finished_signal = Signal(bool, list, str) 
    def run(self):
        try:
            response = requests.get("http://localhost:8080/api/servers", headers=get_api_headers(), timeout=5)
            if response.status_code == 200: self.finished_signal.emit(True, response.json(), "NONE") 
            elif response.status_code == 401: self.finished_signal.emit(False, [], "UNAUTHORIZED")
            else: self.finished_signal.emit(False, [], "GENERAL")
        except: self.finished_signal.emit(False, [], "GENERAL")

class ApiJoinServerThread(QThread):
    finished_signal = Signal(bool, str, str)
    def __init__(self, invite_code):
        super().__init__(); self.invite_code = invite_code
    def run(self):
        try:
            response = requests.post("http://localhost:8080/api/servers/join", json={"invite_code": self.invite_code}, headers=get_api_headers(), timeout=5)
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
            response = requests.get(f"http://localhost:8080/api/users/search?q={self.search_query}", headers=get_api_headers(), timeout=5)
            if response.status_code == 200: self.finished_signal.emit(True, response.json())
            else: self.finished_signal.emit(False, [])
        except: self.finished_signal.emit(False, [])

class ApiAddFriendThread(QThread):
    finished_signal = Signal(bool, str)
    def __init__(self, target_user_id):
        super().__init__(); self.target_user_id = target_user_id
    def run(self):
        try:
            response = requests.post("http://localhost:8080/api/friends/add", json={"friend_id": self.target_user_id}, headers=get_api_headers(), timeout=5)
            if response.status_code == 200: self.finished_signal.emit(True, "İstek gönderildi.")
            else: self.finished_signal.emit(False, f"Reddedildi ({response.status_code})")
        except: self.finished_signal.emit(False, "Bağlantı hatası.")

# ==========================================
# DIALOG VE DASHBOARD SINIFLARI (AYNI, SADECE CSS VE IMPORT GÜNCELLENDİ)
# ==========================================
# (Dialog sınıfları aynı kalıyor, DashboardView apply_theme fonksiyonu aşağıda kökten değiştirildi)

class CustomDialog(QDialog):
    def __init__(self, parent, is_dark_mode, title, sub_text, ph_text, btn_ok_text, btn_cancel_text):
        super().__init__(parent); self.setWindowTitle(title); self.setFixedSize(480, 260) 
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint); self.setAttribute(Qt.WA_TranslucentBackground) 
        self.bg_frame = QFrame(self); self.bg_frame.setGeometry(0, 0, 480, 260); self.bg_frame.setObjectName("dialog_bg")
        shadow = QGraphicsDropShadowEffect(self); shadow.setBlurRadius(25); shadow.setXOffset(0); shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 180 if is_dark_mode else 80)); self.bg_frame.setGraphicsEffect(shadow)
        layout = QVBoxLayout(self.bg_frame); layout.setContentsMargins(35, 30, 35, 30); layout.setSpacing(15)
        lbl_title = QLabel(title); lbl_title.setObjectName("dialog_title"); lbl_title.setAlignment(Qt.AlignCenter)
        lbl_sub = QLabel(sub_text); lbl_sub.setObjectName("dialog_sub"); lbl_sub.setAlignment(Qt.AlignCenter); lbl_sub.setWordWrap(True)
        self.input_field = QLineEdit(); self.input_field.setPlaceholderText(ph_text); self.input_field.setMinimumHeight(45) 
        btn_layout = QHBoxLayout(); btn_layout.setSpacing(15); btn_layout.addStretch() 
        btn_cancel = QPushButton(btn_cancel_text); btn_cancel.setObjectName("dialog_btn_cancel"); btn_cancel.setFixedSize(100, 42); btn_cancel.clicked.connect(self.reject) 
        btn_ok = QPushButton(btn_ok_text); btn_ok.setObjectName("dialog_btn_ok"); btn_ok.setFixedSize(140, 42); btn_ok.clicked.connect(self.accept) 
        btn_layout.addWidget(btn_cancel); btn_layout.addWidget(btn_ok)
        layout.addWidget(lbl_title); layout.addWidget(lbl_sub); layout.addSpacing(5); layout.addWidget(self.input_field); layout.addStretch(); layout.addLayout(btn_layout)
        self.apply_theme(is_dark_mode)

    def apply_theme(self, is_dark_mode):
        if is_dark_mode:
            self.bg_frame.setStyleSheet("""
                QFrame#dialog_bg { background-color: #313338; border-radius: 12px; border: 1px solid #1e1f22; }
                QLabel#dialog_title { color: #ffffff; font-size: 22px; font-weight: 800; }
                QLabel#dialog_sub { color: #b5bac1; font-size: 14px; }
                QLineEdit { background-color: #1e1f22; border: 1px solid #1e1f22; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #dbdee1; }
                QLineEdit:focus { border: 1px solid #5865f2; }
                QPushButton#dialog_btn_cancel { background-color: transparent; color: #b5bac1; font-size: 14px; font-weight: bold; border-radius: 6px; border: none; }
                QPushButton#dialog_btn_cancel:hover { color: #ffffff; text-decoration: underline; }
                QPushButton#dialog_btn_ok { background-color: #5865f2; color: white; font-size: 14px; font-weight: bold; border-radius: 6px; border: none; }
                QPushButton#dialog_btn_ok:hover { background-color: #4752c4; }
            """)
        else:
            self.bg_frame.setStyleSheet("""
                QFrame#dialog_bg { background-color: #ffffff; border-radius: 12px; border: 1px solid #e3e5e8; }
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

class AddFriendDialog(QDialog):
    def __init__(self, parent, is_dark_mode, lang_dict):
        super().__init__(parent); self.lang = lang_dict; self.is_dark_mode = is_dark_mode
        self.setWindowTitle(self.lang['search_title']); self.setFixedSize(500, 500) 
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint); self.setAttribute(Qt.WA_TranslucentBackground) 
        self.search_timer = QTimer(); self.search_timer.setSingleShot(True); self.search_timer.timeout.connect(self.perform_search)
        self.setup_ui(); self.apply_theme(self.is_dark_mode)

    def setup_ui(self):
        self.bg_frame = QFrame(self); self.bg_frame.setGeometry(0, 0, 500, 500); self.bg_frame.setObjectName("dialog_bg")
        shadow = QGraphicsDropShadowEffect(self); shadow.setBlurRadius(25); shadow.setXOffset(0); shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 180 if self.is_dark_mode else 80)); self.bg_frame.setGraphicsEffect(shadow)
        layout = QVBoxLayout(self.bg_frame); layout.setContentsMargins(30, 30, 30, 30); layout.setSpacing(15)
        lbl_title = QLabel(self.lang['search_title']); lbl_title.setObjectName("dialog_title"); lbl_title.setAlignment(Qt.AlignCenter)
        lbl_sub = QLabel(self.lang['search_sub']); lbl_sub.setObjectName("dialog_sub"); lbl_sub.setAlignment(Qt.AlignCenter)
        self.search_input = QLineEdit(); self.search_input.setPlaceholderText(self.lang['search_ph']); self.search_input.setMinimumHeight(45)
        self.search_input.textChanged.connect(self.on_text_changed)
        self.result_list = QListWidget(); self.result_list.setObjectName("result_list"); self.result_list.setSelectionMode(QListWidget.NoSelection) 
        btn_close = QPushButton(self.lang['search_btn_close']); btn_close.setObjectName("dialog_btn_cancel")
        btn_close.setFixedSize(120, 40); btn_close.setCursor(Qt.PointingHandCursor); btn_close.clicked.connect(self.reject) 
        layout.addWidget(lbl_title); layout.addWidget(lbl_sub); layout.addSpacing(10); layout.addWidget(self.search_input); layout.addWidget(self.result_list); layout.addWidget(btn_close, alignment=Qt.AlignCenter)

    def on_text_changed(self, text): self.search_timer.start(500) 
    def perform_search(self):
        query = self.search_input.text().strip(); self.result_list.clear()
        if not query: return
        item = QListWidgetItem("Aranıyor..."); item.setTextAlignment(Qt.AlignCenter); self.result_list.addItem(item)
        self.search_thread = ApiSearchUsersThread(query); self.search_thread.finished_signal.connect(self.on_search_finished); self.search_thread.start()

    def on_search_finished(self, success, user_list):
        self.result_list.clear()
        if success and isinstance(user_list, list):
            if len(user_list) == 0:
                item = QListWidgetItem(self.lang['search_no_result']); item.setTextAlignment(Qt.AlignCenter); self.result_list.addItem(item)
            else:
                for user in user_list: self.add_user_row(user)
        else:
            item = QListWidgetItem("Bağlantı hatası veya geçersiz sorgu."); item.setTextAlignment(Qt.AlignCenter); self.result_list.addItem(item)

    def add_user_row(self, user):
        item = QListWidgetItem(self.result_list); item.setSizeHint(QSize(0, 60)) 
        row_widget = QWidget(); row_layout = QHBoxLayout(row_widget); row_layout.setContentsMargins(10, 5, 10, 5)
        lbl_avatar = QLabel("👤"); lbl_avatar.setStyleSheet("font-size: 24px;")
        info_layout = QVBoxLayout(); lbl_name = QLabel(user.get('username', 'Bilinmeyen Kullanıcı')); lbl_name.setStyleSheet("font-weight: bold; font-size: 14px;")
        lbl_email = QLabel(user.get('email', '')); lbl_email.setObjectName("row_email") 
        info_layout.addWidget(lbl_name); info_layout.addWidget(lbl_email); info_layout.setAlignment(Qt.AlignVCenter)
        btn_add = QPushButton(self.lang['search_btn_add']); btn_add.setObjectName("dialog_btn_ok") 
        btn_add.setCursor(Qt.PointingHandCursor); btn_add.setFixedSize(80, 35); btn_add.clicked.connect(lambda _, u=user: self.send_friend_request(u))
        row_layout.addWidget(lbl_avatar); row_layout.addLayout(info_layout); row_layout.addStretch(); row_layout.addWidget(btn_add)
        self.result_list.setItemWidget(item, row_widget)

    def send_friend_request(self, user):
        self.add_req_thread = ApiAddFriendThread(str(user.get('id', '')))
        self.add_req_thread.finished_signal.connect(lambda s, m: self.on_request_finished(s, m, user)); self.add_req_thread.start()
        
    def on_request_finished(self, success, msg, user):
        if success: QMessageBox.information(self, "Başarılı", f"@{user.get('username', '')} kullanıcısına istek gönderildi!"); self.accept()
        else: QMessageBox.warning(self, "Hata", msg)

    def apply_theme(self, is_dark_mode):
        if is_dark_mode:
            self.bg_frame.setStyleSheet("""
                QFrame#dialog_bg { background-color: #313338; border-radius: 12px; border: 1px solid #1e1f22; }
                QLabel#dialog_title { color: #ffffff; font-size: 20px; font-weight: 800; }
                QLabel#dialog_sub { color: #b5bac1; font-size: 13px; }
                QLineEdit { background-color: #1e1f22; border: 1px solid #1e1f22; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #dbdee1; }
                QLineEdit:focus { border: 1px solid #5865f2; }
                QListWidget#result_list { background-color: transparent; border: none; outline: none; color: #dbdee1;}
                QListWidget#result_list::item { background-color: #2b2d31; border-radius: 8px; margin-bottom: 5px; }
                QListWidget#result_list::item:hover { background-color: #35393f; }
                QLabel#row_email { color: #b5bac1; font-size: 11px; }
                QPushButton#dialog_btn_cancel { background-color: transparent; color: #b5bac1; font-size: 14px; font-weight: bold; border-radius: 6px; padding: 10px; border: none; }
                QPushButton#dialog_btn_cancel:hover { color: #ffffff; text-decoration: underline; }
                QPushButton#dialog_btn_ok { background-color: #5865f2; color: white; font-size: 13px; font-weight: bold; border-radius: 6px; padding: 8px; border: none; }
                QPushButton#dialog_btn_ok:hover { background-color: #4752c4; }
            """)
        else:
            self.bg_frame.setStyleSheet("""
                QFrame#dialog_bg { background-color: #ffffff; border-radius: 12px; border: 1px solid #e3e5e8; }
                QLabel#dialog_title { color: #060607; font-size: 20px; font-weight: 800; }
                QLabel#dialog_sub { color: #4e5058; font-size: 13px; }
                QLineEdit { background-color: #f2f3f5; border: 1px solid #ccc; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #060607; }
                QLineEdit:focus { border: 1px solid #1877f2; background-color: #ffffff; }
                QListWidget#result_list { background-color: transparent; border: none; outline: none; color: #5c5e66;}
                QListWidget#result_list::item { background-color: #f8f9fa; border: 1px solid #e3e5e8; border-radius: 8px; margin-bottom: 5px; }
                QListWidget#result_list::item:hover { background-color: #f2f3f5; }
                QLabel#row_email { color: #5c5e66; font-size: 11px; }
                QPushButton#dialog_btn_cancel { background-color: transparent; color: #4e5058; font-size: 14px; font-weight: bold; border-radius: 6px; padding: 10px; border: none; }
                QPushButton#dialog_btn_cancel:hover { text-decoration: underline; }
                QPushButton#dialog_btn_ok { background-color: #1877f2; color: white; font-size: 13px; font-weight: bold; border-radius: 6px; padding: 8px; border: none; }
                QPushButton#dialog_btn_ok:hover { background-color: #166fe5; }
            """)


class SettingsDialog(QDialog):
    def __init__(self, parent, is_dark_mode, lang_dict):
        super().__init__(parent)
        self.parent_dashboard = parent 
        self.lang = lang_dict
        self.is_dark_mode = is_dark_mode
        self.setWindowTitle(self.lang['set_pers_title'])
        self.setFixedSize(850, 650) 
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        self.bg_frame = QFrame(self); self.bg_frame.setGeometry(0, 0, 850, 650); self.bg_frame.setObjectName("dialog_bg")
        shadow = QGraphicsDropShadowEffect(self); shadow.setBlurRadius(25); shadow.setXOffset(0); shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 180 if self.is_dark_mode else 80)); self.bg_frame.setGraphicsEffect(shadow)
        main_layout = QHBoxLayout(self.bg_frame); main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)

        self.sidebar = QFrame(); self.sidebar.setObjectName("settings_sidebar"); self.sidebar.setFixedWidth(240)
        sb_layout = QVBoxLayout(self.sidebar); sb_layout.setContentsMargins(15, 30, 15, 15)
        self.menu_list = QListWidget(); self.menu_list.setObjectName("settings_list")
        self.menu_list.addItem(self.lang['set_cat_personal']); self.menu_list.addItem(self.lang['set_cat_server'])
        logout_item = QListWidgetItem(self.lang['set_cat_logout']); logout_item.setForeground(QColor("#ed4245")) 
        self.menu_list.addItem(logout_item); self.menu_list.currentRowChanged.connect(self.on_menu_changed)
        sb_layout.addWidget(self.menu_list)

        self.content_area = QFrame(); self.content_area.setObjectName("settings_content")
        content_layout = QVBoxLayout(self.content_area); content_layout.setContentsMargins(40, 20, 40, 40)
        top_bar = QHBoxLayout()
        self.btn_close = QPushButton("✖"); self.btn_close.setObjectName("settings_close_btn")
        self.btn_close.setFixedSize(36, 36); self.btn_close.setCursor(Qt.PointingHandCursor); self.btn_close.clicked.connect(self.reject) 
        top_bar.addStretch(); top_bar.addWidget(self.btn_close)

        self.stacked = QStackedWidget()
        self.scroll_area = QScrollArea(); self.scroll_area.setWidgetResizable(True); self.scroll_area.setObjectName("settings_scroll")
        
        self.page_personal = QWidget(); p_layout = QVBoxLayout(self.page_personal); p_layout.setAlignment(Qt.AlignTop); p_layout.setSpacing(20)
        lbl_p_title = QLabel(self.lang['set_pers_title']); lbl_p_title.setObjectName("settings_title"); p_layout.addWidget(lbl_p_title)

        avatar_layout = QHBoxLayout()
        self.set_avatar = QLabel("👤"); self.set_avatar.setObjectName("big_avatar"); self.set_avatar.setFixedSize(80, 80); self.set_avatar.setAlignment(Qt.AlignCenter)
        btn_upload_avatar = QPushButton(self.lang['set_avatar_btn']); btn_upload_avatar.setObjectName("secondary_btn")
        btn_upload_avatar.setFixedSize(150, 40); btn_upload_avatar.setCursor(Qt.PointingHandCursor)
        btn_upload_avatar.clicked.connect(lambda: QMessageBox.information(self, "Bilgi", "Fotoğraf yükleme yakında eklenecektir."))
        avatar_layout.addWidget(self.set_avatar); avatar_layout.addSpacing(15); avatar_layout.addWidget(btn_upload_avatar); avatar_layout.addStretch()
        p_layout.addLayout(avatar_layout)

        lbl_name_hint = QLabel(self.lang['set_pers_name']); lbl_name_hint.setObjectName("bold_label")
        self.inp_name = QLineEdit(); self.inp_name.setMinimumHeight(45); self.inp_name.setText(self.parent_dashboard.lbl_username.text()); self.inp_name.setReadOnly(True) 
        lbl_email_hint = QLabel(self.lang['set_pers_email']); lbl_email_hint.setObjectName("bold_label")
        self.inp_email = QLineEdit(); self.inp_email.setMinimumHeight(45); self.inp_email.setText(self.parent_dashboard.lbl_email.text()); self.inp_email.setReadOnly(True) 
        p_layout.addWidget(lbl_name_hint); p_layout.addWidget(self.inp_name); p_layout.addWidget(lbl_email_hint); p_layout.addWidget(self.inp_email)

        self.acc_box = QFrame(); self.acc_box.setObjectName("account_box"); acc_box_layout = QVBoxLayout(self.acc_box)
        lbl_acc_box_title = QLabel(self.lang['set_acc_title']); lbl_acc_box_title.setObjectName("bold_label")
        lbl_acc_type = QLabel(self.lang['set_acc_type']); lbl_acc_type.setStyleSheet("font-size: 14px;")
        lbl_acc_limit = QLabel(self.lang['set_acc_limit']); lbl_acc_limit.setStyleSheet("font-size: 14px;")
        self.btn_upgrade = QPushButton(self.lang['set_acc_upgrade']); self.btn_upgrade.setObjectName("upgrade_btn"); self.btn_upgrade.setCursor(Qt.PointingHandCursor)
        self.btn_upgrade.clicked.connect(lambda: webbrowser.open("https://sizin-odeme-linkiniz.com"))
        acc_box_layout.addWidget(lbl_acc_box_title); acc_box_layout.addWidget(lbl_acc_type); acc_box_layout.addWidget(lbl_acc_limit); acc_box_layout.addSpacing(10); acc_box_layout.addWidget(self.btn_upgrade)
        p_layout.addWidget(self.acc_box)

        lbl_pass_title = QLabel(self.lang['set_pass_title']); lbl_pass_title.setObjectName("settings_title"); p_layout.addWidget(lbl_pass_title)
        self.inp_old_pass = QLineEdit(); self.inp_old_pass.setPlaceholderText(self.lang['set_pass_old']); self.inp_old_pass.setMinimumHeight(45); self.inp_old_pass.setEchoMode(QLineEdit.Password)
        self.inp_new_pass = QLineEdit(); self.inp_new_pass.setPlaceholderText(self.lang['set_pass_new']); self.inp_new_pass.setMinimumHeight(45); self.inp_new_pass.setEchoMode(QLineEdit.Password)
        self.inp_new_pass_rep = QLineEdit(); self.inp_new_pass_rep.setPlaceholderText(self.lang['set_pass_rep']); self.inp_new_pass_rep.setMinimumHeight(45); self.inp_new_pass_rep.setEchoMode(QLineEdit.Password)
        p_layout.addWidget(self.inp_old_pass); p_layout.addWidget(self.inp_new_pass); p_layout.addWidget(self.inp_new_pass_rep)

        btn_save_p = QPushButton(self.lang['set_pers_save']); btn_save_p.setObjectName("primary_btn"); btn_save_p.setFixedSize(200, 45); btn_save_p.setCursor(Qt.PointingHandCursor)
        p_layout.addSpacing(20); p_layout.addWidget(btn_save_p)
        self.scroll_area.setWidget(self.page_personal)

        self.page_server = QWidget(); s_layout = QVBoxLayout(self.page_server); s_layout.setAlignment(Qt.AlignTop)
        lbl_s_title = QLabel(self.lang['set_srv_title']); lbl_s_title.setObjectName("settings_title")
        lbl_s_desc = QLabel(self.lang['set_srv_desc']); lbl_s_desc.setObjectName("desc_label")
        s_layout.addWidget(lbl_s_title); s_layout.addWidget(lbl_s_desc)

        self.stacked.addWidget(self.scroll_area); self.stacked.addWidget(self.page_server)
        content_layout.addLayout(top_bar); content_layout.addWidget(self.stacked)
        main_layout.addWidget(self.sidebar); main_layout.addWidget(self.content_area)
        self.menu_list.setCurrentRow(0)

    def on_menu_changed(self, row):
        if row == 0: self.stacked.setCurrentIndex(0)
        elif row == 1: self.stacked.setCurrentIndex(1)
        elif row == 2: self.done(2) 

    def apply_theme(self):
        if self.is_dark_mode:
            self.bg_frame.setStyleSheet("""
                QFrame#dialog_bg { background-color: #313338; border-radius: 12px; border: 1px solid #1e1f22; }
                QFrame#settings_sidebar { background-color: #2b2d31; border-top-left-radius: 12px; border-bottom-left-radius: 12px; }
                QListWidget#settings_list { background: transparent; border: none; outline: none; font-size: 15px; font-weight: bold; }
                QListWidget#settings_list::item { color: #b5bac1; padding: 12px 15px; border-radius: 6px; margin-bottom: 5px; }
                QListWidget#settings_list::item:hover { background-color: #35393f; color: #dcddde; }
                QListWidget#settings_list::item:selected { background-color: #404249; color: #ffffff; }
                
                QFrame#settings_content { background-color: #313338; border-top-right-radius: 12px; border-bottom-right-radius: 12px; }
                QLabel#settings_title { color: #ffffff; font-size: 22px; font-weight: 800; border-bottom: 1px solid #444; padding-bottom: 10px; margin-top: 15px; }
                QLabel#bold_label { color: #dcddde; font-weight: bold; font-size: 13px; }
                QLabel#desc_label { color: #949ba4; font-size: 13px; }
                
                QLabel#big_avatar { background-color: #5865f2; color: white; font-size: 36px; border-radius: 40px; }
                QPushButton#settings_close_btn { background-color: transparent; color: #949ba4; font-weight: bold; font-size: 20px; border: none; }
                QPushButton#settings_close_btn:hover { color: #ffffff; }
                
                QLineEdit { background-color: #1e1f22; border: 1px solid #444; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #ffffff; }
                QLineEdit:focus { border: 1px solid #5865f2; }
                QLineEdit[readOnly="true"] { background-color: #232428; color: #87909c; border: 1px solid #1e1f22; }
                
                QPushButton#primary_btn { background-color: #5865f2; color: white; border-radius: 6px; padding: 12px; font-weight: bold; font-size: 14px; border: none; }
                QPushButton#primary_btn:hover { background-color: #4752c4; }
                QPushButton#secondary_btn { background-color: #2b2d31; color: #dcddde; border: 1px solid #444; border-radius: 6px; padding: 10px; font-weight: bold; font-size: 13px; }
                QPushButton#secondary_btn:hover { background-color: #35393f; }
                
                QFrame#account_box { background-color: #2b2d31; border: 1px solid #1e1f22; border-radius: 8px; }
                QPushButton#upgrade_btn { background-color: #f1c40f; color: #000; font-weight: bold; border-radius: 6px; padding: 10px; font-size: 14px; border: none; }
                QPushButton#upgrade_btn:hover { background-color: #d4ac0d; }
                
                QScrollArea#settings_scroll { background: transparent; border: none; }
                QScrollArea#settings_scroll > QWidget > QWidget { background: transparent; }
            """)
        else:
            self.bg_frame.setStyleSheet("""
                QFrame#dialog_bg { background-color: #ffffff; border-radius: 12px; border: 1px solid #ccc; }
                QFrame#settings_sidebar { background-color: #f2f3f5; border-top-left-radius: 12px; border-bottom-left-radius: 12px; border-right: 1px solid #e3e5e8; }
                QListWidget#settings_list { background: transparent; border: none; outline: none; font-size: 15px; font-weight: bold; }
                QListWidget#settings_list::item { color: #4e5058; padding: 12px 15px; border-radius: 6px; margin-bottom: 5px; }
                QListWidget#settings_list::item:hover { background-color: #e3e5e8; color: #060607; }
                QListWidget#settings_list::item:selected { background-color: #d4d7dc; color: #060607; }
                
                QFrame#settings_content { background-color: #ffffff; border-top-right-radius: 12px; border-bottom-right-radius: 12px; }
                QLabel#settings_title { color: #060607; font-size: 22px; font-weight: 800; border-bottom: 1px solid #e3e5e8; padding-bottom: 10px; margin-top: 15px; }
                QLabel#bold_label { color: #4e5058; font-weight: bold; font-size: 13px; }
                QLabel#desc_label { color: #5c5e66; font-size: 13px; }
                
                QLabel#big_avatar { background-color: #1877f2; color: white; font-size: 36px; border-radius: 40px; }
                QPushButton#settings_close_btn { background-color: transparent; color: #5c5e66; font-weight: bold; font-size: 20px; border: none; }
                QPushButton#settings_close_btn:hover { color: #060607; }
                
                QLineEdit { background-color: #f2f3f5; border: 1px solid #ccc; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #060607; }
                QLineEdit:focus { border: 1px solid #1877f2; background-color: #ffffff; }
                QLineEdit[readOnly="true"] { background-color: #e3e5e8; color: #5c5e66; border: 1px solid #ccc; }
                
                QPushButton#primary_btn { background-color: #1877f2; color: white; border-radius: 6px; padding: 12px; font-weight: bold; font-size: 14px; border: none; }
                QPushButton#primary_btn:hover {{ background-color: #166fe5; }}
                QPushButton#secondary_btn { background-color: #f8f9fa; color: #4e5058; border: 1px solid #ccc; border-radius: 6px; padding: 10px; font-weight: bold; font-size: 13px; }
                QPushButton#secondary_btn:hover {{ background-color: #e3e5e8; }}
                
                QFrame#account_box { background-color: #f8f9fa; border: 1px solid #e3e5e8; border-radius: 8px; }
                QPushButton#upgrade_btn { background-color: #f1c40f; color: #000; font-weight: bold; border-radius: 6px; padding: 10px; font-size: 14px; border: none; }
                QPushButton#upgrade_btn:hover { background-color: #d4ac0d; }
                
                QScrollArea#settings_scroll { background: transparent; border: none; }
                QScrollArea#settings_scroll > QWidget > QWidget { background: transparent; }
            """)


# ==========================================
# ANA EKRAN (DASHBOARD VIEW)
# ==========================================
class DashboardView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.setObjectName("dashboard_main") # CSS BUG FIX ICIN GEREKLI
        self.main_window = main_window
        self.settings = QSettings("MySaaS", "DesktopClient")
        self.is_dark_mode = self.settings.value("is_dark_mode", False, type=bool)
        self.current_lang = self.settings.value("language", "TR")
        
        self.is_online = True 
        self.is_mic_on = True
        self.is_deafened = False
        
        self.setup_ui()
        self.sync_settings()
        self.fetch_my_profile()
        self.fetch_my_servers()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'floating_profile_box'):
            pb_width = 245 
            pb_height = 80
            self.floating_profile_box.setGeometry(7, self.height() - pb_height - 15, pb_width, pb_height)

    def handle_unauthorized(self):
        if hasattr(self, 'servers_thread') and self.servers_thread.isRunning(): self.servers_thread.quit()
        if hasattr(self, 'join_thread') and self.join_thread.isRunning(): self.join_thread.quit()
        if hasattr(self, 'create_thread') and self.create_thread.isRunning(): self.create_thread.quit()
        if hasattr(self, 'profile_thread') and self.profile_thread.isRunning(): self.profile_thread.quit()
            
        t = DASHBOARD_LANGS[self.current_lang]
        self.settings.setValue("auth_token", "") 
        self.settings.setValue("remember_me", False) 
        self.main_window.show_login()
        QMessageBox.critical(self.main_window, "Oturum Hatası", t['err_401'])

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

    def toggle_sidebar(self):
        self.sidebar_anim = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.sidebar_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.sidebar_anim.setDuration(250)
        if self.sidebar.width() > 10:
            self.sidebar_anim.setStartValue(260); self.sidebar_anim.setEndValue(0)
            self.sidebar.setMinimumWidth(0)
        else:
            self.sidebar_anim.setStartValue(0); self.sidebar_anim.setEndValue(260)
            self.sidebar.setMinimumWidth(260)
        self.sidebar_anim.start()

    def toggle_mic(self):
        self.is_mic_on = not self.is_mic_on
        self.btn_mic.setText("🎙️" if self.is_mic_on else "🔇")
        self.apply_theme() 

    def toggle_deafen(self):
        self.is_deafened = not self.is_deafened
        self.btn_deafen.setText("🎧" if not self.is_deafened else "🔈")
        self.apply_theme() 

    def fetch_my_profile(self):
        self.profile_thread = ApiFetchProfileThread()
        self.profile_thread.finished_signal.connect(self.on_profile_fetched)
        self.profile_thread.start()

    def on_profile_fetched(self, success, data):
        if success and data:
            name = data.get("name", data.get("username", "Kullanıcı"))
            email = data.get("email", "bilinmeyen@hesap.com")
            self.lbl_username.setText(name)
            self.lbl_email.setText(email)

    def fetch_my_servers(self):
        self.server_list.clear()
        self.servers_thread = ApiFetchMyServersThread()
        self.servers_thread.finished_signal.connect(self.on_servers_fetched)
        self.servers_thread.start()

    def on_servers_fetched(self, success, servers, error_type):
        self.server_list.clear()
        t = DASHBOARD_LANGS[self.current_lang]
        
        home_item = QListWidgetItem(f"🏠 {t['home_btn']}")
        home_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
        home_item.setData(Qt.UserRole, "HOME")
        self.server_list.addItem(home_item)
        self.server_list.addItem(QListWidgetItem("")) 
        
        if success and isinstance(servers, list):
            if len(servers) == 0:
                item = QListWidgetItem(t['no_servers']); item.setFont(QFont("Segoe UI", 10)); item.setFlags(Qt.NoItemFlags) 
                self.server_list.addItem(item)
                if not self.settings.value("has_completed_onboarding", False, type=bool):
                    self.stacked_widget.setCurrentWidget(self.page_selection)
                else:
                    self.stacked_widget.setCurrentWidget(self.page_standard) 
            else:
                for srv in servers:
                    name = srv.get("name", "Bilinmeyen Sunucu")
                    item = QListWidgetItem(f"🏢 {name}")
                    item.setFont(QFont("Segoe UI", 11))
                    item.setData(Qt.UserRole, srv.get("id"))
                    self.server_list.addItem(item)
                
                self.stacked_widget.setCurrentWidget(self.page_friends) 
                self.lbl_channel_name.setText(t['friends_title'])
                
        elif error_type == "UNAUTHORIZED":
            QTimer.singleShot(100, self.handle_unauthorized)
        else:
            item = QListWidgetItem("Bağlantı Bekleniyor...")
            item.setFont(QFont("Segoe UI", 10))
            self.server_list.addItem(item)

    def on_server_selected(self, item):
        server_id = item.data(Qt.UserRole)
        if not server_id: return
        t = DASHBOARD_LANGS[self.current_lang]
        if server_id == "HOME":
            self.stacked_widget.setCurrentWidget(self.page_friends)
            self.lbl_channel_name.setText(t['friends_title'])
            return
            
        server_name = item.text().replace("🏢 ", "")
        self.lbl_srv_title.setText(server_name)
        self.lbl_channel_name.setText("# genel-sohbet")
        self.stacked_widget.setCurrentWidget(self.page_active_server)
        self.populate_mock_channels()

    def populate_mock_channels(self):
        self.channel_list.clear()
        t = DASHBOARD_LANGS[self.current_lang]
        cat1 = QListWidgetItem(t['cat_text']); cat1.setFlags(Qt.NoItemFlags); cat1.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.channel_list.addItem(cat1)
        self.channel_list.addItem(QListWidgetItem("   # genel-sohbet"))
        cat2 = QListWidgetItem(t['cat_board']); cat2.setFlags(Qt.NoItemFlags); cat2.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.channel_list.addItem(cat2)
        self.channel_list.addItem(QListWidgetItem("   📋 Proje Panosu"))

    def show_settings_page(self):
        t = DASHBOARD_LANGS[self.current_lang]
        dialog = SettingsDialog(self, self.is_dark_mode, t)
        result = dialog.exec()
        if result == 2: 
            self.settings.setValue("auth_token", "")
            self.settings.setValue("remember_me", False) 
            self.main_window.show_login()

    def setup_ui(self):
        self.main_layout = QHBoxLayout(self); self.main_layout.setContentsMargins(0, 0, 0, 0); self.main_layout.setSpacing(0)

        self.sidebar = QFrame(); self.sidebar.setObjectName("sidebar")
        self.sidebar.setMaximumWidth(260); self.sidebar.setMinimumWidth(260) 
        sidebar_layout = QVBoxLayout(self.sidebar); sidebar_layout.setContentsMargins(15, 20, 15, 15); sidebar_layout.setSpacing(15)

        self.lbl_logo = QLabel(); self.lbl_logo.setObjectName("logo_text")
        self.lbl_menu_title = QLabel(); self.lbl_menu_title.setObjectName("menu_title")
        self.server_list = QListWidget(); self.server_list.setObjectName("server_list")
        self.server_list.itemClicked.connect(self.on_server_selected)
        self.server_list.setStyleSheet("padding-bottom: 100px;") 

        sidebar_layout.addWidget(self.lbl_logo); sidebar_layout.addSpacing(10)
        sidebar_layout.addWidget(self.lbl_menu_title); sidebar_layout.addWidget(self.server_list)

        self.content_area = QFrame(); self.content_area.setObjectName("content_area")
        content_layout = QVBoxLayout(self.content_area); content_layout.setContentsMargins(0, 0, 0, 0); content_layout.setSpacing(0)

        self.header = QFrame(); self.header.setObjectName("header"); self.header.setFixedHeight(65)
        header_layout = QHBoxLayout(self.header); header_layout.setContentsMargins(15, 0, 20, 0)
        self.btn_toggle_sidebar = QPushButton("☰"); self.btn_toggle_sidebar.setObjectName("header_toggle_btn")
        self.btn_toggle_sidebar.setFixedSize(40, 40); self.btn_toggle_sidebar.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_sidebar.clicked.connect(self.toggle_sidebar)
        
        self.lbl_channel_name = QLabel(); self.lbl_channel_name.setObjectName("channel_name")
        self.btn_theme = QPushButton(); self.btn_theme.setObjectName("theme_btn"); self.btn_theme.setCursor(Qt.PointingHandCursor); self.btn_theme.clicked.connect(self.toggle_theme)

        self.lang_cb = QComboBox(); self.lang_cb.setObjectName("lang_cb"); self.lang_cb.setCursor(Qt.PointingHandCursor)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.lang_cb.addItem(QIcon(os.path.join(base_dir, 'assets', 'tr.png').replace('\\', '/')), "TR")
        self.lang_cb.addItem(QIcon(os.path.join(base_dir, 'assets', 'en.png').replace('\\', '/')), "EN")
        self.lang_cb.addItem(QIcon(os.path.join(base_dir, 'assets', 'ger.png').replace('\\', '/')), "GER")
        self.lang_cb.setIconSize(QSize(20, 15)); self.lang_cb.currentTextChanged.connect(self.change_language)
        
        header_layout.addWidget(self.btn_toggle_sidebar); header_layout.addSpacing(10)
        header_layout.addWidget(self.lbl_channel_name); header_layout.addStretch()
        header_layout.addWidget(self.btn_theme); header_layout.addWidget(self.lang_cb)
        content_layout.addWidget(self.header)

        # SAYFALARA ÖZEL 'page_bg' ID'si EKLENDİ (AÇIK TEMA BUG'I İÇİN)
        self.stacked_widget = QStackedWidget(); self.stacked_widget.setObjectName("main_stack")
        self.page_selection = self.create_selection_page(); self.page_selection.setObjectName("page_bg")
        self.page_standard = self.create_standard_page(); self.page_standard.setObjectName("page_bg")
        self.page_enterprise = self.create_enterprise_page(); self.page_enterprise.setObjectName("page_bg")
        self.page_server_setup = self.create_server_setup_page(); self.page_server_setup.setObjectName("page_bg")
        self.page_active_server = self.create_active_server_page(); self.page_active_server.setObjectName("page_bg")
        self.page_friends = self.create_friends_page(); self.page_friends.setObjectName("page_bg")

        self.stacked_widget.addWidget(self.page_selection)
        self.stacked_widget.addWidget(self.page_standard)
        self.stacked_widget.addWidget(self.page_enterprise)
        self.stacked_widget.addWidget(self.page_server_setup) 
        self.stacked_widget.addWidget(self.page_active_server) 
        self.stacked_widget.addWidget(self.page_friends)
        
        self.stacked_widget.setCurrentWidget(self.page_selection) 
        content_layout.addWidget(self.stacked_widget)
        self.main_layout.addWidget(self.sidebar); self.main_layout.addWidget(self.content_area)

        self.floating_profile_box = QFrame(self) 
        self.floating_profile_box.setObjectName("floating_profile")
        shadow = QGraphicsDropShadowEffect(self); shadow.setBlurRadius(20); shadow.setXOffset(0); shadow.setYOffset(5); shadow.setColor(QColor(0, 0, 0, 150))
        self.floating_profile_box.setGraphicsEffect(shadow)

        pf_layout = QHBoxLayout(self.floating_profile_box); pf_layout.setContentsMargins(12, 8, 12, 8); pf_layout.setSpacing(8)
        self.lbl_avatar = QLabel("👤"); self.lbl_avatar.setObjectName("profile_avatar"); self.lbl_avatar.setFixedSize(40, 40); self.lbl_avatar.setAlignment(Qt.AlignCenter)

        info_widget = QWidget(); info_layout = QVBoxLayout(info_widget); info_layout.setContentsMargins(0,0,0,0); info_layout.setSpacing(0)
        
        name_status_layout = QHBoxLayout()
        self.lbl_username = QLabel("Yükleniyor..."); self.lbl_username.setObjectName("profile_user")
        self.lbl_status = QLabel("🟢") 
        name_status_layout.addWidget(self.lbl_username); name_status_layout.addWidget(self.lbl_status); name_status_layout.addStretch()

        self.lbl_email = QLabel("..."); self.lbl_email.setObjectName("profile_email"); self.lbl_email.setFixedWidth(95) 

        info_layout.addLayout(name_status_layout); info_layout.addWidget(self.lbl_email); info_layout.setAlignment(Qt.AlignVCenter)

        btn_layout = QHBoxLayout(); btn_layout.setSpacing(2)
        
        self.btn_mic = QPushButton("🎙️"); self.btn_mic.setObjectName("btn_mic")
        self.btn_deafen = QPushButton("🎧"); self.btn_deafen.setObjectName("btn_deafen")
        self.btn_settings = QPushButton("⚙️"); self.btn_settings.setObjectName("btn_settings")
        
        for btn in [self.btn_mic, self.btn_deafen, self.btn_settings]:
            btn.setFixedSize(30, 30); btn.setCursor(Qt.PointingHandCursor)
            btn_layout.addWidget(btn)

        self.btn_mic.clicked.connect(self.toggle_mic)
        self.btn_deafen.clicked.connect(self.toggle_deafen)
        self.btn_settings.clicked.connect(self.show_settings_page)

        pf_layout.addWidget(self.lbl_avatar); pf_layout.addWidget(info_widget); pf_layout.addStretch(); pf_layout.addLayout(btn_layout)


    def complete_onboarding(self):
        self.settings.setValue("has_completed_onboarding", True); self.stacked_widget.setCurrentWidget(self.page_standard)

    def create_friends_page(self):
        page = QWidget(); page.setObjectName("friends_page_main")
        layout = QVBoxLayout(page); layout.setContentsMargins(40, 40, 40, 40); layout.setAlignment(Qt.AlignTop)

        top_bar = QHBoxLayout()
        self.btn_friends_online = QPushButton("Çevrimiçi"); self.btn_friends_online.setObjectName("tab_btn_active"); self.btn_friends_online.setCursor(Qt.PointingHandCursor)
        self.btn_friends_all = QPushButton("Tümü"); self.btn_friends_all.setObjectName("tab_btn"); self.btn_friends_all.setCursor(Qt.PointingHandCursor)
        
        self.btn_search_friend = QPushButton("🔍 Arkadaş Ara"); self.btn_search_friend.setObjectName("success_btn")
        self.btn_search_friend.setFixedSize(140, 40); self.btn_search_friend.setCursor(Qt.PointingHandCursor)
        self.btn_search_friend.clicked.connect(self.show_add_friend_dialog)
        
        top_bar.addWidget(self.btn_friends_online); top_bar.addWidget(self.btn_friends_all); top_bar.addStretch(); top_bar.addWidget(self.btn_search_friend)
        
        divider = QFrame(); divider.setFrameShape(QFrame.HLine); divider.setStyleSheet("color: rgba(150,150,150,0.2); margin: 15px 0;")
        
        self.friends_search_input = QLineEdit(); self.friends_search_input.setObjectName("search_input") 
        self.friends_search_input.setPlaceholderText("Arkadaşlarda Ara..."); self.friends_search_input.setMinimumHeight(45)
        
        self.friends_list_area = QListWidget(); self.friends_list_area.setObjectName("friends_list")
        
        empty_item = QListWidgetItem("Henüz arkadaş listeniz boş."); empty_item.setTextAlignment(Qt.AlignCenter); empty_item.setFlags(Qt.NoItemFlags)
        self.friends_list_area.addItem(empty_item)

        layout.addLayout(top_bar); layout.addWidget(divider); layout.addWidget(self.friends_search_input); layout.addSpacing(10); layout.addWidget(self.friends_list_area)
        return page

    def create_active_server_page(self):
        page = QWidget(); page.setObjectName("active_server_main")
        layout = QHBoxLayout(page); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(0)

        self.channel_sidebar = QFrame(); self.channel_sidebar.setObjectName("channel_sidebar"); self.channel_sidebar.setFixedWidth(240)
        ch_layout = QVBoxLayout(self.channel_sidebar); ch_layout.setContentsMargins(15, 20, 15, 15)
        
        self.lbl_srv_title = QLabel("Sunucu Adı"); self.lbl_srv_title.setObjectName("srv_title")
        ch_layout.addWidget(self.lbl_srv_title); ch_layout.addSpacing(15)
        
        self.channel_list = QListWidget(); self.channel_list.setObjectName("channel_list")
        self.channel_list.setStyleSheet("padding-bottom: 90px;") 
        ch_layout.addWidget(self.channel_list)

        self.chat_area = QFrame(); self.chat_area.setObjectName("chat_area")
        chat_layout = QVBoxLayout(self.chat_area); chat_layout.setContentsMargins(20, 20, 20, 20)
        
        self.msg_list = QListWidget(); self.msg_list.setObjectName("msg_list"); self.msg_list.setSelectionMode(QListWidget.NoSelection)
        
        input_frame = QFrame(); input_frame.setObjectName("chat_input_frame")
        input_layout = QHBoxLayout(input_frame); input_layout.setContentsMargins(5, 5, 5, 5)
        self.msg_input = QLineEdit(); self.msg_input.setObjectName("chat_input"); self.msg_input.setMinimumHeight(45)
        self.btn_send_msg = QPushButton("Gönder"); self.btn_send_msg.setObjectName("primary_btn"); self.btn_send_msg.setFixedSize(80, 45); self.btn_send_msg.setCursor(Qt.PointingHandCursor)
        
        input_layout.addWidget(self.msg_input); input_layout.addWidget(self.btn_send_msg)
        chat_layout.addWidget(self.msg_list); chat_layout.addWidget(input_frame)

        layout.addWidget(self.channel_sidebar); layout.addWidget(self.chat_area)
        return page

    def create_server_setup_page(self):
        page = QWidget(); page.setObjectName("setup_page_main"); layout = QVBoxLayout(page); layout.setAlignment(Qt.AlignCenter)
        self.setup_box = QFrame(); self.setup_box.setObjectName("payment_box"); self.setup_box.setFixedSize(550, 450)
        box_layout = QVBoxLayout(self.setup_box); box_layout.setContentsMargins(40, 40, 40, 40); box_layout.setSpacing(20)
        
        self.lbl_setup_title = QLabel(); self.lbl_setup_title.setObjectName("pay_title"); self.lbl_setup_title.setAlignment(Qt.AlignCenter)
        self.lbl_setup_sub = QLabel(); self.lbl_setup_sub.setObjectName("welcome_sub"); self.lbl_setup_sub.setAlignment(Qt.AlignCenter); self.lbl_setup_sub.setWordWrap(True)
        self.setup_name_input = QLineEdit(); self.setup_name_input.setMinimumHeight(50)
        self.btn_upload_icon = QPushButton(); self.btn_upload_icon.setObjectName("secondary_btn"); self.btn_upload_icon.setMinimumHeight(45); self.btn_upload_icon.setCursor(Qt.PointingHandCursor)
        self.btn_upload_icon.clicked.connect(lambda: QMessageBox.information(self, "Bilgi", "İkon yükleme özelliği yakında eklenecek."))
        
        btn_layout = QHBoxLayout()
        self.btn_setup_cancel = QPushButton(); self.btn_setup_cancel.setObjectName("text_btn"); self.btn_setup_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_setup_cancel.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.page_standard))
        self.btn_setup_create = QPushButton(); self.btn_setup_create.setObjectName("primary_btn"); self.btn_setup_create.setMinimumHeight(45); self.btn_setup_create.setCursor(Qt.PointingHandCursor)
        self.btn_setup_create.clicked.connect(self.start_server_creation) 

        btn_layout.addWidget(self.btn_setup_cancel); btn_layout.addWidget(self.btn_setup_create)
        box_layout.addWidget(self.lbl_setup_title); box_layout.addWidget(self.lbl_setup_sub); box_layout.addSpacing(10); box_layout.addWidget(self.setup_name_input); box_layout.addWidget(self.btn_upload_icon); box_layout.addStretch(); box_layout.addLayout(btn_layout)
        layout.addWidget(self.setup_box)
        return page

    def create_selection_page(self):
        page = QWidget(); page.setObjectName("selection_page_main"); layout = QVBoxLayout(page); layout.setAlignment(Qt.AlignCenter); layout.setSpacing(40)
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
        page = QWidget(); page.setObjectName("standard_page_main"); layout = QVBoxLayout(page); layout.setAlignment(Qt.AlignCenter); layout.setSpacing(20) 
        top_layout = QVBoxLayout(); top_layout.setAlignment(Qt.AlignCenter)
        self.lbl_welcome_title = QLabel(); self.lbl_welcome_title.setObjectName("welcome_title"); self.lbl_welcome_title.setAlignment(Qt.AlignCenter)
        self.lbl_welcome_sub = QLabel(); self.lbl_welcome_sub.setObjectName("welcome_sub"); self.lbl_welcome_sub.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(self.lbl_welcome_title); top_layout.addWidget(self.lbl_welcome_sub)

        cards_layout = QHBoxLayout(); cards_layout.setSpacing(25); cards_layout.setAlignment(Qt.AlignCenter)
        self.card_create, self.lbl_c_title, self.lbl_c_desc, self.btn_create = self.create_action_card("➕")
        self.card_join, self.lbl_j_title, self.lbl_j_desc, self.btn_join = self.create_action_card("🔗")
        self.card_friend, self.lbl_f_title, self.lbl_f_desc, self.btn_friend = self.create_action_card("👥")
        
        self.btn_create.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.page_server_setup))
        self.btn_join.clicked.connect(self.show_join_dialog)
        self.btn_friend.clicked.connect(self.show_add_friend_dialog)
        
        cards_layout.addWidget(self.card_create); cards_layout.addWidget(self.card_join); cards_layout.addWidget(self.card_friend)
        layout.addStretch(); layout.addLayout(top_layout); layout.addSpacing(20); layout.addLayout(cards_layout); layout.addStretch()
        return page

    def create_enterprise_page(self):
        page = QWidget(); page.setObjectName("enterprise_page_main"); layout = QVBoxLayout(page); layout.setAlignment(Qt.AlignCenter)
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

    def start_server_creation(self):
        server_name = self.setup_name_input.text().strip()
        if not server_name:
            QMessageBox.warning(self, "Uyarı", "Lütfen sunucu adını boş bırakmayın.")
            return

        self.btn_setup_create.setText("Yükleniyor...")
        self.btn_setup_create.setEnabled(False)

        self.create_thread = ApiCreateServerThread(server_name)
        self.create_thread.finished_signal.connect(self.on_create_finished)
        self.create_thread.start()

    def show_message_safe(self, title, message, is_success):
        if is_success:
            QMessageBox.information(self, title, message)
            self.fetch_my_servers()
            self.stacked_widget.setCurrentWidget(self.page_friends) 
            self.setup_name_input.clear()
        else:
            QMessageBox.warning(self, title, message)
        
        t = DASHBOARD_LANGS[self.current_lang]
        self.btn_setup_create.setText(t['setup_btn_create'])
        self.btn_setup_create.setEnabled(True)

    def on_create_finished(self, success, msg, error_type):
        t = DASHBOARD_LANGS[self.current_lang]
        if success:
            QTimer.singleShot(100, lambda: self.show_message_safe("Başarılı", msg, True))
        else:
            if error_type == "LIMIT_EXCEEDED":
                QTimer.singleShot(100, lambda: self.show_message_safe("Limit Uyarısı", t['err_freemium_limit'], False))
            elif error_type == "UNAUTHORIZED":
                QTimer.singleShot(100, self.handle_unauthorized)
            else:
                QTimer.singleShot(100, lambda: self.show_message_safe("Hata", msg, False))

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

    def show_message_safe_join(self, title, msg, is_success):
        if is_success:
            QMessageBox.information(self, title, msg)
            self.fetch_my_servers()
        else:
            QMessageBox.warning(self, title, msg)

    def on_join_finished(self, success, msg, error_type):
        t = DASHBOARD_LANGS[self.current_lang]
        if success: 
            QTimer.singleShot(100, lambda: self.show_message_safe_join("Başarılı", msg, True))
        else: 
            if error_type == "UNAUTHORIZED":
                QTimer.singleShot(100, self.handle_unauthorized)
            else:
                QTimer.singleShot(100, lambda: self.show_message_safe_join("Hata", t['err_invalid_invite'], False))

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
        self.btn_settings.setToolTip(t['logout_tip']); self.btn_theme.setText(t['theme_light'] if self.is_dark_mode else t['theme_dark'])
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
        
        self.lbl_setup_title.setText(t['setup_title']); self.lbl_setup_sub.setText(t['setup_sub'])
        self.btn_upload_icon.setText(t['setup_btn_icon']); self.setup_name_input.setPlaceholderText(t['setup_ph'])
        self.btn_setup_create.setText(t['setup_btn_create']); self.btn_setup_cancel.setText(t['setup_btn_cancel'])
        
        if hasattr(self, 'msg_input'):
            self.msg_input.setPlaceholderText(t['chat_ph']); self.btn_send_msg.setText(t['btn_send'])
            if self.channel_list.count() > 0: self.populate_mock_channels()
            
        self.btn_mic.setToolTip(t['tip_mic'])
        self.btn_deafen.setToolTip(t['tip_deaf'])

        if hasattr(self, 'btn_friends_online'):
            self.btn_friends_online.setText(t['friends_online'])
            self.btn_friends_all.setText(t['friends_all'])
            self.btn_search_friend.setText(t['btn_search_friend'])
            self.friends_search_input.setPlaceholderText(t['friends_search'])
            if self.friends_list_area.count() > 0 and self.friends_list_area.item(0).flags() == Qt.NoItemFlags:
                self.friends_list_area.item(0).setText(t['friends_empty'])
                
        if self.stacked_widget.currentWidget() == self.page_friends:
            self.lbl_channel_name.setText(t['friends_title'])

    def apply_theme(self):
        status_color = "#23a559" if self.is_online else "#80848e"
        mic_bg = "transparent" if self.is_mic_on else "#ed4245"
        deaf_bg = "transparent" if not self.is_deafened else "#ed4245"

        if self.is_dark_mode:
            self.setStyleSheet(f"""
                /* CSS BUG FIX: ZORUNLU AÇIK/KOYU TEMA ARKA PLANLARI */
                QWidget#dashboard_main, QWidget#page_bg, QStackedWidget#main_stack,
                QWidget#selection_page_main, QWidget#standard_page_main, QWidget#enterprise_page_main,
                QWidget#setup_page_main, QWidget#active_server_main, QWidget#friends_page_main {{ 
                    background-color: #313338; color: #dcddde; 
                }}
                QWidget#page_bg QLabel {{ color: #ffffff; }}
                
                QFrame#sidebar {{ background-color: #1e2124; border-right: 1px solid #282b30; }}
                QLabel#logo_text {{ color: #ffffff; font-size: 18px; font-weight: 800; }}
                QLabel#menu_title {{ color: #87909c; font-size: 11px; font-weight: bold; margin-top: 10px; }}
                QListWidget#server_list {{ background: transparent; border: none; outline: none; }}
                QListWidget#server_list::item {{ color: #949ba4; padding: 10px 15px; border-radius: 6px; margin-bottom: 2px;}}
                QListWidget#server_list::item:hover {{ background-color: #35393f; color: #dcddde; }}
                QListWidget#server_list::item:selected {{ background-color: #4752c4; color: #ffffff; font-weight: bold; }}
                
                QFrame#floating_profile {{ background-color: #232428; border-radius: 12px; border: 1px solid #1e1f22; }}
                QLabel#profile_avatar {{ background-color: #5865f2; border-radius: 20px; color: white; font-size: 20px; }}
                QLabel#profile_user {{ color: #ffffff; font-weight: bold; font-size: 14px; }}
                QLabel#profile_email {{ color: #949ba4; font-size: 11px; }}
                
                QPushButton#btn_settings {{ background: transparent; color: #dcddde; border: none; border-radius: 6px; font-size: 16px; }}
                QPushButton#btn_settings:hover {{ background-color: #35393f; color: #ffffff; }}
                QPushButton#btn_mic {{ background-color: {mic_bg}; color: white if "{mic_bg}" != "transparent" else "#dcddde"; border: none; border-radius: 6px; font-size: 16px; }}
                QPushButton#btn_mic:hover {{ background-color: #35393f if "{mic_bg}" == "transparent" else "#c9383b"; color: #ffffff; }}
                QPushButton#btn_deafen {{ background-color: {deaf_bg}; color: white if "{deaf_bg}" != "transparent" else "#dcddde"; border: none; border-radius: 6px; font-size: 16px; }}
                QPushButton#btn_deafen:hover {{ background-color: #35393f if "{deaf_bg}" == "transparent" else "#c9383b"; color: #ffffff; }}

                QFrame#content_area {{ background-color: #313338; }}
                QFrame#header {{ background-color: #313338; border-bottom: 1px solid #282b30; }}
                QLabel#channel_name {{ color: #ffffff; font-size: 20px; font-weight: 800; }}
                QPushButton#theme_btn {{ background-color: #1e2124; color: #dcddde; border: 1px solid #444; border-radius: 6px; padding: 6px 12px; font-weight: bold; }}
                QPushButton#theme_btn:hover {{ background-color: #444; }}
                
                QPushButton#header_toggle_btn {{ background-color: transparent; color: #ffffff; font-size: 22px; border: none; font-weight: bold; }}
                QPushButton#header_toggle_btn:hover {{ color: #5865f2; }}
                
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
                
                QPushButton#secondary_btn {{ background-color: #2b2d31; color: #dcddde; border: 1px solid #444; border-radius: 6px; padding: 10px; font-weight: bold; font-size: 13px; }}
                QPushButton#secondary_btn:hover {{ background-color: #35393f; }}

                QFrame#payment_box {{ background-color: #2b2d31; border: 1px solid #4da3ff; border-radius: 16px; }}
                QLabel#pay_title {{ color: #4da3ff; font-size: 22px; font-weight: bold; }}
                QLabel#pay_price {{ color: #ffffff; font-size: 36px; font-weight: 900; }}
                QLabel#pay_item {{ color: #dcddde; font-size: 15px; font-weight: 500; margin-bottom: 8px; }}
                
                QFrame#channel_sidebar {{ background-color: #2b2d31; border-right: 1px solid #1e1f22; }}
                QLabel#srv_title {{ color: #ffffff; font-size: 18px; font-weight: 800; border-bottom: 1px solid #1e1f22; padding-bottom: 15px; }}
                QListWidget#channel_list {{ background: transparent; border: none; outline: none; }}
                QListWidget#channel_list::item {{ color: #949ba4; padding: 8px 10px; border-radius: 4px; }}
                QListWidget#channel_list::item:hover {{ background-color: #35393f; color: #dcddde; }}
                QListWidget#channel_list::item:selected {{ background-color: #404249; color: #ffffff; font-weight: bold; }}
                
                QFrame#chat_area {{ background-color: #313338; }}
                QListWidget#msg_list {{ background: transparent; border: none; outline: none; color: #dcddde; }}
                QFrame#chat_input_frame {{ background-color: #383a40; border-radius: 8px; }}
                QLineEdit#chat_input {{ background: transparent; border: none; color: #dcddde; font-size: 14px; padding-left: 10px; }}
                
                QLineEdit {{ background-color: #1e1f22; border: 1px solid #444; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #ffffff; }}
                QLineEdit:focus {{ border: 1px solid #5865f2; }}
                
                QListWidget#friends_list {{ background: transparent; border: none; outline: none; }}
                QListWidget#friends_list::item {{ background-color: #2b2d31; padding: 15px; border-radius: 8px; margin-bottom: 8px; color: #dcddde; }}
                QListWidget#friends_list::item:hover {{ background-color: #35393f; }}
                QPushButton#tab_btn_active {{ background-color: #404249; color: white; border-radius: 6px; padding: 8px 15px; font-weight: bold; border: none; }}
                QPushButton#tab_btn {{ background-color: transparent; color: #949ba4; border-radius: 6px; padding: 8px 15px; font-weight: bold; border: none; }}
                QPushButton#tab_btn:hover {{ background-color: #35393f; color: #dcddde; }}
                QLineEdit#search_input {{ background-color: #1e1f22; border: 1px solid #444; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #ffffff; }}
                QLineEdit#search_input:focus {{ border: 1px solid #5865f2; }}
            """)
        else:
            self.setStyleSheet(f"""
                /* YENİ: AÇIK TEMA BUG'I İÇİN GLOBAL ARKA PLAN ZORLAMASI */
                QWidget#dashboard_main, QWidget#page_bg, QStackedWidget#main_stack,
                QWidget#selection_page_main, QWidget#standard_page_main, QWidget#enterprise_page_main,
                QWidget#setup_page_main, QWidget#active_server_main, QWidget#friends_page_main {{ 
                    background-color: #ffffff; color: #060607; 
                }}
                QWidget#page_bg QLabel {{ color: #060607; }}
                
                QFrame#sidebar {{ background-color: #f2f3f5; border-right: 1px solid #e3e5e8; }}
                QLabel#logo_text {{ color: #060607; font-size: 18px; font-weight: 800; }}
                QLabel#menu_title {{ color: #5c5e66; font-size: 11px; font-weight: bold; margin-top: 10px; }}
                QListWidget#server_list {{ background: transparent; border: none; outline: none; }}
                QListWidget#server_list::item {{ color: #4e5058; padding: 10px 15px; border-radius: 6px; margin-bottom: 2px;}}
                QListWidget#server_list::item:hover {{ background-color: #e3e5e8; color: #060607; }}
                QListWidget#server_list::item:selected {{ background-color: #1877f2; color: #ffffff; font-weight: bold; }}
                
                QFrame#floating_profile {{ background-color: #ffffff; border-radius: 12px; border: 1px solid #e3e5e8; }}
                QLabel#profile_avatar {{ background-color: #1877f2; border-radius: 20px; color: white; font-size: 20px; }}
                QLabel#profile_user {{ color: #060607; font-weight: bold; font-size: 14px; }}
                QLabel#profile_email {{ color: #5c5e66; font-size: 11px; }}
                
                QPushButton#btn_settings {{ background: transparent; color: #4e5058; border: none; border-radius: 6px; font-size: 16px; }}
                QPushButton#btn_settings:hover {{ background-color: #e3e5e8; color: #060607; }}
                QPushButton#btn_mic {{ background-color: {mic_bg}; color: white if "{mic_bg}" != "transparent" else "#4e5058"; border: none; border-radius: 6px; font-size: 16px; }}
                QPushButton#btn_mic:hover {{ background-color: #e3e5e8 if "{mic_bg}" == "transparent" else "#c9383b"; color: #060607 if "{mic_bg}" == "transparent" else "#ffffff"; }}
                QPushButton#btn_deafen {{ background-color: {deaf_bg}; color: white if "{deaf_bg}" != "transparent" else "#4e5058"; border: none; border-radius: 6px; font-size: 16px; }}
                QPushButton#btn_deafen:hover {{ background-color: #e3e5e8 if "{deaf_bg}" == "transparent" else "#c9383b"; color: #060607 if "{deaf_bg}" == "transparent" else "#ffffff"; }}

                QFrame#content_area {{ background-color: #ffffff; }}
                QFrame#header {{ background-color: #ffffff; border-bottom: 1px solid #e3e5e8; }}
                QLabel#channel_name {{ color: #060607; font-size: 20px; font-weight: 800; }}
                QPushButton#theme_btn {{ background-color: #f2f3f5; color: #4e5058; border: 1px solid #ccc; border-radius: 6px; padding: 6px 12px; font-weight: bold; }}
                QPushButton#theme_btn:hover {{ background-color: #e3e5e8; }}
                
                QPushButton#header_toggle_btn {{ background-color: transparent; color: #060607; font-size: 22px; border: none; font-weight: bold; }}
                QPushButton#header_toggle_btn:hover {{ color: #1877f2; }}
                
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
                QPushButton#secondary_btn {{ background-color: #f8f9fa; color: #4e5058; border: 1px solid #ccc; border-radius: 6px; padding: 10px; font-weight: bold; font-size: 13px; }}
                QPushButton#secondary_btn:hover {{ background-color: #e3e5e8; }}

                QFrame#payment_box {{ background-color: #f8f9fa; border: 1px solid #1877f2; border-radius: 16px; }}
                QLabel#pay_title {{ color: #1877f2; font-size: 22px; font-weight: bold; }}
                QLabel#pay_price {{ color: #060607; font-size: 36px; font-weight: 900; }}
                QLabel#pay_item {{ color: #4e5058; font-size: 15px; font-weight: 500; margin-bottom: 8px; }}
                
                QFrame#channel_sidebar {{ background-color: #f2f3f5; border-right: 1px solid #e3e5e8; }}
                QLabel#srv_title {{ color: #060607; font-size: 18px; font-weight: 800; border-bottom: 1px solid #e3e5e8; padding-bottom: 15px; }}
                QListWidget#channel_list {{ background: transparent; border: none; outline: none; }}
                QListWidget#channel_list::item {{ color: #4e5058; padding: 8px 10px; border-radius: 4px; }}
                QListWidget#channel_list::item:hover {{ background-color: #e3e5e8; color: #060607; }}
                QListWidget#channel_list::item:selected {{ background-color: #d4d7dc; color: #060607; font-weight: bold; }}
                
                QFrame#chat_area {{ background-color: #ffffff; }}
                QListWidget#msg_list {{ background: transparent; border: none; outline: none; color: #060607; }}
                QFrame#chat_input_frame {{ background-color: #ebedef; border-radius: 8px; }}
                QLineEdit#chat_input {{ background: transparent; border: none; color: #060607; font-size: 14px; padding-left: 10px; }}

                QLineEdit {{ background-color: #f2f3f5; border: 1px solid #ccc; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #060607; }}
                QLineEdit:focus {{ border: 1px solid #1877f2; background-color: #ffffff; }}
                
                QListWidget#friends_list {{ background: transparent; border: none; outline: none; }}
                QListWidget#friends_list::item {{ background-color: #f8f9fa; border: 1px solid #e3e5e8; padding: 15px; border-radius: 8px; margin-bottom: 8px; color: #060607; }}
                QListWidget#friends_list::item:hover {{ background-color: #e3e5e8; }}
                QPushButton#tab_btn_active {{ background-color: #e3e5e8; color: #060607; border-radius: 6px; padding: 8px 15px; font-weight: bold; border: none; }}
                QPushButton#tab_btn {{ background-color: transparent; color: #5c5e66; border-radius: 6px; padding: 8px 15px; font-weight: bold; border: none; }}
                QPushButton#tab_btn:hover {{ background-color: #e3e5e8; color: #060607; }}
                QLineEdit#search_input {{ background-color: #f2f3f5; border: 1px solid #ccc; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #060607; }}
                QLineEdit#search_input:focus {{ border: 1px solid #1877f2; background-color: #ffffff; }}
            """)