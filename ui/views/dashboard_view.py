import os
import webbrowser
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,  QDialog,
                               QPushButton, QFrame, QStackedWidget, QListWidget, 
                               QListWidgetItem, QComboBox, QLineEdit, QMessageBox,
                               QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize, QSettings, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QIcon, QFont, QColor

# YENİ MODÜLER YAPIDAN İÇERİ AKTARIMLAR
from ui.resources.languages import DASHBOARD_LANGS
from ui.styles.dashboard_theme import get_dashboard_stylesheet
from api.threads import (ApiFetchProfileThread, ApiCreateServerThread, 
                         ApiFetchMyServersThread, ApiJoinServerThread)
from ui.components.dialogs import CustomDialog, AddFriendDialog, SettingsDialog

class DashboardView(QWidget):
# 1. init kısmına aktif sunucu takibi için değişkenler ekleyin
    def __init__(self, main_window):
        super().__init__()
        self.setObjectName("dashboard_main") 
        self.main_window = main_window
        self.settings = QSettings("MySaaS", "DesktopClient")
        self.is_dark_mode = self.settings.value("is_dark_mode", False, type=bool)
        self.current_lang = self.settings.value("language", "TR")
        
        self.is_online = True 
        self.is_mic_on = True
        self.is_deafened = False
        
        # YENİ: Hangi sunucuda olduğumuzu tutan değişkenler
        self.active_server_id = None
        self.active_server_name = ""
        
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
        self.is_online = online_state; self.update_texts(); self.apply_theme()  

    def sync_settings(self):
        self.is_dark_mode = self.settings.value("is_dark_mode", False, type=bool)
        self.current_lang = self.settings.value("language", "TR")
        self.apply_theme()
        self.update_texts()
        self.lang_cb.blockSignals(True); self.lang_cb.setCurrentText(self.current_lang); self.lang_cb.blockSignals(False)

    def toggle_sidebar(self):
        self.sidebar_anim = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.sidebar_anim.setEasingCurve(QEasingCurve.InOutQuad); self.sidebar_anim.setDuration(250)
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
            self.lbl_username.setText(data.get("name", data.get("username", "Kullanıcı")))
            self.lbl_email.setText(data.get("email", "bilinmeyen@hesap.com"))

    def fetch_my_servers(self):
        self.server_list.clear()
        self.servers_thread = ApiFetchMyServersThread()
        self.servers_thread.finished_signal.connect(self.on_servers_fetched)
        self.servers_thread.start()

# 1. on_servers_fetched fonksiyonunu güncelleyin
    def on_servers_fetched(self, success, servers, error_type):
        self.server_list.clear()
        
        # YENİ: Sunucuları hafızaya al ki Ayarlara aktarabilelim
        self.my_servers = servers if success and isinstance(servers, list) else []
        
        t = DASHBOARD_LANGS[self.current_lang]
        
        home_item = QListWidgetItem(f"🏠 {t['home_btn']}")
        home_item.setFont(QFont("Segoe UI", 11, QFont.Bold))
        home_item.setData(Qt.UserRole, "HOME")
        self.server_list.addItem(home_item)
        
        spacer = QListWidgetItem()
        spacer.setFlags(Qt.NoItemFlags)   
        spacer.setSizeHint(QSize(0, 15))  
        self.server_list.addItem(spacer)
        
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
                
        elif error_type == "UNAUTHORIZED": QTimer.singleShot(100, self.handle_unauthorized)
        else:
            item = QListWidgetItem("Bağlantı Bekleniyor..."); item.setFont(QFont("Segoe UI", 10)); item.setFlags(Qt.NoItemFlags)
            self.server_list.addItem(item)


    def on_server_selected(self, item):
        server_id = item.data(Qt.UserRole)
        if not server_id: return
        t = DASHBOARD_LANGS[self.current_lang]
        
        if server_id == "HOME":
            self.active_server_id = None # Ana sayfadaysa sunucu seçili değil
            self.active_server_name = ""
            self.stacked_widget.setCurrentWidget(self.page_friends)
            self.lbl_channel_name.setText(t['friends_title'])
            return
            
        # Eğer bir sunucu seçildiyse hafızaya al
        self.active_server_id = server_id
        self.active_server_name = item.text().replace("🏢 ", "")
        
        self.lbl_srv_title.setText(self.active_server_name)
        self.lbl_channel_name.setText("# genel-sohbet")
        self.stacked_widget.setCurrentWidget(self.page_active_server)
        self.populate_mock_channels()

    def populate_mock_channels(self):
        self.channel_list.clear(); t = DASHBOARD_LANGS[self.current_lang]
        cat1 = QListWidgetItem(t['cat_text']); cat1.setFlags(Qt.NoItemFlags); cat1.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.channel_list.addItem(cat1); self.channel_list.addItem(QListWidgetItem("   # genel-sohbet"))
        cat2 = QListWidgetItem(t['cat_board']); cat2.setFlags(Qt.NoItemFlags); cat2.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.channel_list.addItem(cat2); self.channel_list.addItem(QListWidgetItem("   📋 Proje Panosu"))

# 2. show_settings_page fonksiyonunu güncelleyin
    def show_settings_page(self):
        t = DASHBOARD_LANGS[self.current_lang]
        # YENİ: self.my_servers listesi ayarlara iletiliyor
        dialog = SettingsDialog(self, self.is_dark_mode, t, 
                                self.lbl_username.text(), self.lbl_email.text(),
                                getattr(self, 'my_servers', []))
        result = dialog.exec()
        if result == 2: 
            self.settings.setValue("auth_token", "")
            self.settings.setValue("remember_me", False) 
            self.main_window.show_login()

    # 3. YENİ BİR FONKSİYON EKLEYİN (DashboardView sınıfının içine)
    def on_channels_updated(self):
        """Ayarlar panelinde bir kanal silinir veya eklenirse aktif paneli yeniler"""
        self.populate_mock_channels()

    def setup_ui(self):
        self.main_layout = QHBoxLayout(self); self.main_layout.setContentsMargins(0, 0, 0, 0); self.main_layout.setSpacing(0)
        self.sidebar = QFrame(); self.sidebar.setObjectName("sidebar"); self.sidebar.setMaximumWidth(260); self.sidebar.setMinimumWidth(260) 
        sidebar_layout = QVBoxLayout(self.sidebar); sidebar_layout.setContentsMargins(15, 20, 15, 15); sidebar_layout.setSpacing(15)
        self.lbl_logo = QLabel(); self.lbl_logo.setObjectName("logo_text")
        self.lbl_menu_title = QLabel(); self.lbl_menu_title.setObjectName("menu_title")
        self.server_list = QListWidget(); self.server_list.setObjectName("server_list"); self.server_list.itemClicked.connect(self.on_server_selected)
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

        self.stacked_widget = QStackedWidget(); self.stacked_widget.setObjectName("main_stack")
        self.page_selection = QFrame(); self.page_selection.setObjectName("page_bg")
        self.page_standard = QFrame(); self.page_standard.setObjectName("page_bg")
        self.page_enterprise = QFrame(); self.page_enterprise.setObjectName("page_bg")
        self.page_server_setup = QFrame(); self.page_server_setup.setObjectName("page_bg")
        self.page_active_server = QFrame(); self.page_active_server.setObjectName("page_bg")
        self.page_friends = QFrame(); self.page_friends.setObjectName("page_bg")

        self.create_selection_page(self.page_selection); self.create_standard_page(self.page_standard) 
        self.create_enterprise_page(self.page_enterprise); self.create_server_setup_page(self.page_server_setup) 
        self.create_active_server_page(self.page_active_server); self.create_friends_page(self.page_friends) 

        self.stacked_widget.addWidget(self.page_selection); self.stacked_widget.addWidget(self.page_standard)
        self.stacked_widget.addWidget(self.page_enterprise); self.stacked_widget.addWidget(self.page_server_setup) 
        self.stacked_widget.addWidget(self.page_active_server); self.stacked_widget.addWidget(self.page_friends)
        
        self.stacked_widget.setCurrentWidget(self.page_selection) 
        content_layout.addWidget(self.stacked_widget)
        self.main_layout.addWidget(self.sidebar); self.main_layout.addWidget(self.content_area)

        self.floating_profile_box = QFrame(self); self.floating_profile_box.setObjectName("floating_profile")
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
            btn.setFixedSize(30, 30); btn.setCursor(Qt.PointingHandCursor); btn_layout.addWidget(btn)

        self.btn_mic.clicked.connect(self.toggle_mic); self.btn_deafen.clicked.connect(self.toggle_deafen)
        self.btn_settings.clicked.connect(self.show_settings_page)

        pf_layout.addWidget(self.lbl_avatar); pf_layout.addWidget(info_widget); pf_layout.addStretch(); pf_layout.addLayout(btn_layout)


    def complete_onboarding(self):
        self.settings.setValue("has_completed_onboarding", True); self.stacked_widget.setCurrentWidget(self.page_standard)

    def create_friends_page(self, page):
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

    def create_active_server_page(self, page):
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

    def create_server_setup_page(self, page):
        layout = QVBoxLayout(page); layout.setAlignment(Qt.AlignCenter)
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

    def create_selection_page(self, page):
        layout = QVBoxLayout(page); layout.setAlignment(Qt.AlignCenter); layout.setSpacing(40)
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

    def create_standard_page(self, page):
        layout = QVBoxLayout(page); layout.setAlignment(Qt.AlignCenter); layout.setSpacing(20) 
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

    def create_enterprise_page(self, page):
        layout = QVBoxLayout(page); layout.setAlignment(Qt.AlignCenter)
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
        if success: QTimer.singleShot(100, lambda: self.show_message_safe("Başarılı", msg, True))
        else:
            if error_type == "LIMIT_EXCEEDED": QTimer.singleShot(100, lambda: self.show_message_safe("Limit Uyarısı", t['err_freemium_limit'], False))
            elif error_type == "UNAUTHORIZED": QTimer.singleShot(100, self.handle_unauthorized)
            else: QTimer.singleShot(100, lambda: self.show_message_safe("Hata", msg, False))

    def show_join_dialog(self):
        t = DASHBOARD_LANGS[self.current_lang]
        dialog = CustomDialog(self, self.is_dark_mode, t['dlg_join_title'], t['dlg_join_sub'], t['dlg_join_ph'], t['card_join_btn'], t['dlg_btn_cancel'])
        if dialog.exec() == QDialog.Accepted:
            invite_code = dialog.get_input_text()
            if invite_code:
                self.join_thread = ApiJoinServerThread(invite_code)
                self.join_thread.finished_signal.connect(self.on_join_finished)
                self.join_thread.start()
            else: QMessageBox.warning(self, "Uyarı", "Lütfen bir davet kodu girin.")

    def show_message_safe_join(self, title, msg, is_success):
        if is_success: QMessageBox.information(self, title, msg); self.fetch_my_servers()
        else: QMessageBox.warning(self, title, msg)

    def on_join_finished(self, success, msg, error_type):
        t = DASHBOARD_LANGS[self.current_lang]
        if success: QTimer.singleShot(100, lambda: self.show_message_safe_join("Başarılı", msg, True))
        else: 
            if error_type == "UNAUTHORIZED": QTimer.singleShot(100, self.handle_unauthorized)
            else: QTimer.singleShot(100, lambda: self.show_message_safe_join("Hata", t['err_invalid_invite'], False))

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
        
# Harici CSS Fonksiyonundan temayı al ve uygula (Boolean değerler gönderiliyor)
        from ui.styles.dashboard_theme import get_dashboard_stylesheet
        self.setStyleSheet(get_dashboard_stylesheet(self.is_dark_mode, self.is_mic_on, self.is_deafened))