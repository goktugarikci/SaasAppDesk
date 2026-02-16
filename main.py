# main.py
import sys
import requests
import threading
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PySide6.QtCore import QSettings

from ui.views.login_view import LoginView
from ui.views.dashboard_view import DashboardView

def notify_server_status(is_online):
    """
    C++ sunucusuna kullanıcının Çevrimiçi/Çevrimdışı olduğunu bildirir.
    Arayüzü dondurmamak için işlemi Arka Planda (Thread) yapar.
    """
    def _send():
        try:
            settings = QSettings("MySaaS", "DesktopClient")
            token = settings.value("auth_token")
            
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                payload = {"online": is_online}
                
                # ÖNEMLİ: C++ tarafındaki statü güncelleme API adresinizi buraya yazın
                url = "http://localhost:8080/api/user/status" 
                
                # Sinyali gönder (3 saniye içinde yanıt gelmezse iptal et ki programı yormasın)
                response = requests.post(url, json=payload, headers=headers, timeout=3)
                
                if response.status_code == 200:
                    durum = "ÇEVRİMİÇİ" if is_online else "ÇEVRİMDIŞI"
                    print(f"[BAŞARILI] Sunucuya {durum} bilgisi iletildi.")
                else:
                    print(f"[HATA] Statü iletilemedi. Sunucu HTTP Kodu: {response.status_code}")
        except Exception as e:
            print(f"[BAĞLANTI BEKLENİYOR] C++ Sunucusuna statü iletilemedi (API yolu hatalı veya kapalı olabilir).")

    # Fonksiyon çağrıldığında arayüzü kilitlememesi için bağımsız çalıştırıyoruz
    threading.Thread(target=_send, daemon=True).start()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MySaaS Masaüstü İstemcisi")
        self.resize(1200, 800) 
        self.setMinimumSize(900, 600)
        
        self.central_stacked_widget = QStackedWidget()
        self.setCentralWidget(self.central_stacked_widget)
        
        self.login_view = LoginView(self)
        self.central_stacked_widget.addWidget(self.login_view)
        self.central_stacked_widget.setCurrentWidget(self.login_view)

    def show_dashboard(self):
        """Kullanıcı başarıyla giriş yaptığında bu fonksiyon çağrılır"""
        if not hasattr(self, 'dashboard_view'):
            self.dashboard_view = DashboardView(self)
            self.central_stacked_widget.addWidget(self.dashboard_view)
        
        self.dashboard_view.sync_settings()
        
        # 1. Arayüzde "🟢 Çevrimiçi" yap
        self.dashboard_view.set_status(True) 
        
        # 2. C++ Sunucusuna "Ben Geldim" (Online) bilgisini gönder
        notify_server_status(is_online=True)
        
        self.central_stacked_widget.setCurrentWidget(self.dashboard_view)

    def show_login(self):
        """Kullanıcı 'Çıkış Yap' (🚪) butonuna bastığında çağrılır"""
        
        # 1. C++ Sunucusuna "Ben Çıkıyorum" (Offline) bilgisini anında gönder
        notify_server_status(is_online=False)
        
        # 2. Token'ı sistemden sil
        settings = QSettings("MySaaS", "DesktopClient")
        settings.remove("auth_token") 
        
        # 3. Arayüzde "⚫ Çevrimdışı" yap
        if hasattr(self, 'dashboard_view'):
            self.dashboard_view.set_status(False) 
            
        self.login_view.reset_form()
        self.login_view.sync_settings()
        self.central_stacked_widget.setCurrentWidget(self.login_view)

    # --- PENCERE KAPATILIRKEN ÇALIŞAN HAYATİ FONKSİYON ---
    def closeEvent(self, event):
        """Kullanıcı oturumu kapatmadan sağ üstten 'X' tuşuna basıp çıkarsa"""
        settings = QSettings("MySaaS", "DesktopClient")
        token = settings.value("auth_token")
        
        if token:
            print("[SİSTEM] Uygulama 'X' ile kapatıldı. Çevrimdışı sinyali C++ sunucusuna gönderiliyor...")
            
            # Sunucuya çıkış yaptığımızı fısılda
            notify_server_status(is_online=False)
            
        event.accept() # Uygulamanın güvenle kapanmasına izin ver


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    
    # --- YENİ: BAŞLANGIÇTA OTURUM KONTROLÜ ---
    settings = QSettings("MySaaS", "DesktopClient")
    remember_me = settings.value("remember_me", False, type=bool)
    token = settings.value("auth_token", "")
    
    if remember_me and token:
        window.show_dashboard() # Oturumu açık tut işaretliyse direkt içeri gir
    else:
        window.show_login()     # İşaretli değilse Login ekranını göster
    # -----------------------------------------
    
    window.show()
    sys.exit(app.exec())