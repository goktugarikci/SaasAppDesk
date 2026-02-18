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

# Dil dosyasından import (Eğer languages.py kullanıyorsanız)
try:
    from ui.resources.languages import DASHBOARD_LANGS as LANGUAGES
except ImportError:
    # Yedek Dil Tanımları (Dosya bulunamazsa çökmemesi için)
    LANGUAGES = {
        'TR': {'log_title': 'Giriş Yap', 'load_log': 'Giriş Yapılıyor...', 'load_reg': 'Kayıt Olunuyor...', 'btn_login': 'Giriş', 'btn_reg': 'Kayıt Ol'},
        'EN': {'log_title': 'Login', 'load_log': 'Logging in...', 'load_reg': 'Registering...', 'btn_login': 'Login', 'btn_reg': 'Register'}
    }

class AuthWorkerThread(QThread):
    finished_signal = Signal(bool, object)
    def __init__(self, action, *args):
        super().__init__()
        self.action = action; self.args = args
    def run(self):
        if self.action == 'login': success, data = login(*self.args)
        elif self.action == 'register': success, data = register(*self.args)
        else: success, data = False, "Invalid action"
        self.finished_signal.emit(success, data)

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass 
    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        self.send_response(200); self.end_headers()
        if 'code' in query:
            self.server.auth_code = query['code'][0]
            self.wfile.write(b"<script>window.close();</script>")
        else: self.wfile.write(b"Cancelled")

class OAuthThread(QThread):
    finished_signal = Signal(str)
    def __init__(self): super().__init__(); self._abort = False 
    def run(self):
        try:
            server = HTTPServer(('127.0.0.1', 8081), OAuthCallbackHandler)
            server.timeout = 1.0; server.auth_code = None; attempts = 0
            while not self._abort and attempts < 60 and server.auth_code is None:
                server.handle_request(); attempts += 1
            self.finished_signal.emit(server.auth_code if server.auth_code else "")
            server.server_close()
        except: self.finished_signal.emit("")
    def abort(self): self._abort = True

class LoginView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.settings = QSettings("MySaaS", "DesktopClient")
        self.is_dark_mode = self.settings.value("is_dark_mode", False, type=bool)
        self.current_lang = self.settings.value("language", "TR")
        
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        bg_path = os.path.join(base_dir, 'assets', 'background.png')
        self.bg_pixmap = QPixmap(bg_path)

        # CRASH FIX: Movie nesnesini burada bir kez oluştur
        gif_path = os.path.join(base_dir, 'assets', 'Loading_2.gif').replace('\\', '/')
        self.loading_movie = None
        if os.path.exists(gif_path):
            self.loading_movie = QMovie(gif_path)
            self.loading_movie.setScaledSize(QSize(64, 64))

        self.setup_ui()
        self.sync_settings() 
        self.load_saved_session()

    def reset_form(self):
        self.login_email.clear(); self.login_pw.clear()
        self.reg_name.clear(); self.reg_email.clear(); self.reg_pw.clear()
        self.remember_cb.setChecked(False)
        self.stacked_widget.setCurrentWidget(self.login_widget)

    def sync_settings(self):
        self.is_dark_mode = self.settings.value("is_dark_mode", False, type=bool)
        self.current_lang = self.settings.value("language", "TR")
        self.apply_theme(); self.update_texts()
        self.lang_cb.blockSignals(True)
        self.lang_cb.setCurrentText(self.current_lang)
        self.lang_cb.blockSignals(False)

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.bg_pixmap.isNull():
            painter.setRenderHint(QPainter.SmoothPixmapTransform)
            scaled = self.bg_pixmap.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = (self.width() - scaled.width()) // 2
            y = (self.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            painter.fillRect(self.rect(), Qt.black if self.is_dark_mode else Qt.lightGray)

    def setup_ui(self):
        self.main_layout = QVBoxLayout(self); self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.top_bar = QHBoxLayout(); self.top_bar.addStretch() 
        self.theme_btn = QPushButton(); self.theme_btn.setCursor(Qt.PointingHandCursor); self.theme_btn.clicked.connect(self.toggle_theme)
        self.lang_cb = QComboBox(); self.lang_cb.setCursor(Qt.PointingHandCursor)
        
        # Dil seçenekleri
        self.lang_cb.addItem("TR"); self.lang_cb.addItem("EN"); self.lang_cb.addItem("GER")
        self.lang_cb.currentTextChanged.connect(self.change_language)

        self.top_bar.addWidget(self.theme_btn); self.top_bar.addWidget(self.lang_cb)
        self.main_layout.addLayout(self.top_bar); self.main_layout.addStretch() 

        self.content_box = QFrame(); self.content_box.setObjectName("content_box")
        self.content_box.setFixedWidth(850); self.content_box.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        content_layout = QHBoxLayout(self.content_box); content_layout.setContentsMargins(35, 35, 35, 35); content_layout.setSpacing(30) 

        self.features_widget = self.create_features_ui()
        content_layout.addWidget(self.features_widget, 1) 

        self.divider = QFrame(); self.divider.setFrameShape(QFrame.VLine); self.divider.setObjectName("divider_line")
        content_layout.addWidget(self.divider)

        self.stacked_widget = QStackedWidget()
        self.login_widget = self.create_login_ui()
        self.register_widget = self.create_register_ui()
        self.loading_widget = self.create_loading_ui()

        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.register_widget)
        self.stacked_widget.addWidget(self.loading_widget)
        content_layout.addWidget(self.stacked_widget, 1) 
        
        box_layout = QHBoxLayout(); box_layout.addStretch(); box_layout.addWidget(self.content_box); box_layout.addStretch()
        self.main_layout.addLayout(box_layout); self.main_layout.addStretch() 

    def create_features_ui(self):
        widget = QWidget(); layout = QVBoxLayout(widget); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(15)
        self.lbl_feat_title = QLabel(); self.lbl_feat_title.setObjectName("feature_title")
        self.free_card = QFrame(); self.free_card.setObjectName("free_card"); f_l = QVBoxLayout(self.free_card)
        self.lbl_plan_free = QLabel(); self.lbl_plan_free.setObjectName("plan_title")
        self.lbl_price_free = QLabel(); self.lbl_price_free.setObjectName("plan_price") 
        self.lbl_f1 = QLabel(); self.lbl_f2 = QLabel(); self.lbl_f3 = QLabel(); self.lbl_f4 = QLabel()
        for l in [self.lbl_plan_free, self.lbl_price_free, self.lbl_f1, self.lbl_f2, self.lbl_f3, self.lbl_f4]: 
            l.setObjectName("plan_item"); f_l.addWidget(l)
        
        self.ent_card = QFrame(); self.ent_card.setObjectName("ent_card"); e_l = QVBoxLayout(self.ent_card)
        self.lbl_plan_ent = QLabel(); self.lbl_plan_ent.setObjectName("plan_title_ent")
        self.lbl_price_ent = QLabel(); self.lbl_price_ent.setObjectName("plan_price_ent") 
        self.lbl_e1 = QLabel(); self.lbl_e2 = QLabel(); self.lbl_e3 = QLabel(); self.lbl_e4 = QLabel()
        for l in [self.lbl_plan_ent, self.lbl_price_ent, self.lbl_e1, self.lbl_e2, self.lbl_e3, self.lbl_e4]:
            l.setObjectName("plan_item_ent"); e_l.addWidget(l)

        layout.addStretch(); layout.addWidget(self.lbl_feat_title); layout.addWidget(self.free_card); layout.addWidget(self.ent_card); layout.addStretch()
        return widget

    def create_login_ui(self):
        widget = QWidget(); layout = QVBoxLayout(widget); layout.setSpacing(12); layout.addStretch() 
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
        widget = QWidget(); layout = QVBoxLayout(widget); layout.setSpacing(12); layout.addStretch()
        self.lbl_reg_title = QLabel(); self.lbl_reg_title.setStyleSheet("font-size: 24px; font-weight: bold;"); self.lbl_reg_title.setAlignment(Qt.AlignCenter)
        self.reg_name = QLineEdit(); self.reg_email = QLineEdit(); self.reg_pw = QLineEdit(); self.reg_pw.setEchoMode(QLineEdit.Password)
        self.btn_reg = QPushButton(); self.btn_reg.setObjectName("success_btn"); self.btn_reg.clicked.connect(self.handle_register)
        self.btn_switch_log = QPushButton(); self.btn_switch_log.setObjectName("switch_btn"); self.btn_switch_log.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.login_widget))
        layout.addWidget(self.lbl_reg_title); layout.addWidget(self.reg_name); layout.addWidget(self.reg_email); layout.addWidget(self.reg_pw)
        layout.addWidget(self.btn_reg); layout.addWidget(self.btn_switch_log, alignment=Qt.AlignCenter); layout.addStretch()
        return widget

    def create_loading_ui(self):
        widget = QWidget(); layout = QVBoxLayout(widget); layout.setAlignment(Qt.AlignCenter); layout.addStretch()
        self.gif_label = QLabel(); self.gif_label.setAlignment(Qt.AlignCenter)
        if self.loading_movie: self.gif_label.setMovie(self.loading_movie)
        self.lbl_load_title = QLabel(); self.lbl_load_title.setStyleSheet("font-size: 20px; font-weight: 800;"); self.lbl_load_title.setAlignment(Qt.AlignCenter)
        self.lbl_load_sub = QLabel(); self.lbl_load_sub.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.gif_label); layout.addWidget(self.lbl_load_title); layout.addWidget(self.lbl_load_sub); layout.addStretch()
        return widget

    def handle_login(self):
        email = self.login_email.text().strip(); pw = self.login_pw.text().strip()
        if not email or not pw: return QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun.")
        
        t = LANGUAGES[self.current_lang]
        self.lbl_load_title.setText(t['load_log']); self.lbl_load_sub.setText(t['load_log_sub'])
        self.stacked_widget.setCurrentWidget(self.loading_widget)
        if self.loading_movie: self.loading_movie.start()

        self.auth_worker = AuthWorkerThread('login', email, pw)
        self.auth_worker.finished_signal.connect(self.on_login_finished)
        self.auth_worker.start()

    def on_login_finished(self, success, data):
        if self.loading_movie: self.loading_movie.stop()
        if success:
            token = data.get("token", "") if isinstance(data, dict) else str(data)
            self.settings.setValue("auth_token", token)
            self.settings.setValue("remember_me", self.remember_cb.isChecked())
            self.main_window.show_dashboard()
        else:
            self.stacked_widget.setCurrentWidget(self.login_widget)
            QMessageBox.critical(self, "Hata", str(data))

    def handle_register(self):
        name = self.reg_name.text().strip(); email = self.reg_email.text().strip(); pw = self.reg_pw.text().strip()
        if not name or not email or not pw: return QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun.")
        
        t = LANGUAGES[self.current_lang]
        self.lbl_load_title.setText(t['load_reg']); self.lbl_load_sub.setText(t['load_reg_sub'])
        self.stacked_widget.setCurrentWidget(self.loading_widget)
        if self.loading_movie: self.loading_movie.start()

        self.auth_worker = AuthWorkerThread('register', name, email, pw)
        self.auth_worker.finished_signal.connect(self.on_register_finished)
        self.auth_worker.start()

    def on_register_finished(self, success, msg):
        if self.loading_movie: self.loading_movie.stop()
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

    def load_saved_session(self):
        saved_token = self.settings.value("auth_token")
        if saved_token:
            from core import config
            config.CURRENT_TOKEN = saved_token
            self.main_window.show_dashboard()


    def toggle_theme(self): 
        self.is_dark_mode = not self.is_dark_mode
        self.settings.setValue("is_dark_mode", self.is_dark_mode)
        self.apply_theme(); self.update_texts()

    def change_language(self, code): 
        self.current_lang = code
        self.settings.setValue("language", code)
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