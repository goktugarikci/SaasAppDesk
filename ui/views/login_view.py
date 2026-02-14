# ui/views/login_view.py
import webbrowser
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QMessageBox, QCheckBox, QStackedWidget, QInputDialog, QFrame, QHBoxLayout)
from PySide6.QtCore import Qt, QSettings
from api.auth_api import login, register, get_google_auth_url, verify_google_code

class LoginView(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.settings = QSettings("MySaaS", "DesktopClient")
        
        # QWidget'ın arka plan rengini alabilmesi için bu ayar şarttır
        self.setAttribute(Qt.WA_StyledBackground, True)
        
        self.setup_ui()
        self.load_saved_session()

    def setup_ui(self):
        # Dış Arka Plan (Gözü yormayan çok açık, yumuşak bir gri)
        self.setStyleSheet("LoginView { background-color: #f0f2f5; }")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setAlignment(Qt.AlignCenter) # Kutuyu tam ortaya hizala

        # İçerik Kutusu (Beyaz Kart Görünümü)
        self.content_box = QFrame()
        self.content_box.setObjectName("content_box")
        self.content_box.setFixedWidth(420) # Kutunun genişliğini sabitledik, orantısız uzamayacak
        
        # Tüm iç elemanların ve kartın genel tasarımı
        self.content_box.setStyleSheet("""
            QFrame#content_box {
                background-color: #ffffff;
                border-radius: 12px;
                border: 1px solid #e1e4e8; /* Çok hafif, zarif bir kenarlık */
            }
            QLabel {
                color: #1c1e21; /* Tam siyah olmayan, yumuşak koyu gri metin */
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit {
                background-color: #f5f6f7;
                border: 1px solid #ccd0d5;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                color: #1c1e21;
            }
            QLineEdit:focus {
                border: 1px solid #1877f2; /* Tıklanınca modern mavi çerçeve */
                background-color: #ffffff;
            }
            QCheckBox {
                color: #606770;
                font-size: 13px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid #ccd0d5;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #1877f2;
                border: 1px solid #1877f2;
            }
            QPushButton#primary_btn {
                background-color: #1877f2;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-size: 15px;
                font-weight: bold;
                border: none;
            }
            QPushButton#primary_btn:hover { background-color: #166fe5; }
            
            QPushButton#success_btn {
                background-color: #42b72a; /* Yeşil kayıt ol butonu */
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-size: 15px;
                font-weight: bold;
                border: none;
            }
            QPushButton#success_btn:hover { background-color: #36a420; }

            QPushButton#google_btn {
                background-color: #df4b37;
                color: white;
                border-radius: 6px;
                padding: 12px;
                font-size: 15px;
                font-weight: bold;
                border: none;
            }
            QPushButton#google_btn:hover { background-color: #c94331; }

            QPushButton#switch_btn {
                color: #1877f2;
                background: transparent;
                border: none;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton#switch_btn:hover { text-decoration: underline; }
        """)

        # İçerik Kutusunun Layout'u
        content_layout = QVBoxLayout(self.content_box)
        content_layout.setContentsMargins(40, 40, 40, 40) # Kartın içindeki boşluklar
        content_layout.setSpacing(20)

        # Sayfa geçişleri için StackedWidget
        self.stacked_widget = QStackedWidget()
        self.login_widget = self.create_login_ui()
        self.register_widget = self.create_register_ui()
        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.register_widget)

        content_layout.addWidget(self.stacked_widget)
        self.main_layout.addWidget(self.content_box)

    def create_login_ui(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        title = QLabel("MySaaS'a Giriş Yap")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 5px;")
        title.setAlignment(Qt.AlignCenter)

        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("E-posta adresi")

        self.login_pw = QLineEdit()
        self.login_pw.setPlaceholderText("Şifre")
        self.login_pw.setEchoMode(QLineEdit.Password)

        self.remember_cb = QCheckBox("Oturumu açık tut")

        login_btn = QPushButton("Giriş Yap")
        login_btn.setObjectName("primary_btn")
        login_btn.clicked.connect(self.handle_login)

        # Araya çizgi veya "veya" yazısı eklemek için
        or_label = QLabel("────────  veya  ────────")
        or_label.setStyleSheet("color: #bcc0c4; font-size: 12px;")
        or_label.setAlignment(Qt.AlignCenter)

        google_btn = QPushButton("G   Google ile Devam Et")
        google_btn.setObjectName("google_btn")
        google_btn.clicked.connect(self.handle_google_login)

        switch_to_reg_btn = QPushButton("Hesabın yok mu? Yeni hesap oluştur")
        switch_to_reg_btn.setObjectName("switch_btn")
        switch_to_reg_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.register_widget))

        layout.addWidget(title)
        layout.addWidget(self.login_email)
        layout.addWidget(self.login_pw)
        layout.addWidget(self.remember_cb)
        layout.addSpacing(5)
        layout.addWidget(login_btn)
        layout.addWidget(or_label)
        layout.addWidget(google_btn)
        layout.addSpacing(10)
        layout.addWidget(switch_to_reg_btn, alignment=Qt.AlignCenter)
        return widget

    def create_register_ui(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        title = QLabel("Yeni Hesap Oluştur")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 5px;")
        title.setAlignment(Qt.AlignCenter)

        self.reg_name = QLineEdit()
        self.reg_name.setPlaceholderText("Ad Soyad")

        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("E-posta adresi")

        self.reg_pw = QLineEdit()
        self.reg_pw.setPlaceholderText("Yeni Şifre")
        self.reg_pw.setEchoMode(QLineEdit.Password)

        reg_btn = QPushButton("Kayıt Ol")
        reg_btn.setObjectName("success_btn")
        reg_btn.clicked.connect(self.handle_register)

        switch_to_log_btn = QPushButton("Zaten hesabın var mı? Giriş yap")
        switch_to_log_btn.setObjectName("switch_btn")
        switch_to_log_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.login_widget))

        layout.addWidget(title)
        layout.addWidget(self.reg_name)
        layout.addWidget(self.reg_email)
        layout.addWidget(self.reg_pw)
        layout.addSpacing(5)
        layout.addWidget(reg_btn)
        layout.addSpacing(10)
        layout.addWidget(switch_to_log_btn, alignment=Qt.AlignCenter)
        return widget

    # --- İŞLEM FONKSİYONLARI ---

    def handle_login(self):
        email = self.login_email.text().strip()
        pw = self.login_pw.text().strip()
        if not email or not pw: return QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun.")

        success, data = login(email, pw)
        if success:
            if self.remember_cb.isChecked():
                self.settings.setValue("auth_token", data.get("token"))
            else:
                self.settings.remove("auth_token")
                
            QMessageBox.information(self, "Başarılı", "Sisteme başarıyla giriş yapıldı!")
            # self.main_window.show_dashboard() # İleride aktif edeceğiz
        else:
            QMessageBox.critical(self, "Hata", data)

    def handle_register(self):
        name = self.reg_name.text().strip()
        email = self.reg_email.text().strip()
        pw = self.reg_pw.text().strip()
        if not name or not email or not pw: return QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurun.")

        success, msg = register(name, email, pw)
        if success:
            QMessageBox.information(self, "Başarılı", msg)
            self.stacked_widget.setCurrentWidget(self.login_widget)
        else:
            QMessageBox.critical(self, "Hata", msg)

    def handle_google_login(self):
        url = get_google_auth_url()
        if url:
            webbrowser.open(url)
            code, ok = QInputDialog.getText(self, "Google Doğrulama", 
                                            "Tarayıcıda açılan ekranda giriş yaptıktan sonra\nURL'de dönen 'code=' değerini buraya yapıştırın:")
            if ok and code:
                success, data = verify_google_code(code)
                if success:
                    self.settings.setValue("auth_token", data.get("token"))
                    QMessageBox.information(self, "Başarılı", "Google ile giriş yapıldı!")
                    # self.main_window.show_dashboard()
                else:
                    QMessageBox.critical(self, "Hata", data)
        else:
            QMessageBox.critical(self, "Hata", "Google sunucularına bağlanılamadı.")

    def load_saved_session(self):
        saved_token = self.settings.value("auth_token")
        if saved_token:
            from core import config
            config.CURRENT_TOKEN = saved_token
            # Normalde sunucudan token doğrulaması yapılır, şimdilik direkt başarılı sayıyoruz
            QMessageBox.information(self, "Oturum Kurtarıldı", "Önceki oturumunuz başarıyla yüklendi!")
            # self.main_window.show_dashboard()