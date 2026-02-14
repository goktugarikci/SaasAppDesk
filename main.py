# main.py
import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from ui.views.login_view import LoginView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MySaaS Masaüstü İstemcisi")
        self.resize(1024, 768) # Başlangıç pencere boyutu
        
        # İlk açılışta Login ekranını göster
        self.show_login()

    def show_login(self):
        self.login_view = LoginView(self)
        self.setCentralWidget(self.login_view)
        
    # İleride buraya show_dashboard, show_chat gibi fonksiyonlar eklenecek

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Tüm uygulama için genel font veya stil ayarları yapılabilir
    app.setStyle("Fusion") 
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())