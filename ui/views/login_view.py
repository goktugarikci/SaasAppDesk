# ui/views/login_view.py
import webbrowser
import os
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QMessageBox, QCheckBox, QStackedWidget, QFrame, QSizePolicy, QComboBox, QProgressBar)
from PySide6.QtCore import Qt, QSettings, QThread, Signal, QSize
from PySide6.QtGui import QMovie, QPainter, QPixmap, QIcon

from api.auth_api import login, register, get_google_auth_url, verify_google_code

LANGUAGES = {
    'TR': {
        'log_title': "MySaaS'a Giriş Yap", 'email_ph': "E-posta adresi", 'pw_ph': "Şifre",
        'remember': "Oturumu açık tut", 'btn_login': "Giriş Yap", 'or_lbl': "──────  veya  ──────",
        'btn_google': "G   Google ile Devam Et", 'wait_google': "Bekleniyor... (İptal)",
        'switch_reg': "Hesabın yok mu? Yeni hesap oluştur", 'reg_title': "Yeni Hesap Oluştur",
        'name_ph': "Ad Soyad", 'reg_pw_ph': "Yeni Şifre", 'btn_reg': "Kayıt Ol",
        'switch_log': "Zaten hesabın var mı? Giriş yap",
        'load_log': "Giriş Yapılıyor...", 'load_log_sub': "Kimlik bilgileriniz güvenle doğrulanıyor",
        'load_reg': "Hesap Oluşturuluyor...", 'load_reg_sub': "Çalışma alanınız sizin için hazırlanıyor",
        'load_google': "Oturum Açılıyor...", 'load_google_sub': "Google verileriniz senkronize ediliyor",
        'theme_dark': "🌙 Koyu Tema", 'theme_light': "☀️ Açık Tema",
        'feat_main_title': "MySaaS'ın Gücünü Keşfedin",
        'plan_free': "Bireysel Kullanıcı", 'price_free': "$0.00 / Aylık",
        'f1': "✓ 1 Sunucu (Server) Sınırı", 'f2': "✓ 1 Çalışma Panosu (TodoList)", 'f3': "✓ Standart Mesajlaşma", 'f4': "✓ 100 MB Dosya Yükleme Sınırı",
        'plan_ent': "Enterprise (Premium)", 'price_ent': "$9.99 / Aylık",
        'e1': "★ Sınırsız Sunucu (Server)", 'e2': "★ Sınırsız Çalışma Panosu", 'e3': "★ Gelişmiş Görüntülü Arama", 'e4': "★ Sınırsız Yükleme & 7/24 Destek"
    },
    'EN': {
        'log_title': "Login to MySaaS", 'email_ph': "Email address", 'pw_ph': "Password",
        'remember': "Keep me signed in", 'btn_login': "Login", 'or_lbl': "──────  or  ──────",
        'btn_google': "G   Continue with Google", 'wait_google': "Waiting... (Cancel)",
        'switch_reg': "Don't have an account? Create one", 'reg_title': "Create New Account",
        'name_ph': "Full Name", 'reg_pw_ph': "New Password", 'btn_reg': "Sign Up",
        'switch_log': "Already have an account? Login",
        'load_log': "Logging in...", 'load_log_sub': "Securely verifying your credentials",
        'load_reg': "Creating Account...", 'load_reg_sub': "Preparing your workspace",
        'load_google': "Signing in...", 'load_google_sub': "Synchronizing your Google data",
        'theme_dark': "🌙 Dark Mode", 'theme_light': "☀️ Light Mode",
        'feat_main_title': "Discover the Power of MySaaS",
        'plan_free': "Individual Plan", 'price_free': "$0.00 / Month",
        'f1': "✓ 1 Server Limit", 'f2': "✓ 1 Workspace Board (TodoList)", 'f3': "✓ Standard Messaging", 'f4': "✓ 100 MB File Upload Limit",
        'plan_ent': "Enterprise (Premium)", 'price_ent': "$9.99 / Month",
        'e1': "★ Unlimited Servers", 'e2': "★ Unlimited Workspace Boards", 'e3': "★ Advanced Video Calling", 'e4': "★ Unlimited Uploads & 24/7 Support"
    },
    'GER': {
        'log_title': "Bei MySaaS anmelden", 'email_ph': "E-Mail-Adresse", 'pw_ph': "Passwort",
        'remember': "Angemeldet bleiben", 'btn_login': "Anmelden", 'or_lbl': "──────  oder  ──────",
        'btn_google': "G   Weiter mit Google", 'wait_google': "Warten... (Abbrechen)",
        'switch_reg': "Kein Konto? Neues erstellen", 'reg_title': "Neues Konto erstellen",
        'name_ph': "Vollständiger Name", 'reg_pw_ph': "Neues Passwort", 'btn_reg': "Registrieren",
        'switch_log': "Hast du schon ein Konto? Anmelden",
        'load_log': "Anmeldung läuft...", 'load_log_sub': "Ihre Anmeldedaten werden sicher überprüft",
        'load_reg': "Konto wird erstellt...", 'load_reg_sub': "Ihr Arbeitsbereich wird vorbereitet",
        'load_google': "Anmelden...", 'load_google_sub': "Ihre Google-Daten werden synchronisiert",
        'theme_dark': "🌙 Dunkel", 'theme_light': "☀️ Hell",
        'feat_main_title': "Entdecken Sie MySaaS",
        'plan_free': "Einzelperson", 'price_free': "$0.00 / Monat",
        'f1': "✓ Limit von 1 Server", 'f2': "✓ 1 Arbeitsbereich (TodoList)", 'f3': "✓ Standardnachrichten", 'f4': "✓ 100 MB Datei-Upload-Limit",
        'plan_ent': "Enterprise (Premium)", 'price_ent': "$9.99 / Monat",
        'e1': "★ Unbegrenzte Server", 'e2': "★ Unbegrenzte Arbeitsbereiche", 'e3': "★ Erweiterte Videoanrufe", 'e4': "★ Unbegrenzte Uploads & Support"
    }
}

class AuthWorkerThread(QThread):
    finished_signal = Signal(bool, object)
    def __init__(self, action, *args):
        super().__init__()
        self.action = action; self.args = args
    def run(self):
        if self.action == 'login': success, data = login(*self.args)
        elif self.action == 'register': success, data = register(*self.args)
        self.finished_signal.emit(success, data)

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass 
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        self.send_response(200); self.send_header('Content-type', 'text/html; charset=utf-8'); self.end_headers()
        if 'code' in query:
            self.server.auth_code = query['code'][0]
            self.wfile.write(b"<html><body style='text-align:center; font-family:sans-serif; margin-top:50px;'><h2 style='color:#28a745;'>Success!</h2><script>setTimeout(function(){window.close();}, 2000);</script></body></html>")
        else:
            self.wfile.write(b"<html><body><h2 style='color:red;'>Cancelled!</h2></body></html>")

class OAuthThread(QThread):
    finished_signal = Signal(str)
    def __init__(self):
        super().__init__(); self._abort = False 
    def run(self):
        try:
            server = HTTPServer(('127.0.0.1', 8081), OAuthCallbackHandler)
            server.timeout = 1.0; server.auth_code = None; attempts = 0
            while not self._abort and attempts < 120 and server.auth_code is None:
                server.handle_request(); attempts += 1
            self.finished_signal.emit(server.auth_code if server.auth_code else "")
            server.server_close()
        except Exception: self.finished_signal.emit("")
    def abort(self): self._abort = True

class LoginView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.settings = QSettings("MySaaS", "DesktopClient")
        
        # Dil ve Temayı sistemden oku (YENİ)
        self.is_dark_mode = self.settings.value("is_dark_mode", False, type=bool)
        self.current_lang = self.settings.value("language", "TR")
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        bg_path = os.path.join(base_dir, 'assets', 'background.png')
        self.bg_pixmap = QPixmap(bg_path)

        self.setup_ui()
        self.sync_settings() # İlk ayarları uygula
        self.load_saved_session()

    def reset_form(self):
        """Çıkış yapıldığında formdaki bilgileri temizler (YENİ)"""
        self.login_email.clear()
        self.login_pw.clear()
        self.reg_name.clear()
        self.reg_email.clear()
        self.reg_pw.clear()
        self.remember_cb.setChecked(False)
        self.stacked_widget.setCurrentWidget(self.login_widget)

    def sync_settings(self):
        """Dashboard'dan dönüşlerde dil ve temayı tekrar eşitler (YENİ)"""
        self.is_dark_mode = self.settings.value("is_dark_mode", False, type=bool)
        self.current_lang = self.settings.value("language", "TR")
        
        self.apply_theme()
        self.update_texts()
        
        self.lang_cb.blockSignals(True)
        self.lang_cb.setCurrentText(self.current_lang)
        self.lang_cb.blockSignals(False)

    def paintEvent(self, event):
        if not self.bg_pixmap.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            scaled = self.bg_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            painter = QPainter(self)
            painter.fillRect(self.rect(), Qt.black if self.is_dark_mode else Qt.lightGray)

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        self.top_bar = QHBoxLayout()
        self.top_bar.addStretch() 

        self.theme_btn = QPushButton()
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self.toggle_theme)

        self.lang_cb = QComboBox()
        self.lang_cb.setCursor(Qt.PointingHandCursor)
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        tr_path = os.path.join(base_dir, 'assets', 'tr.png').replace('\\', '/')
        en_path = os.path.join(base_dir, 'assets', 'en.png').replace('\\', '/')
        ger_path = os.path.join(base_dir, 'assets', 'ger.png').replace('\\', '/')
        
        self.lang_cb.addItem(QIcon(tr_path), "TR")
        self.lang_cb.addItem(QIcon(en_path), "EN")
        self.lang_cb.addItem(QIcon(ger_path), "GER")
        self.lang_cb.setIconSize(QSize(20, 15)) 
        self.lang_cb.currentTextChanged.connect(self.change_language)

        self.top_bar.addWidget(self.theme_btn)
        self.top_bar.addWidget(self.lang_cb)
        self.main_layout.addLayout(self.top_bar)

        self.main_layout.addStretch() 

        self.content_box = QFrame()
        self.content_box.setObjectName("content_box")
        self.content_box.setFixedWidth(850) 
        self.content_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        content_layout = QHBoxLayout(self.content_box)
        content_layout.setContentsMargins(35, 35, 35, 35)
        content_layout.setSpacing(30) 

        self.features_widget = self.create_features_ui()
        content_layout.addWidget(self.features_widget, 1) 

        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.VLine)
        self.divider.setObjectName("divider_line")
        content_layout.addWidget(self.divider)

        self.stacked_widget = QStackedWidget()
        self.login_widget = self.create_login_ui()
        self.register_widget = self.create_register_ui()
        self.loading_widget = self.create_loading_ui()

        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.register_widget)
        self.stacked_widget.addWidget(self.loading_widget)

        content_layout.addWidget(self.stacked_widget, 1) 
        
        box_layout = QHBoxLayout()
        box_layout.addStretch()
        box_layout.addWidget(self.content_box)
        box_layout.addStretch()
        
        self.main_layout.addLayout(box_layout)
        self.main_layout.addStretch() 

    def create_features_ui(self):
        widget = QWidget(); layout = QVBoxLayout(widget); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(15)
        self.lbl_feat_title = QLabel(); self.lbl_feat_title.setObjectName("feature_title"); self.lbl_feat_title.setAlignment(Qt.AlignLeft)

        self.free_card = QFrame(); self.free_card.setObjectName("free_card")
        free_layout = QVBoxLayout(self.free_card); free_layout.setSpacing(6)
        self.lbl_plan_free = QLabel(); self.lbl_plan_free.setObjectName("plan_title")
        self.lbl_price_free = QLabel(); self.lbl_price_free.setObjectName("plan_price") 
        self.lbl_f1 = QLabel(); self.lbl_f1.setObjectName("plan_item")
        self.lbl_f2 = QLabel(); self.lbl_f2.setObjectName("plan_item")
        self.lbl_f3 = QLabel(); self.lbl_f3.setObjectName("plan_item")
        self.lbl_f4 = QLabel(); self.lbl_f4.setObjectName("plan_item")
        free_layout.addWidget(self.lbl_plan_free); free_layout.addWidget(self.lbl_price_free); free_layout.addSpacing(5)
        free_layout.addWidget(self.lbl_f1); free_layout.addWidget(self.lbl_f2); free_layout.addWidget(self.lbl_f3); free_layout.addWidget(self.lbl_f4)

        self.ent_card = QFrame(); self.ent_card.setObjectName("ent_card")
        ent_layout = QVBoxLayout(self.ent_card); ent_layout.setSpacing(6)
        self.lbl_plan_ent = QLabel(); self.lbl_plan_ent.setObjectName("plan_title_ent")
        self.lbl_price_ent = QLabel(); self.lbl_price_ent.setObjectName("plan_price_ent") 
        self.lbl_e1 = QLabel(); self.lbl_e1.setObjectName("plan_item_ent")
        self.lbl_e2 = QLabel(); self.lbl_e2.setObjectName("plan_item_ent")
        self.lbl_e3 = QLabel(); self.lbl_e3.setObjectName("plan_item_ent")
        self.lbl_e4 = QLabel(); self.lbl_e4.setObjectName("plan_item_ent")
        ent_layout.addWidget(self.lbl_plan_ent); ent_layout.addWidget(self.lbl_price_ent); ent_layout.addSpacing(5)
        ent_layout.addWidget(self.lbl_e1); ent_layout.addWidget(self.lbl_e2); ent_layout.addWidget(self.lbl_e3); ent_layout.addWidget(self.lbl_e4)

        layout.addStretch(); layout.addWidget(self.lbl_feat_title); layout.addWidget(self.free_card); layout.addWidget(self.ent_card); layout.addStretch()
        return widget

    def create_login_ui(self):
        widget = QWidget(); widget.setAttribute(Qt.WA_TranslucentBackground); layout = QVBoxLayout(widget); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(12); layout.addStretch() 
        self.lbl_log_title = QLabel(); self.lbl_log_title.setStyleSheet("font-size: 24px; font-weight: bold;"); self.lbl_log_title.setAlignment(Qt.AlignCenter)
        self.login_email = QLineEdit(); self.login_pw = QLineEdit(); self.login_pw.setEchoMode(QLineEdit.Password); self.remember_cb = QCheckBox()
        self.btn_login = QPushButton(); self.btn_login.setObjectName("primary_btn"); self.btn_login.clicked.connect(self.handle_login)
        self.lbl_or = QLabel(); self.lbl_or.setAlignment(Qt.AlignCenter)
        self.google_btn_log = QPushButton(); self.google_btn_log.setObjectName("google_btn"); self.google_btn_log.clicked.connect(self.handle_google_login)
        self.btn_switch_reg = QPushButton(); self.btn_switch_reg.setObjectName("switch_btn"); self.btn_switch_reg.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.register_widget))

        layout.addWidget(self.lbl_log_title); layout.addWidget(self.login_email); layout.addWidget(self.login_pw); layout.addWidget(self.remember_cb)
        layout.addWidget(self.btn_login); layout.addWidget(self.lbl_or); layout.addWidget(self.google_btn_log); layout.addWidget(self.btn_switch_reg, alignment=Qt.AlignCenter); layout.addStretch()
        return widget

    def create_register_ui(self):
        widget = QWidget(); widget.setAttribute(Qt.WA_TranslucentBackground); layout = QVBoxLayout(widget); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(12); layout.addStretch()
        self.lbl_reg_title = QLabel(); self.lbl_reg_title.setStyleSheet("font-size: 24px; font-weight: bold;"); self.lbl_reg_title.setAlignment(Qt.AlignCenter)
        self.reg_name = QLineEdit(); self.reg_email = QLineEdit(); self.reg_pw = QLineEdit(); self.reg_pw.setEchoMode(QLineEdit.Password)
        self.btn_reg = QPushButton(); self.btn_reg.setObjectName("success_btn"); self.btn_reg.clicked.connect(self.handle_register)
        self.btn_switch_log = QPushButton(); self.btn_switch_log.setObjectName("switch_btn"); self.btn_switch_log.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.login_widget))

        layout.addWidget(self.lbl_reg_title); layout.addWidget(self.reg_name); layout.addWidget(self.reg_email); layout.addWidget(self.reg_pw)
        layout.addWidget(self.btn_reg); layout.addWidget(self.btn_switch_log, alignment=Qt.AlignCenter); layout.addStretch()
        return widget

    def create_loading_ui(self):
        widget = QWidget(); widget.setAttribute(Qt.WA_TranslucentBackground); layout = QVBoxLayout(widget); layout.setContentsMargins(0, 0, 0, 0); layout.setAlignment(Qt.AlignCenter); layout.setSpacing(15); layout.addStretch()
        anim_container = QWidget(); anim_layout = QVBoxLayout(anim_container); anim_layout.setAlignment(Qt.AlignCenter); anim_layout.setContentsMargins(0,0,0,0)
        
        self.gif_label = QLabel(); self.gif_label.setAlignment(Qt.AlignCenter)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        gif_path = os.path.join(base_dir, 'assets', 'Loading_2.gif').replace('\\', '/')
        self.fallback_bar = QProgressBar(); self.fallback_bar.setRange(0, 0); self.fallback_bar.setFixedWidth(200); self.fallback_bar.setFixedHeight(4); self.fallback_bar.setTextVisible(False)

        if os.path.exists(gif_path):
            self.loading_movie = QMovie(gif_path); self.loading_movie.setScaledSize(QSize(64, 64))
            self.gif_label.setMovie(self.loading_movie); anim_layout.addWidget(self.gif_label); self.fallback_bar.hide()
        else: self.loading_movie = None; anim_layout.addWidget(self.fallback_bar)

        self.lbl_load_title = QLabel(); self.lbl_load_title.setStyleSheet("font-size: 20px; font-weight: 800;"); self.lbl_load_title.setAlignment(Qt.AlignCenter)
        self.lbl_load_sub = QLabel(); self.lbl_load_sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(anim_container); layout.addWidget(self.lbl_load_title); layout.addWidget(self.lbl_load_sub); layout.addStretch()
        return widget

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.settings.setValue("is_dark_mode", self.is_dark_mode) # YENİ: Sisteme Kaydet
        self.apply_theme()
        self.update_texts()

    def change_language(self, lang_code):
        self.current_lang = lang_code
        self.settings.setValue("language", self.current_lang) # YENİ: Sisteme Kaydet
        self.update_texts()

    def update_texts(self):
        t = LANGUAGES[self.current_lang]
        self.lbl_log_title.setText(t['log_title'])
        self.login_email.setPlaceholderText(t['email_ph'])
        self.login_pw.setPlaceholderText(t['pw_ph'])
        self.remember_cb.setText(t['remember'])
        self.btn_login.setText(t['btn_login'])
        self.lbl_or.setText(t['or_lbl'])
        if not (hasattr(self, 'oauth_thread') and self.oauth_thread.isRunning()): self.google_btn_log.setText(t['btn_google'])
        self.btn_switch_reg.setText(t['switch_reg'])
        self.lbl_reg_title.setText(t['reg_title'])
        self.reg_name.setPlaceholderText(t['name_ph'])
        self.reg_email.setPlaceholderText(t['email_ph'])
        self.reg_pw.setPlaceholderText(t['reg_pw_ph'])
        self.btn_reg.setText(t['btn_reg'])
        self.btn_switch_log.setText(t['switch_log'])
        self.theme_btn.setText(t['theme_light'] if self.is_dark_mode else t['theme_dark'])
        self.lbl_feat_title.setText(t['feat_main_title'])
        self.lbl_plan_free.setText(t['plan_free']); self.lbl_price_free.setText(t['price_free'])
        self.lbl_f1.setText(t['f1']); self.lbl_f2.setText(t['f2']); self.lbl_f3.setText(t['f3']); self.lbl_f4.setText(t['f4'])
        self.lbl_plan_ent.setText(t['plan_ent']); self.lbl_price_ent.setText(t['price_ent'])
        self.lbl_e1.setText(t['e1']); self.lbl_e2.setText(t['e2']); self.lbl_e3.setText(t['e3']); self.lbl_e4.setText(t['e4'])

    def apply_theme(self):
        if self.is_dark_mode:
            self.content_box.setStyleSheet("""
                QFrame#content_box { background-color: rgba(30, 35, 40, 230); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.1); }
                QLabel { color: #f0f2f5; font-family: 'Segoe UI', Arial; background: transparent; }
                QLineEdit { background-color: rgba(0, 0, 0, 100); border: 1px solid rgba(255,255,255,0.2); border-radius: 6px; padding: 10px; font-size: 13px; color: #ffffff; }
                QLineEdit:focus { border: 2px solid #1877f2; background-color: rgba(0, 0, 0, 150); }
                QCheckBox { color: #f0f2f5; font-size: 12px; spacing: 8px; font-weight: 500; background: transparent;}
                QCheckBox::indicator { width: 16px; height: 16px; border-radius: 4px; border: 1px solid #777; background-color: rgba(0, 0, 0, 100); }
                QCheckBox::indicator:checked { background-color: #1877f2; border: 1px solid #1877f2; }
                QPushButton#primary_btn { background-color: #1877f2; color: white; border-radius: 6px; padding: 10px; font-size: 14px; font-weight: bold; border: none; }
                QPushButton#primary_btn:hover { background-color: #166fe5; }
                QPushButton#success_btn { background-color: #28a745; color: white; border-radius: 6px; padding: 10px; font-size: 14px; font-weight: bold; border: none; }
                QPushButton#success_btn:hover { background-color: #218838; }
                QPushButton#google_btn { background-color: #ea4335; color: white; border-radius: 6px; padding: 10px; font-size: 14px; font-weight: bold; border: none; }
                QPushButton#google_btn:hover { background-color: #d33828; }
                QPushButton#switch_btn { color: #4da3ff; background: transparent; border: none; font-size: 13px; font-weight: 600; }
                QPushButton#switch_btn:hover { text-decoration: underline; }
                QFrame#divider_line { color: rgba(255, 255, 255, 0.1); }
                QLabel#feature_title { font-size: 22px; font-weight: bold; color: #ffffff; margin-bottom: 5px; }
                QFrame#free_card { background-color: rgba(0,0,0,0.2); border-radius: 8px; padding: 15px; border: 1px solid rgba(255,255,255,0.05); }
                QLabel#plan_title { font-size: 14px; font-weight: bold; color: #a0a0a0; }
                QLabel#plan_price { font-size: 22px; font-weight: 800; color: #ffffff; } 
                QLabel#plan_item { font-size: 13px; color: #cccccc; }
                QFrame#ent_card { background-color: rgba(24,119,242,0.15); border-radius: 8px; padding: 15px; border: 1px solid rgba(24,119,242,0.5); }
                QLabel#plan_title_ent { font-size: 14px; font-weight: bold; color: #4da3ff; }
                QLabel#plan_price_ent { font-size: 22px; font-weight: 800; color: #4da3ff; } 
                QLabel#plan_item_ent { font-size: 13px; color: #f0f2f5; font-weight: 500; }
            """)
            self.lbl_or.setStyleSheet("color: #888888; font-size: 12px; font-weight: bold;")
            self.lbl_load_sub.setStyleSheet("font-size: 13px; color: #aaaaaa; font-weight: 500;")
            self.fallback_bar.setStyleSheet("QProgressBar { background-color: #333; border-radius: 2px; } QProgressBar::chunk { background-color: #1877f2; border-radius: 2px; }")
            self.theme_btn.setStyleSheet("background-color: rgba(30,35,40,220); color: white; border-radius: 6px; padding: 6px 15px; font-weight: bold; border: 1px solid rgba(255,255,255,0.1);")
            self.lang_cb.setStyleSheet("""
                QComboBox { background-color: rgba(30,35,40,220); color: #f0f2f5; border-radius: 6px; padding: 6px 10px 6px 15px; font-weight: bold; border: 1px solid rgba(255,255,255,0.1); }
                QComboBox:hover { background-color: rgba(40,45,50,255); border: 1px solid rgba(24,119,242,0.5); }
                QComboBox::drop-down { border: none; width: 25px; } 
                QComboBox QAbstractItemView { background-color: #1e2328; color: #f0f2f5; border: 1px solid #444; border-radius: 6px; selection-background-color: transparent; outline: none; padding: 4px; }
                QComboBox QAbstractItemView::item { padding: 8px 10px; border-radius: 4px; min-height: 25px; }
                QComboBox QAbstractItemView::item:hover { background-color: #2a3038; color: #4da3ff; }
            """)
        else:
            self.content_box.setStyleSheet("""
                QFrame#content_box { background-color: rgba(255, 255, 255, 240); border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.8); }
                QLabel { color: #1a1a1a; font-family: 'Segoe UI', Arial; background: transparent; }
                QLineEdit { background-color: rgba(255, 255, 255, 200); border: 1px solid rgba(0, 0, 0, 0.15); border-radius: 6px; padding: 10px; font-size: 13px; color: #1a1a1a; }
                QLineEdit:focus { border: 2px solid #1877f2; background-color: rgba(255, 255, 255, 255); }
                QCheckBox { color: #333333; font-size: 12px; spacing: 8px; font-weight: 500; background: transparent;}
                QCheckBox::indicator { width: 16px; height: 16px; border-radius: 4px; border: 1px solid #a0a0a0; background-color: rgba(255, 255, 255, 200); }
                QCheckBox::indicator:checked { background-color: #1877f2; border: 1px solid #1877f2; }
                QPushButton#primary_btn { background-color: #1877f2; color: white; border-radius: 6px; padding: 10px; font-size: 14px; font-weight: bold; border: none; }
                QPushButton#primary_btn:hover { background-color: #166fe5; }
                QPushButton#success_btn { background-color: #28a745; color: white; border-radius: 6px; padding: 10px; font-size: 14px; font-weight: bold; border: none; }
                QPushButton#success_btn:hover { background-color: #218838; }
                QPushButton#google_btn { background-color: #ea4335; color: white; border-radius: 6px; padding: 10px; font-size: 14px; font-weight: bold; border: none; }
                QPushButton#google_btn:hover { background-color: #d33828; }
                QPushButton#switch_btn { color: #1877f2; background: transparent; border: none; font-size: 13px; font-weight: 600; }
                QPushButton#switch_btn:hover { text-decoration: underline; }
                QFrame#divider_line { color: rgba(0, 0, 0, 0.1); }
                QLabel#feature_title { font-size: 22px; font-weight: bold; color: #1c1e21; margin-bottom: 5px; }
                QFrame#free_card { background-color: rgba(0,0,0,0.03); border-radius: 8px; padding: 15px; border: 1px solid rgba(0,0,0,0.05); }
                QLabel#plan_title { font-size: 14px; font-weight: bold; color: #606770; }
                QLabel#plan_price { font-size: 22px; font-weight: 800; color: #1c1e21; } 
                QLabel#plan_item { font-size: 13px; color: #444444; }
                QFrame#ent_card { background-color: rgba(24,119,242,0.08); border-radius: 8px; padding: 15px; border: 1px solid rgba(24,119,242,0.5); }
                QLabel#plan_title_ent { font-size: 14px; font-weight: bold; color: #1877f2; }
                QLabel#plan_price_ent { font-size: 22px; font-weight: 800; color: #1877f2; } 
                QLabel#plan_item_ent { font-size: 13px; color: #1c1e21; font-weight: 500; }
            """)
            self.lbl_or.setStyleSheet("color: #666666; font-size: 12px; font-weight: bold;")
            self.lbl_load_sub.setStyleSheet("font-size: 13px; color: #606770; font-weight: 500;")
            self.fallback_bar.setStyleSheet("QProgressBar { background-color: #e4e6eb; border-radius: 2px; } QProgressBar::chunk { background-color: #1877f2; border-radius: 2px; }")
            self.theme_btn.setStyleSheet("background-color: rgba(255,255,255,220); color: #1c1e21; border-radius: 6px; padding: 6px 15px; font-weight: bold; border: 1px solid rgba(0,0,0,0.1);")
            self.lang_cb.setStyleSheet("""
                QComboBox { background-color: rgba(255,255,255,220); color: #1c1e21; border-radius: 6px; padding: 6px 10px 6px 15px; font-weight: bold; border: 1px solid rgba(0,0,0,0.1); }
                QComboBox:hover { background-color: rgba(255,255,255,255); border: 1px solid rgba(24,119,242,0.5); }
                QComboBox::drop-down { border: none; width: 25px; } 
                QComboBox QAbstractItemView { background-color: #ffffff; color: #1c1e21; border: 1px solid #ccd0d5; border-radius: 6px; selection-background-color: transparent; outline: none; padding: 4px; }
                QComboBox QAbstractItemView::item { padding: 8px 10px; border-radius: 4px; min-height: 25px; }
                QComboBox QAbstractItemView::item:hover { background-color: #f0f2f5; color: #1877f2; }
            """)
        self.update()

    def handle_login(self):
        email = self.login_email.text().strip(); pw = self.login_pw.text().strip()
        if not email or not pw: return QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun.")
        
        t = LANGUAGES[self.current_lang]
        self.lbl_load_title.setText(t['load_log'])
        self.lbl_load_sub.setText(t['load_log_sub'])
        self.stacked_widget.setCurrentWidget(self.loading_widget)
        if hasattr(self, 'loading_movie') and self.loading_movie: self.loading_movie.start()

        self.auth_worker = AuthWorkerThread('login', email, pw)
        self.auth_worker.finished_signal.connect(self.on_login_finished)
        self.auth_worker.start()


    def on_login_finished(self, success, data):
        if hasattr(self, 'loading_movie') and self.loading_movie: 
            self.loading_movie.stop()
        
        if success:
            my_token = ""
            if isinstance(data, dict):
                my_token = data.get("token", "")
            elif isinstance(data, str):
                my_token = data

            if not my_token:
                QMessageBox.critical(self, "Token Hatası", "Giriş yapıldı ama sunucu token göndermedi!")
                self.stacked_widget.setCurrentWidget(self.login_widget)
                return

            pure_token = str(my_token).strip()
            self.settings.setValue("auth_token", pure_token)
            
            # --- YENİ: OTURUMU AÇIK TUT KONTROLÜ ---
            if hasattr(self, 'cb_remember') and self.cb_remember.isChecked():
                self.settings.setValue("remember_me", True)
            else:
                self.settings.setValue("remember_me", False)
            # --------------------------------------

            self.settings.sync() 
            self.main_window.show_dashboard()
        else:
            self.stacked_widget.setCurrentWidget(self.login_widget)
            QMessageBox.critical(self, "Hata", str(data))


    def handle_register(self):
        name = self.reg_name.text().strip(); email = self.reg_email.text().strip(); pw = self.reg_pw.text().strip()
        if not name or not email or not pw: return QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun.")
        
        t = LANGUAGES[self.current_lang]
        self.lbl_load_title.setText(t['load_reg'])
        self.lbl_load_sub.setText(t['load_reg_sub'])
        self.stacked_widget.setCurrentWidget(self.loading_widget)
        if hasattr(self, 'loading_movie') and self.loading_movie: self.loading_movie.start()

        self.auth_worker = AuthWorkerThread('register', name, email, pw)
        self.auth_worker.finished_signal.connect(self.on_register_finished)
        self.auth_worker.start()

    def on_register_finished(self, success, msg):
        if hasattr(self, 'loading_movie') and self.loading_movie: self.loading_movie.stop()
        self.stacked_widget.setCurrentWidget(self.login_widget)
        if success: QMessageBox.information(self, "Başarılı", msg)
        else: QMessageBox.critical(self, "Hata", msg)

    def handle_google_login(self):
        if hasattr(self, 'oauth_thread') and self.oauth_thread.isRunning():
            self.oauth_thread.abort(); return
        url = get_google_auth_url()
        if url:
            self.google_btn_log.setText(LANGUAGES[self.current_lang]['wait_google'])
            self.google_btn_log.setStyleSheet("background-color: #f39c12; color: white; border-radius: 6px; padding: 10px; font-weight: bold; border: none;")
            self.oauth_thread = OAuthThread()
            self.oauth_thread.finished_signal.connect(self.on_google_callback)
            self.oauth_thread.start()
            webbrowser.open(url)
        else: QMessageBox.critical(self, "Hata", "Bağlantı kurulamadı.")

    def on_google_callback(self, code):
        self.google_btn_log.setText(LANGUAGES[self.current_lang]['btn_google'])
        self.google_btn_log.setStyleSheet("") 
        if code:
            t = LANGUAGES[self.current_lang]
            self.lbl_load_title.setText(t['load_google']); self.lbl_load_sub.setText(t['load_google_sub'])
            self.stacked_widget.setCurrentWidget(self.loading_widget)
            if hasattr(self, 'loading_movie') and self.loading_movie: self.loading_movie.start()
            
            success, data = verify_google_code(code)
            
            if hasattr(self, 'loading_movie') and self.loading_movie: self.loading_movie.stop()
            self.stacked_widget.setCurrentWidget(self.login_widget)

            if success:
                self.settings.setValue("auth_token", data.get("token"))
                self.main_window.show_dashboard()
            else: QMessageBox.critical(self, "Hata", data)
        else: QMessageBox.warning(self, "Uyarı", "İşlem iptal edildi.")

    def load_saved_session(self):
        saved_token = self.settings.value("auth_token")
        if saved_token:
            from core import config
            config.CURRENT_TOKEN = saved_token
            self.main_window.show_dashboard()