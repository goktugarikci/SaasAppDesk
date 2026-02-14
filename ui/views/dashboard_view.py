# ui/views/dashboard_view.py
import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QStackedWidget, QListWidget, QListWidgetItem, QComboBox)
from PySide6.QtCore import Qt, QSize, QSettings
from PySide6.QtGui import QIcon, QFont

# YENİ: Çevrimdışı (Offline) metinleri eklendi
DASHBOARD_LANGS = {
    'TR': {
        'logo': "☁️ MySaaS Workspace", 'menu_title': "SUNUCULARIM",
        'status_online': "🟢 Çevrimiçi", 'status_offline': "⚫ Çevrimdışı", 'logout_tip': "Çıkış Yap",
        'theme_dark': "🌙 Koyu Tema", 'theme_light': "☀️ Açık Tema",
        'welcome_title': "MySaaS'a Hoş Geldiniz!", 'welcome_sub': "Çalışmaya başlamak için aşağıdaki seçeneklerden birini seçin.",
        'card_create_title': "Sunucu Oluştur", 'card_create_desc': "Kendi topluluğunuzu veya özel çalışma alanınızı kurun.", 'card_create_btn': "Oluştur",
        'card_join_title': "Sunucuya Katıl", 'card_join_desc': "Elinizdeki davet bağlantısı ile mevcut bir sunucuya katılın.", 'card_join_btn': "Katıl",
        'card_friend_title': "Arkadaş Ekle", 'card_friend_desc': "Arkadaşlarınızı ekleyerek anında direkt mesajlaşmaya başlayın.", 'card_friend_btn': "Ekle"
    },
    'EN': {
        'logo': "☁️ MySaaS Workspace", 'menu_title': "MY SERVERS",
        'status_online': "🟢 Online", 'status_offline': "⚫ Offline", 'logout_tip': "Logout",
        'theme_dark': "🌙 Dark Mode", 'theme_light': "☀️ Light Mode",
        'welcome_title': "Welcome to MySaaS!", 'welcome_sub': "Choose one of the options below to get started.",
        'card_create_title': "Create Server", 'card_create_desc': "Set up your own community or private workspace.", 'card_create_btn': "Create",
        'card_join_title': "Join Server", 'card_join_desc': "Join an existing server using an invite link.", 'card_join_btn': "Join",
        'card_friend_title': "Add Friend", 'card_friend_desc': "Add your friends to start direct messaging instantly.", 'card_friend_btn': "Add Friend"
    },
    'GER': {
        'logo': "☁️ MySaaS Workspace", 'menu_title': "MEINE SERVER",
        'status_online': "🟢 Online", 'status_offline': "⚫ Offline", 'logout_tip': "Abmelden",
        'theme_dark': "🌙 Dunkel", 'theme_light': "☀️ Hell",
        'welcome_title': "Willkommen bei MySaaS!", 'welcome_sub': "Wählen Sie eine der untenstehenden Optionen, um zu beginnen.",
        'card_create_title': "Server erstellen", 'card_create_desc': "Richten Sie Ihre eigene Community oder Ihren Arbeitsbereich ein.", 'card_create_btn': "Erstellen",
        'card_join_title': "Server beitreten", 'card_join_desc': "Treten Sie einem Server mit einem Einladungslink bei.", 'card_join_btn': "Beitreten",
        'card_friend_title': "Freund hinzufügen", 'card_friend_desc': "Fügen Sie Freunde hinzu, um Direktnachrichten zu senden.", 'card_friend_btn': "Hinzufügen"
    }
}

class DashboardView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.settings = QSettings("MySaaS", "DesktopClient")
        
        self.is_dark_mode = self.settings.value("is_dark_mode", False, type=bool)
        self.current_lang = self.settings.value("language", "TR")
        
        # YENİ: Kullanıcının anlık durumu
        self.is_online = True 
        
        self.setup_ui()
        self.sync_settings()

    # YENİ: Dışarıdan tetiklenecek durum güncelleme fonksiyonu
    def set_status(self, online_state: bool):
        self.is_online = online_state
        self.update_texts() # Metni (Çevrimiçi/Çevrimdışı) güncelle
        self.apply_theme()  # Rengini (Yeşil/Gri) güncelle

    def sync_settings(self):
        self.is_dark_mode = self.settings.value("is_dark_mode", False, type=bool)
        self.current_lang = self.settings.value("language", "TR")
        self.apply_theme()
        self.update_texts()
        self.lang_cb.blockSignals(True)
        self.lang_cb.setCurrentText(self.current_lang)
        self.lang_cb.blockSignals(False)

    def setup_ui(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # SOL MENÜ
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 20, 15, 15)
        sidebar_layout.setSpacing(15)

        self.lbl_logo = QLabel()
        self.lbl_logo.setObjectName("logo_text")
        sidebar_layout.addWidget(self.lbl_logo)
        sidebar_layout.addSpacing(10)

        self.lbl_menu_title = QLabel()
        self.lbl_menu_title.setObjectName("menu_title")
        sidebar_layout.addWidget(self.lbl_menu_title)

        self.server_list = QListWidget()
        self.server_list.setObjectName("server_list")
        sidebar_layout.addWidget(self.server_list)

        self.profile_box = QFrame()
        self.profile_box.setObjectName("profile_box")
        profile_layout = QHBoxLayout(self.profile_box)
        profile_layout.setContentsMargins(10, 10, 10, 10)
        
        self.lbl_avatar = QLabel("👤")
        self.lbl_avatar.setStyleSheet("font-size: 24px;")
        
        user_info_layout = QVBoxLayout()
        self.lbl_username = QLabel("Kullanıcı Adı")
        self.lbl_username.setObjectName("username_lbl")
        self.lbl_status = QLabel()
        self.lbl_status.setObjectName("status_lbl")
        user_info_layout.addWidget(self.lbl_username)
        user_info_layout.addWidget(self.lbl_status)
        
        self.btn_logout = QPushButton("🚪")
        self.btn_logout.setObjectName("logout_btn")
        self.btn_logout.clicked.connect(self.main_window.show_login) 
        self.btn_logout.setFixedSize(30, 30)

        profile_layout.addWidget(self.lbl_avatar)
        profile_layout.addLayout(user_info_layout)
        profile_layout.addStretch()
        profile_layout.addWidget(self.btn_logout)

        sidebar_layout.addWidget(self.profile_box)

        # SAĞ İÇERİK ALANI
        self.content_area = QFrame()
        self.content_area.setObjectName("content_area")
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self.header = QFrame()
        self.header.setObjectName("header")
        self.header.setFixedHeight(65)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        self.lbl_channel_name = QLabel() 
        self.lbl_channel_name.setObjectName("channel_name")
        
        self.btn_theme = QPushButton()
        self.btn_theme.setObjectName("theme_btn")
        self.btn_theme.setCursor(Qt.PointingHandCursor)
        self.btn_theme.clicked.connect(self.toggle_theme)

        self.lang_cb = QComboBox()
        self.lang_cb.setObjectName("lang_cb")
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
        
        header_layout.addWidget(self.lbl_channel_name)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_theme)
        header_layout.addWidget(self.lang_cb)

        content_layout.addWidget(self.header)

        self.stacked_widget = QStackedWidget()
        self.welcome_page = QWidget()
        welcome_layout = QVBoxLayout(self.welcome_page)
        welcome_layout.setAlignment(Qt.AlignCenter)
        welcome_layout.setSpacing(40) 
        
        title_box = QWidget()
        title_layout = QVBoxLayout(title_box)
        title_layout.setAlignment(Qt.AlignCenter)
        
        self.lbl_welcome_title = QLabel()
        self.lbl_welcome_title.setObjectName("welcome_title")
        self.lbl_welcome_title.setAlignment(Qt.AlignCenter)
        
        self.lbl_welcome_sub = QLabel()
        self.lbl_welcome_sub.setObjectName("welcome_sub")
        self.lbl_welcome_sub.setAlignment(Qt.AlignCenter)
        
        title_layout.addWidget(self.lbl_welcome_title)
        title_layout.addWidget(self.lbl_welcome_sub)
        
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(25)
        cards_layout.setAlignment(Qt.AlignCenter)
        
        self.card_create, self.lbl_c_title, self.lbl_c_desc, self.btn_create = self.create_action_card("➕")
        self.card_join, self.lbl_j_title, self.lbl_j_desc, self.btn_join = self.create_action_card("🔗")
        self.card_friend, self.lbl_f_title, self.lbl_f_desc, self.btn_friend = self.create_action_card("👤")
        
        cards_layout.addWidget(self.card_create)
        cards_layout.addWidget(self.card_join)
        cards_layout.addWidget(self.card_friend)
        
        welcome_layout.addStretch()
        welcome_layout.addWidget(title_box)
        welcome_layout.addLayout(cards_layout)
        welcome_layout.addStretch()
        
        self.stacked_widget.addWidget(self.welcome_page)
        content_layout.addWidget(self.stacked_widget)

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area)

    def create_action_card(self, icon_emoji):
        card = QFrame()
        card.setObjectName("action_card")
        card.setFixedSize(260, 280) 
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(20, 30, 20, 20)
        
        lbl_icon = QLabel(icon_emoji)
        lbl_icon.setObjectName("card_icon")
        lbl_icon.setAlignment(Qt.AlignCenter)
        
        lbl_title = QLabel()
        lbl_title.setObjectName("card_title")
        lbl_title.setAlignment(Qt.AlignCenter)
        
        lbl_desc = QLabel()
        lbl_desc.setObjectName("card_desc")
        lbl_desc.setAlignment(Qt.AlignCenter)
        lbl_desc.setWordWrap(True) 
        
        btn = QPushButton()
        btn.setObjectName("action_btn")
        btn.setCursor(Qt.PointingHandCursor)
        
        layout.addWidget(lbl_icon)
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_desc)
        layout.addStretch()
        layout.addWidget(btn)
        
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
        
        self.lbl_logo.setText(t['logo'])
        self.lbl_menu_title.setText(t['menu_title'])
        
        # YENİ: Duruma göre metin ata
        self.lbl_status.setText(t['status_online'] if self.is_online else t['status_offline'])
        
        self.btn_logout.setToolTip(t['logout_tip'])
        self.btn_theme.setText(t['theme_light'] if self.is_dark_mode else t['theme_dark'])
        
        self.lbl_welcome_title.setText(t['welcome_title'])
        self.lbl_welcome_sub.setText(t['welcome_sub'])
        
        self.lbl_c_title.setText(t['card_create_title'])
        self.lbl_c_desc.setText(t['card_create_desc'])
        self.btn_create.setText(t['card_create_btn'])
        
        self.lbl_j_title.setText(t['card_join_title'])
        self.lbl_j_desc.setText(t['card_join_desc'])
        self.btn_join.setText(t['card_join_btn'])
        
        self.lbl_f_title.setText(t['card_friend_title'])
        self.lbl_f_desc.setText(t['card_friend_desc'])
        self.btn_friend.setText(t['card_friend_btn'])

    def apply_theme(self):
        # YENİ: Duruma göre renk (Yeşil = Online, Gri/Sönük = Offline)
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
                
                /* YENİ RENK DİNAMİĞİ EKLENDİ */
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
                QComboBox#lang_cb QAbstractItemView {{ background-color: #1e2328; color: #dcddde; border: 1px solid #444; border-radius: 6px; selection-background-color: transparent; outline: none; padding: 4px; }}
                QComboBox#lang_cb QAbstractItemView::item {{ padding: 8px 10px; border-radius: 4px; min-height: 25px; }}
                QComboBox#lang_cb QAbstractItemView::item:hover {{ background-color: #2a3038; color: #4da3ff; }}

                QLabel#welcome_title {{ color: #ffffff; font-size: 32px; font-weight: 900; }}
                QLabel#welcome_sub {{ color: #b5bac1; font-size: 16px; margin-bottom: 20px; }}
                
                QFrame#action_card {{ background-color: #2b2d31; border: 1px solid #1e1f22; border-radius: 12px; }}
                QFrame#action_card:hover {{ border: 1px solid #5865f2; background-color: #2e3035; }}
                QLabel#card_icon {{ font-size: 48px; margin-bottom: 10px; }}
                QLabel#card_title {{ color: #ffffff; font-size: 18px; font-weight: bold; margin-bottom: 5px; }}
                QLabel#card_desc {{ color: #949ba4; font-size: 13px; line-height: 1.4; }}
                
                QPushButton#action_btn {{ background-color: #5865f2; color: white; border-radius: 6px; padding: 12px; font-weight: bold; font-size: 14px; border: none; }}
                QPushButton#action_btn:hover {{ background-color: #4752c4; }}
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
                
                /* YENİ RENK DİNAMİĞİ EKLENDİ */
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
                QComboBox#lang_cb QAbstractItemView {{ background-color: #ffffff; color: #1c1e21; border: 1px solid #ccd0d5; border-radius: 6px; selection-background-color: transparent; outline: none; padding: 4px; }}
                QComboBox#lang_cb QAbstractItemView::item {{ padding: 8px 10px; border-radius: 4px; min-height: 25px; }}
                QComboBox#lang_cb QAbstractItemView::item:hover {{ background-color: #f0f2f5; color: #1877f2; }}

                QLabel#welcome_title {{ color: #060607; font-size: 32px; font-weight: 900; }}
                QLabel#welcome_sub {{ color: #4e5058; font-size: 16px; margin-bottom: 20px; }}
                
                QFrame#action_card {{ background-color: #ffffff; border: 1px solid #e3e5e8; border-radius: 12px; }}
                QFrame#action_card:hover {{ border: 1px solid #1877f2; background-color: #f8f9fa; }}
                QLabel#card_icon {{ font-size: 48px; margin-bottom: 10px; }}
                QLabel#card_title {{ color: #060607; font-size: 18px; font-weight: bold; margin-bottom: 5px; }}
                QLabel#card_desc {{ color: #5c5e66; font-size: 13px; line-height: 1.4; }}
                
                QPushButton#action_btn {{ background-color: #1877f2; color: white; border-radius: 6px; padding: 12px; font-weight: bold; font-size: 14px; border: none; }}
                QPushButton#action_btn:hover {{ background-color: #166fe5; }}
            """)