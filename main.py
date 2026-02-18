# main.py
import sys
import requests
import threading
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QMessageBox
from PySide6.QtCore import Qt
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
                requests.post(url, json=payload, headers=headers, timeout=3)
                
        except Exception:
            # Bağlantı hatası olursa program akışını bozma
            pass

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
        """
        Kullanıcı başarıyla giriş yaptığında bu fonksiyon çağrılır.
        Her zaman YENİ bir Dashboard oluşturur (Eski verileri önler).
        """
        # Eğer hafızada eski bir dashboard kaldıysa onu temizle (Garanti önlem)
        if hasattr(self, 'dashboard_view'):
            self.central_stacked_widget.removeWidget(self.dashboard_view)
            self.dashboard_view.deleteLater()
            del self.dashboard_view

        # Sıfırdan temiz bir Dashboard oluştur
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
        # Beni hatırla seçeneğini de sıfırla ki otomatik girmesin
        settings.remove("remember_me") 
        
        # 3. CRITICAL: DASHBOARD'I HAFIZADAN TAMAMEN SİL (ÖNBELLEK TEMİZLİĞİ)
        if hasattr(self, 'dashboard_view'):
            # StackedWidget'tan çıkar
            self.central_stacked_widget.removeWidget(self.dashboard_view)
            # Nesneyi yok et
            self.dashboard_view.deleteLater()
            # Değişkeni sil
            del self.dashboard_view
            
        # 4. Login formunu temizle ve göster
        self.login_view.reset_form()
        self.login_view.sync_settings()
        self.central_stacked_widget.setCurrentWidget(self.login_view)

    # --- PENCERE KAPATILIRKEN ÇALIŞAN HAYATİ FONKSİYON ---
    def closeEvent(self, event):
        """Kullanıcı oturumu kapatmadan sağ üstten 'X' tuşuna basıp çıkarsa"""
        settings = QSettings("MySaaS", "DesktopClient")
        token = settings.value("auth_token")
        
        if token:
            # Sunucuya çıkış yaptığımızı fısılda
            notify_server_status(is_online=False)
            
        event.accept() # Uygulamanın güvenle kapanmasına izin ver

if __name__ == "__main__":
    # --- YENİ: PERFORMANS VE GPU AYARLARI ---
    # Uygulama başlamadan önce ayarları oku
    temp_settings = QSettings("MySaaS", "DesktopClient")
    use_gpu = temp_settings.value("use_gpu", True, type=bool)
    perf_mode = temp_settings.value("perf_mode", "balanced", type=str)
    
    # 1. GPU Hızlandırma Ayarı
    if use_gpu:
        # OpenGL ve GPU paylaşımını aktif et (Arayüz Hızlandırma)
        QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
        QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
        # Bazı sistemlerde şu da işe yarar:
        # QApplication.setAttribute(Qt.AA_UseOpenGLES) 
    else:
        # GPU'yu kapat (Yazılımsal Render - Düşük donanımlar için)
        QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)

    app = QApplication(sys.argv)
    
    # 2. Performans Moduna Göre Ayarlar
    # (Örnek: Animasyon sürelerini global olarak kısabiliriz veya thread önceliğini artırabiliriz)
    if perf_mode == "high":
        # Yüksek performans için efektleri azaltma mantığı buraya eklenebilir
        pass 
    elif perf_mode == "eco":
        # Güç tasarrufu işlemleri
        pass

    window = MainWindow()
    
    # Oturum Kontrolü
    remember_me = temp_settings.value("remember_me", False, type=bool)
    token = temp_settings.value("auth_token", "")
    
    if remember_me and token:
        window.show_dashboard() 
    else:
        window.show_login()    
    
    window.show()
    sys.exit(app.exec())