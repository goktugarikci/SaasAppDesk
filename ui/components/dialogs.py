# ui/components/dialogs.py
import webbrowser
from PySide6.QtWidgets import (QDialog, QFrame, QVBoxLayout, QHBoxLayout, 
                               QLabel, QLineEdit, QPushButton, QListWidget, 
                               QListWidgetItem, QWidget, QStackedWidget, 
                               QScrollArea, QMessageBox, QComboBox, QGraphicsDropShadowEffect)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QColor, QFont

# API Threadleri
from api.threads import (ApiSearchUsersThread, ApiAddFriendThread, 
                         ApiFetchChannelsThread, ApiCreateChannelThread, 
                         ApiUpdateChannelThread, ApiDeleteChannelThread)

# Tema Dosyası
from ui.styles.dashboard_theme import get_dialog_stylesheet, get_settings_stylesheet

# ==========================================
# 1. BASİT INPUT DIALOG (SUNUCU KATILMA VB.)
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

        layout = QVBoxLayout(self.bg_frame)
        layout.setContentsMargins(35, 30, 35, 30)
        layout.setSpacing(15)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("dialog_title")
        lbl_title.setAlignment(Qt.AlignCenter)

        lbl_sub = QLabel(sub_text)
        lbl_sub.setObjectName("dialog_sub")
        lbl_sub.setAlignment(Qt.AlignCenter)
        lbl_sub.setWordWrap(True)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText(ph_text)
        self.input_field.setMinimumHeight(45) 
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        btn_layout.addStretch() 

        btn_cancel = QPushButton(btn_cancel_text)
        btn_cancel.setObjectName("dialog_btn_cancel")
        btn_cancel.setFixedSize(100, 42)
        btn_cancel.clicked.connect(self.reject) 

        btn_ok = QPushButton(btn_ok_text)
        btn_ok.setObjectName("dialog_btn_ok")
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

        self.bg_frame.setStyleSheet(get_dialog_stylesheet(is_dark_mode))

    def get_input_text(self):
        return self.input_field.text().strip()


# ==========================================
# 2. ARKADAŞ EKLEME DIALOG
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

    def setup_ui(self):
        self.bg_frame = QFrame(self)
        self.bg_frame.setGeometry(0, 0, 500, 500)
        self.bg_frame.setObjectName("dialog_bg")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25); shadow.setXOffset(0); shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 180 if self.is_dark_mode else 80))
        self.bg_frame.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.bg_frame)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        lbl_title = QLabel(self.lang['search_title'])
        lbl_title.setObjectName("dialog_title")
        lbl_title.setAlignment(Qt.AlignCenter)

        lbl_sub = QLabel(self.lang['search_sub'])
        lbl_sub.setObjectName("dialog_sub")
        lbl_sub.setAlignment(Qt.AlignCenter)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.lang['search_ph'])
        self.search_input.setMinimumHeight(45)
        self.search_input.textChanged.connect(self.on_text_changed)

        self.result_list = QListWidget()
        self.result_list.setObjectName("result_list")
        self.result_list.setSelectionMode(QListWidget.NoSelection) 
        
        btn_close = QPushButton(self.lang['search_btn_close'])
        btn_close.setObjectName("dialog_btn_cancel")
        btn_close.setFixedSize(120, 40)
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.reject) 

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_sub)
        layout.addSpacing(10)
        layout.addWidget(self.search_input)
        layout.addWidget(self.result_list)
        layout.addWidget(btn_close, alignment=Qt.AlignCenter)
        
        self.bg_frame.setStyleSheet(get_dialog_stylesheet(self.is_dark_mode))

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
        
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(10, 5, 10, 5)

        lbl_avatar = QLabel("👤")
        lbl_avatar.setStyleSheet("font-size: 24px;")

        info_layout = QVBoxLayout()
        lbl_name = QLabel(user.get('username', 'Bilinmeyen Kullanıcı'))
        lbl_name.setStyleSheet("font-weight: bold; font-size: 14px;")
        
        lbl_email = QLabel(user.get('email', ''))
        lbl_email.setObjectName("row_email") 
        
        info_layout.addWidget(lbl_name)
        info_layout.addWidget(lbl_email)
        info_layout.setAlignment(Qt.AlignVCenter)

        btn_add = QPushButton(self.lang['search_btn_add'])
        btn_add.setObjectName("dialog_btn_ok") 
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setFixedSize(80, 35)
        btn_add.clicked.connect(lambda _, u=user: self.send_friend_request(u))

        row_layout.addWidget(lbl_avatar)
        row_layout.addLayout(info_layout)
        row_layout.addStretch()
        row_layout.addWidget(btn_add)
        
        self.result_list.setItemWidget(item, row_widget)

    def send_friend_request(self, user):
        self.add_req_thread = ApiAddFriendThread(str(user.get('id', '')))
        self.add_req_thread.finished_signal.connect(lambda s, m: self.on_request_finished(s, m, user))
        self.add_req_thread.start()
        
    def on_request_finished(self, success, msg, user):
        if success:
            QMessageBox.information(self, "Başarılı", f"@{user.get('username', '')} kullanıcısına istek gönderildi!")
            self.accept()
        else:
            QMessageBox.warning(self, "Hata", msg)


# ==========================================
# 3. KANAL OLUŞTURMA DIALOG (REKLAM & KISITLAMA İLE)
# ==========================================
class ChannelDialog(QDialog):
    def __init__(self, parent, is_dark_mode, lang_dict, mode="add", channel_name="", channel_type=0, user_plan="standard"):
        super().__init__(parent)
        self.lang = lang_dict
        self.is_dark_mode = is_dark_mode
        self.mode = mode
        self.user_plan = user_plan  # Kullanıcı planı ('standard' veya 'enterprise')
        
        title = self.lang['ch_dlg_title_add'] if mode == "add" else self.lang['ch_dlg_title_edit']
        self.setWindowTitle(title)
        self.setFixedSize(450, 420) # Reklam için yükseklik artırıldı
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setup_ui(channel_name, channel_type)

    def setup_ui(self, channel_name, channel_type):
        self.bg_frame = QFrame(self)
        self.bg_frame.setGeometry(0, 0, 450, 420)
        self.bg_frame.setObjectName("dialog_bg")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25); shadow.setXOffset(0); shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 180 if self.is_dark_mode else 80))
        self.bg_frame.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self.bg_frame)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        lbl_title = QLabel(self.windowTitle())
        lbl_title.setObjectName("dialog_title")
        lbl_title.setAlignment(Qt.AlignCenter)
        
        self.inp_name = QLineEdit()
        self.inp_name.setPlaceholderText(self.lang['ch_dlg_name'])
        self.inp_name.setMinimumHeight(45)
        self.inp_name.setText(channel_name)

        self.cb_type = QComboBox()
        self.cb_type.setMinimumHeight(45)
        self.cb_type.addItem(self.lang['type_text'], 0)  
        self.cb_type.addItem(self.lang['type_board'], 3) # Kanban
        self.cb_type.addItem(self.lang['type_voice'], 2) 
        
        index = self.cb_type.findData(channel_type)
        if index >= 0: self.cb_type.setCurrentIndex(index)

        self.cb_type.currentIndexChanged.connect(self.check_plan_restrictions)

        # --- REKLAM / UPSELL ALANI ---
        self.upsell_frame = QFrame()
        self.upsell_frame.setObjectName("upsell_frame") 
        if self.is_dark_mode:
            self.upsell_frame.setStyleSheet("background-color: #2a200d; border: 1px solid #b7791f; border-radius: 8px;")
        
        upsell_layout = QVBoxLayout(self.upsell_frame)
        
        self.lbl_lock_title = QLabel(self.lang.get('srv_kanban_restricted', 'Kilitli Özellik'))
        self.lbl_lock_title.setObjectName("upsell_text")
        self.lbl_lock_title.setAlignment(Qt.AlignCenter)
        
        self.lbl_ad_desc = QLabel(self.lang.get('srv_kanban_ad', 'Enterprise ile sınırsız özellikler.'))
        self.lbl_ad_desc.setObjectName("upsell_desc")
        self.lbl_ad_desc.setWordWrap(True)
        self.lbl_ad_desc.setAlignment(Qt.AlignCenter)
        
        btn_layout_ad = QHBoxLayout()
        self.btn_upgrade = QPushButton(self.lang.get('btn_upgrade_now', 'Yükselt'))
        self.btn_upgrade.setStyleSheet("background-color: #f1c40f; color: black; font-weight: bold; border-radius: 4px; padding: 6px;")
        self.btn_upgrade.setCursor(Qt.PointingHandCursor)
        self.btn_upgrade.clicked.connect(lambda: webbrowser.open("https://sizin-odeme-linkiniz.com"))
        
        self.btn_toggle_ad = QPushButton(self.lang.get('btn_ad_close', 'Reklamı Kapat'))
        self.btn_toggle_ad.setObjectName("secondary_btn")
        self.btn_toggle_ad.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_ad.clicked.connect(self.toggle_ad_visibility)
        
        btn_layout_ad.addWidget(self.btn_upgrade)
        btn_layout_ad.addWidget(self.btn_toggle_ad)
        
        upsell_layout.addWidget(self.lbl_lock_title)
        upsell_layout.addWidget(self.lbl_ad_desc)
        upsell_layout.addLayout(btn_layout_ad)
        # -----------------------------

        btn_layout = QHBoxLayout()
        btn_cancel = QPushButton("İptal")
        btn_cancel.setObjectName("dialog_btn_cancel")
        btn_cancel.setFixedSize(100, 42)
        btn_cancel.clicked.connect(self.reject)

        self.btn_ok = QPushButton("Kaydet")
        self.btn_ok.setObjectName("dialog_btn_ok")
        self.btn_ok.setFixedSize(120, 42)
        self.btn_ok.clicked.connect(self.accept)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancel)
        btn_layout.addWidget(self.btn_ok)

        layout.addWidget(lbl_title)
        layout.addWidget(self.inp_name)
        layout.addWidget(self.cb_type)
        layout.addWidget(self.upsell_frame)
        layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.bg_frame.setStyleSheet(get_dialog_stylesheet(self.is_dark_mode))
        
        self.check_plan_restrictions()

    def check_plan_restrictions(self):
        selected_type = self.cb_type.currentData()
        # Eğer "Kanban (3)" seçiliyse ve kullanıcı "standard" ise kısıtla
        if selected_type == 3 and self.user_plan == "standard":
            self.upsell_frame.show()
            self.btn_ok.setEnabled(False) 
            self.btn_ok.setStyleSheet("background-color: #555; color: #888;")
        else:
            self.upsell_frame.hide()
            self.btn_ok.setEnabled(True)
            self.btn_ok.setObjectName("dialog_btn_ok")
            self.btn_ok.setStyleSheet("") 

    def toggle_ad_visibility(self):
        if self.lbl_ad_desc.isVisible():
            self.lbl_ad_desc.hide()
            self.btn_upgrade.hide()
            self.btn_toggle_ad.setText(self.lang.get('btn_ad_show', 'Reklam'))
        else:
            self.lbl_ad_desc.show()
            self.btn_upgrade.show()
            self.btn_toggle_ad.setText(self.lang.get('btn_ad_close', 'Kapat'))

    def get_data(self):
        return self.inp_name.text().strip(), self.cb_type.currentData()


# ==========================================
# 4. SUNUCU AYARLARI & KANAL YÖNETİMİ (SettingsDialog)
# ==========================================
class SettingsDialog(QDialog):
    def __init__(self, parent, is_dark_mode, lang_dict, current_name, current_email, servers_list):
        super().__init__(parent)
        self.parent_dashboard = parent 
        self.lang = lang_dict
        self.is_dark_mode = is_dark_mode
        self.current_name = current_name
        self.current_email = current_email
        self.servers_list = servers_list 
        self.active_server_id = None
        
        self.setWindowTitle(self.lang['set_pers_title'])
        self.setFixedSize(850, 650) 
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setup_ui()

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
        
        # --- KİŞİSEL AYARLAR ---
        self.page_personal = QFrame(); self.page_personal.setObjectName("settings_page_frame")
        p_layout = QVBoxLayout(self.page_personal); p_layout.setAlignment(Qt.AlignTop); p_layout.setSpacing(20)
        lbl_p_title = QLabel(self.lang['set_pers_title']); lbl_p_title.setObjectName("settings_title"); p_layout.addWidget(lbl_p_title)
        
        avatar_layout = QHBoxLayout(); self.set_avatar = QLabel("👤"); self.set_avatar.setObjectName("big_avatar"); self.set_avatar.setFixedSize(80, 80); self.set_avatar.setAlignment(Qt.AlignCenter)
        btn_upload_avatar = QPushButton(self.lang['set_avatar_btn']); btn_upload_avatar.setObjectName("secondary_btn"); btn_upload_avatar.setFixedSize(150, 40); btn_upload_avatar.setCursor(Qt.PointingHandCursor)
        btn_upload_avatar.clicked.connect(lambda: QMessageBox.information(self, "Bilgi", "Fotoğraf yükleme yakında eklenecektir."))
        avatar_layout.addWidget(self.set_avatar); avatar_layout.addSpacing(15); avatar_layout.addWidget(btn_upload_avatar); avatar_layout.addStretch()
        p_layout.addLayout(avatar_layout)

        lbl_name_hint = QLabel(self.lang['set_pers_name']); lbl_name_hint.setObjectName("bold_label")
        self.inp_name = QLineEdit(); self.inp_name.setMinimumHeight(45); self.inp_name.setText(self.current_name); self.inp_name.setReadOnly(True) 
        lbl_email_hint = QLabel(self.lang['set_pers_email']); lbl_email_hint.setObjectName("bold_label")
        self.inp_email = QLineEdit(); self.inp_email.setMinimumHeight(45); self.inp_email.setText(self.current_email); self.inp_email.setReadOnly(True) 
        p_layout.addWidget(lbl_name_hint); p_layout.addWidget(self.inp_name); p_layout.addWidget(lbl_email_hint); p_layout.addWidget(self.inp_email)

        self.acc_box = QFrame(); self.acc_box.setObjectName("account_box"); acc_box_layout = QVBoxLayout(self.acc_box)
        lbl_acc_box_title = QLabel(self.lang['set_acc_title']); lbl_acc_box_title.setObjectName("bold_label")
        lbl_acc_type = QLabel(self.lang['set_acc_type']); lbl_acc_type.setObjectName("normal_label")
        lbl_acc_limit = QLabel(self.lang['set_acc_limit']); lbl_acc_limit.setObjectName("normal_label")
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
        btn_save_p.clicked.connect(lambda: QMessageBox.information(self, "Bilgi", "Şifre güncellendi!"))
        p_layout.addSpacing(20); p_layout.addWidget(btn_save_p)
        self.scroll_area.setWidget(self.page_personal)

        # --- SUNUCU AYARLARI ---
        self.page_server = QFrame(); self.page_server.setObjectName("settings_page_frame")
        s_layout = QVBoxLayout(self.page_server); s_layout.setAlignment(Qt.AlignTop); s_layout.setSpacing(15)
        
        lbl_s_title = QLabel(self.lang['set_srv_title']); lbl_s_title.setObjectName("settings_title"); s_layout.addWidget(lbl_s_title)
        lbl_select = QLabel(self.lang['srv_select']); lbl_select.setObjectName("bold_label"); s_layout.addWidget(lbl_select)
        
        self.cb_managed_servers = QComboBox(); self.cb_managed_servers.setMinimumHeight(40); self.cb_managed_servers.setCursor(Qt.PointingHandCursor)
        self.managed_servers = []
        for s in self.servers_list: self.managed_servers.append(s)
            
        if not self.managed_servers:
            self.cb_managed_servers.addItem(self.lang['srv_no_admin'])
            self.cb_managed_servers.setEnabled(False)
        else:
            for s in self.managed_servers: self.cb_managed_servers.addItem(f"🏢 {s.get('name', 'Sunucu')}", s.get('id'))
                
        self.cb_managed_servers.currentIndexChanged.connect(self.on_managed_server_changed)
        s_layout.addWidget(self.cb_managed_servers)
        
        lbl_channels = QLabel(self.lang['srv_set_channels']); lbl_channels.setObjectName("bold_label"); s_layout.addWidget(lbl_channels)
        self.settings_channel_list = QListWidget(); self.settings_channel_list.setObjectName("channel_settings_list"); s_layout.addWidget(self.settings_channel_list)
        
        btn_crud_layout = QHBoxLayout()
        self.btn_add_ch = QPushButton(self.lang['btn_add_ch']); self.btn_add_ch.setObjectName("success_btn"); self.btn_add_ch.setCursor(Qt.PointingHandCursor)
        self.btn_edit_ch = QPushButton(self.lang['btn_edit_ch']); self.btn_edit_ch.setObjectName("primary_btn"); self.btn_edit_ch.setCursor(Qt.PointingHandCursor)
        self.btn_del_ch = QPushButton(self.lang['btn_del_ch']); self.btn_del_ch.setStyleSheet("background-color: #ed4245; color: white; border-radius: 6px; padding: 10px; font-weight: bold;")
        self.btn_del_ch.setCursor(Qt.PointingHandCursor)
        
        btn_crud_layout.addWidget(self.btn_add_ch); btn_crud_layout.addWidget(self.btn_edit_ch); btn_crud_layout.addWidget(self.btn_del_ch)
        s_layout.addLayout(btn_crud_layout)

        self.btn_add_ch.clicked.connect(self.on_add_channel_clicked)
        self.btn_edit_ch.clicked.connect(self.on_edit_channel_clicked)
        self.btn_del_ch.clicked.connect(self.on_delete_channel_clicked)

        self.stacked.addWidget(self.scroll_area); self.stacked.addWidget(self.page_server)
        content_layout.addLayout(top_bar); content_layout.addWidget(self.stacked)
        main_layout.addWidget(self.sidebar); main_layout.addWidget(self.content_area)
        self.bg_frame.setStyleSheet(get_settings_stylesheet(self.is_dark_mode))
        self.menu_list.setCurrentRow(0)

        if self.managed_servers: self.on_managed_server_changed(0)

    def on_managed_server_changed(self, index):
        if index >= 0 and self.managed_servers:
            self.active_server_id = self.cb_managed_servers.itemData(index)
            self.fetch_channels()

    def fetch_channels(self):
        if not self.active_server_id: return
        self.settings_channel_list.clear()
        self.fetch_ch_thread = ApiFetchChannelsThread(self.active_server_id)
        self.fetch_ch_thread.finished_signal.connect(self.on_channels_fetched)
        self.fetch_ch_thread.start()

    def on_channels_fetched(self, success, channels):
        self.settings_channel_list.clear()
        if success and channels:
            for ch in channels:
                ch_type = ch.get("type", 0)
                icon = "💬" if ch_type == 0 else "🔊" if ch_type == 2 else "📋"
                item = QListWidgetItem(f"{icon} {ch.get('name')}")
                item.setFont(QFont("Segoe UI", 11))
                item.setData(Qt.UserRole, ch.get("id")); item.setData(Qt.UserRole + 1, ch_type)
                self.settings_channel_list.addItem(item)
        else:
            item = QListWidgetItem("Kanal bulunamadı."); item.setFlags(Qt.NoItemFlags)
            self.settings_channel_list.addItem(item)

    def on_add_channel_clicked(self):
        # Kullanıcı planını Dashboard'dan al
        user_plan = getattr(self.parent_dashboard, 'user_plan', 'standard')
        dialog = ChannelDialog(self, self.is_dark_mode, self.lang, mode="add", user_plan=user_plan)
        if dialog.exec() == QDialog.Accepted:
            name, ch_type = dialog.get_data()
            if not name: return QMessageBox.warning(self, "Uyarı", "Kanal adı boş olamaz!")
            self.create_ch_thread = ApiCreateChannelThread(self.active_server_id, name, ch_type)
            self.create_ch_thread.finished_signal.connect(self.on_crud_finished)
            self.create_ch_thread.start()

    def on_edit_channel_clicked(self):
        selected = self.settings_channel_list.currentItem()
        if not selected or selected.flags() == Qt.NoItemFlags: return QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek için bir kanal seçin.")
        ch_id = selected.data(Qt.UserRole); ch_type = selected.data(Qt.UserRole + 1); ch_name = selected.text().split(" ", 1)[1]
        
        user_plan = getattr(self.parent_dashboard, 'user_plan', 'standard')
        dialog = ChannelDialog(self, self.is_dark_mode, self.lang, mode="edit", channel_name=ch_name, channel_type=ch_type, user_plan=user_plan)
        if dialog.exec() == QDialog.Accepted:
            new_name, new_type = dialog.get_data()
            if not new_name: return QMessageBox.warning(self, "Uyarı", "Kanal adı boş olamaz!")
            self.upd_ch_thread = ApiUpdateChannelThread(ch_id, new_name, new_type)
            self.upd_ch_thread.finished_signal.connect(self.on_crud_finished)
            self.upd_ch_thread.start()

    def on_delete_channel_clicked(self):
        selected = self.settings_channel_list.currentItem()
        if not selected or selected.flags() == Qt.NoItemFlags: return QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir kanal seçin.")
        reply = QMessageBox.question(self, "Onay", f"'{selected.text()}' kanalını silmek istediğinize emin misiniz?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            ch_id = selected.data(Qt.UserRole)
            self.del_ch_thread = ApiDeleteChannelThread(ch_id)
            self.del_ch_thread.finished_signal.connect(self.on_crud_finished)
            self.del_ch_thread.start()

    def on_crud_finished(self, success, msg):
        if success:
            self.fetch_channels()
            self.parent_dashboard.on_channels_updated()
        else: QMessageBox.warning(self, "Hata", msg)

    def on_menu_changed(self, row):
        if row == 0: self.stacked.setCurrentIndex(0)
        elif row == 1: self.stacked.setCurrentIndex(1)
        elif row == 2: self.done(2)