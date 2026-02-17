# ui/styles/dashboard_theme.py

def get_dashboard_stylesheet(is_dark_mode, is_mic_on, is_deafened):
    mic_bg = "transparent" if is_mic_on else "#ed4245"
    deaf_bg = "transparent" if not is_deafened else "#ed4245"
    
    if is_dark_mode:
        mic_color = "#dcddde" if is_mic_on else "#ffffff"
        mic_hover_bg = "#35393f" if is_mic_on else "#c9383b"
        deaf_color = "#dcddde" if not is_deafened else "#ffffff"
        deaf_hover_bg = "#35393f" if not is_deafened else "#c9383b"

        return f"""
            QWidget#dashboard_main, QFrame#page_bg, QStackedWidget#main_stack,
            QFrame#selection_page_main, QFrame#standard_page_main, QFrame#enterprise_page_main,
            QFrame#setup_page_main, QFrame#active_server_main, QFrame#friends_page_main {{ 
                background-color: #313338; color: #dcddde; 
            }}
            QLabel {{ color: #ffffff; }}
            
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
            QPushButton#btn_mic {{ background-color: {mic_bg}; color: {mic_color}; border: none; border-radius: 6px; font-size: 16px; }}
            QPushButton#btn_mic:hover {{ background-color: {mic_hover_bg}; color: #ffffff; }}
            QPushButton#btn_deafen {{ background-color: {deaf_bg}; color: {deaf_color}; border: none; border-radius: 6px; font-size: 16px; }}
            QPushButton#btn_deafen:hover {{ background-color: {deaf_hover_bg}; color: #ffffff; }}

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
            QPushButton#success_btn {{ background-color: #23a559; color: white; border-radius: 6px; padding: 10px 15px; font-weight: bold; font-size: 14px; border: none; }}
            QPushButton#success_btn:hover {{ background-color: #1b8546; }}
            QPushButton#text_btn {{ background-color: transparent; color: #949ba4; font-weight: bold; font-size: 13px; border: none; }}
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
            
            QListWidget#friends_list {{ background-color: #313338; border: none; outline: none; color: #dcddde; border-radius: 8px; }}
            QListWidget#friends_list::item {{ background-color: #2b2d31; padding: 15px; border-radius: 8px; margin-bottom: 8px; color: #dcddde; border: 1px solid #1e1f22; }}
            QListWidget#friends_list::item:hover {{ background-color: #35393f; }}
            
            QPushButton#tab_btn_active {{ background-color: #404249; color: white; border-radius: 6px; padding: 8px 15px; font-weight: bold; border: none; }}
            QPushButton#tab_btn_active:hover {{ background-color: #4f545c; }}
            
            QPushButton#tab_btn {{ background-color: transparent; color: #949ba4; border-radius: 6px; padding: 8px 15px; font-weight: bold; border: none; }}
            QPushButton#tab_btn:hover {{ background-color: #35393f; color: #dcddde; }}
            
            QLineEdit#search_input {{ background-color: #1e1f22; border: 1px solid #444; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #ffffff; }}
            QLineEdit#search_input:focus {{ border: 1px solid #5865f2; }}

            QMessageBox {{ background-color: #313338; color: #dcddde; }}
            QMessageBox QLabel {{ color: #dcddde; background: transparent; }}
            QMessageBox QPushButton {{ background-color: #5865f2; color: white; border-radius: 6px; padding: 6px 15px; font-weight: bold; min-width: 60px; min-height: 25px; }}
            QMessageBox QPushButton:hover {{ background-color: #4752c4; }}
        """
    else:
        mic_color = "#4e5058" if is_mic_on else "#ffffff"
        mic_hover_bg = "#e3e5e8" if is_mic_on else "#c9383b"
        mic_hover_color = "#060607" if is_mic_on else "#ffffff"
        deaf_color = "#4e5058" if not is_deafened else "#ffffff"
        deaf_hover_bg = "#e3e5e8" if not is_deafened else "#c9383b"
        deaf_hover_color = "#060607" if not is_deafened else "#ffffff"

        return f"""
            QWidget {{ color: #000000; }}
            QWidget#dashboard_main, QFrame#page_bg, QStackedWidget#main_stack,
            QFrame#selection_page_main, QFrame#standard_page_main, QFrame#enterprise_page_main,
            QFrame#setup_page_main, QFrame#active_server_main, QFrame#friends_page_main {{ 
                background-color: #ffffff; color: #000000; 
            }}
            
            QFrame#sidebar {{ background-color: #f7f8fa; border-right: 1px solid #e3e5e8; }}
            QLabel#logo_text {{ color: #000000; font-size: 18px; font-weight: 800; }}
            QLabel#menu_title {{ color: #5c5e66; font-size: 11px; font-weight: bold; margin-top: 10px; }}
            QListWidget#server_list {{ background: transparent; border: none; outline: none; }}
            QListWidget#server_list::item {{ color: #4e5058; padding: 10px 15px; border-radius: 6px; margin-bottom: 2px; font-weight: 500; }}
            QListWidget#server_list::item:hover {{ background-color: #e3e5e8; color: #000000; }}
            QListWidget#server_list::item:selected {{ background-color: #1877f2; color: #ffffff; font-weight: bold; }}
            
            QFrame#floating_profile {{ background-color: #ffffff; border-radius: 12px; border: 1px solid #e3e5e8; }}
            QLabel#profile_avatar {{ background-color: #1877f2; border-radius: 20px; color: white; font-size: 20px; }}
            QLabel#profile_user {{ color: #000000; font-weight: bold; font-size: 14px; }}
            QLabel#profile_email {{ color: #5c5e66; font-size: 11px; }}
            
            QPushButton#btn_settings {{ background: transparent; color: #4e5058; border: none; border-radius: 6px; font-size: 16px; }}
            QPushButton#btn_settings:hover {{ background-color: #f0f2f5; color: #000000; }}
            QPushButton#btn_mic {{ background-color: {mic_bg}; color: {mic_color}; border: none; border-radius: 6px; font-size: 16px; }}
            QPushButton#btn_mic:hover {{ background-color: {mic_hover_bg}; color: {mic_hover_color}; }}
            QPushButton#btn_deafen {{ background-color: {deaf_bg}; color: {deaf_color}; border: none; border-radius: 6px; font-size: 16px; }}
            QPushButton#btn_deafen:hover {{ background-color: {deaf_hover_bg}; color: {deaf_hover_color}; }}

            QFrame#content_area {{ background-color: #ffffff; }}
            QFrame#header {{ background-color: #ffffff; border-bottom: 1px solid #e3e5e8; }}
            QLabel#channel_name {{ color: #000000; font-size: 20px; font-weight: 800; }}
            QPushButton#theme_btn {{ background-color: #f0f2f5; color: #4e5058; border: 1px solid #ccd0d5; border-radius: 6px; padding: 6px 12px; font-weight: bold; }}
            QPushButton#theme_btn:hover {{ background-color: #e3e5e8; color: #000000; }}
            QPushButton#header_toggle_btn {{ background-color: transparent; color: #000000; font-size: 22px; border: none; font-weight: bold; }}
            QPushButton#header_toggle_btn:hover {{ color: #1877f2; }}
            
            QComboBox#lang_cb {{ background-color: #f0f2f5; color: #000000; border-radius: 6px; padding: 6px 10px 6px 15px; font-weight: bold; border: 1px solid #ccd0d5; }}
            QComboBox#lang_cb:hover {{ background-color: #e3e5e8; }}
            QComboBox#lang_cb::drop-down {{ border: none; width: 25px; }} 
            QComboBox#lang_cb QAbstractItemView {{ background-color: #ffffff; color: #000000; border: 1px solid #ccd0d5; border-radius: 6px; outline: none; padding: 4px; }}
            QComboBox#lang_cb QAbstractItemView::item:hover {{ background-color: #f0f2f5; color: #1877f2; }}

            QLabel#welcome_title {{ color: #000000; font-size: 32px; font-weight: 900; }}
            QLabel#welcome_sub {{ color: #4e5058; font-size: 16px; margin-bottom: 20px; }}
            QFrame#action_card {{ background-color: #ffffff; border: 1px solid #ccd0d5; border-radius: 12px; }}
            QFrame#action_card:hover {{ border: 1px solid #1877f2; background-color: #f7f8fa; }}
            QFrame#enterprise_card {{ border: 1px solid rgba(24,119,242,0.5); background-color: rgba(24,119,242,0.05); }}
            QFrame#enterprise_card:hover {{ border: 1px solid #1877f2; background-color: rgba(24,119,242,0.1); }}
            QLabel#card_icon {{ font-size: 48px; margin-bottom: 10px; }}
            QLabel#card_title {{ color: #000000; font-size: 18px; font-weight: bold; margin-bottom: 5px; }}
            QLabel#card_desc {{ color: #5c5e66; font-size: 13px; line-height: 1.4; }}
            
            QPushButton#primary_btn {{ background-color: #1877f2; color: white; border-radius: 6px; padding: 12px; font-weight: bold; font-size: 14px; border: none; }}
            QPushButton#primary_btn:hover {{ background-color: #166fe5; }}
            QPushButton#success_btn {{ background-color: #23a559; color: white; border-radius: 6px; padding: 10px 15px; font-weight: bold; font-size: 14px; border: none; }}
            QPushButton#success_btn:hover {{ background-color: #1b8546; }}
            QPushButton#text_btn {{ background-color: transparent; color: #5c5e66; font-weight: bold; font-size: 13px; border: none; }}
            QPushButton#text_btn:hover {{ color: #1877f2; text-decoration: underline; }}
            QPushButton#secondary_btn {{ background-color: #f0f2f5; color: #000000; border: 1px solid #ccd0d5; border-radius: 6px; padding: 10px; font-weight: bold; font-size: 13px; }}
            QPushButton#secondary_btn:hover {{ background-color: #e3e5e8; }}

            QFrame#payment_box {{ background-color: #f8f9fa; border: 1px solid #1877f2; border-radius: 16px; }}
            QLabel#pay_title {{ color: #1877f2; font-size: 22px; font-weight: bold; }}
            QLabel#pay_price {{ color: #000000; font-size: 36px; font-weight: 900; }}
            QLabel#pay_item {{ color: #4e5058; font-size: 15px; font-weight: 500; margin-bottom: 8px; }}
            
            QFrame#channel_sidebar {{ background-color: #f7f8fa; border-right: 1px solid #e3e5e8; }}
            QLabel#srv_title {{ color: #000000; font-size: 18px; font-weight: 800; border-bottom: 1px solid #e3e5e8; padding-bottom: 15px; }}
            QListWidget#channel_list {{ background: transparent; border: none; outline: none; }}
            QListWidget#channel_list::item {{ color: #4e5058; padding: 8px 10px; border-radius: 4px; }}
            QListWidget#channel_list::item:hover {{ background-color: #e3e5e8; color: #000000; }}
            QListWidget#channel_list::item:selected {{ background-color: #d4d7dc; color: #000000; font-weight: bold; }}
            
            QFrame#chat_area {{ background-color: #ffffff; }}
            QListWidget#msg_list {{ background: transparent; border: none; outline: none; color: #000000; }}
            QFrame#chat_input_frame {{ background-color: #f0f2f5; border-radius: 8px; border: 1px solid #ccd0d5; }}
            QLineEdit#chat_input {{ background: transparent; border: none; color: #000000; font-size: 14px; padding-left: 10px; }}

            QLineEdit {{ background-color: #ffffff; border: 1px solid #ccd0d5; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #000000; }}
            QLineEdit:focus {{ border: 2px solid #1877f2; }}
            
            QListWidget#friends_list {{ background-color: #ffffff; border: 1px solid #e3e5e8; border-radius: 8px; outline: none; color: #000000; }}
            QListWidget#friends_list::item {{ background-color: #ffffff; border-bottom: 1px solid #f0f2f5; padding: 15px; margin: 0px; color: #000000; }}
            QListWidget#friends_list::item:hover {{ background-color: #f7f8fa; }}
            
            QPushButton#tab_btn_active {{ background-color: #e3e5e8; color: #000000; border-radius: 6px; padding: 8px 15px; font-weight: bold; border: none; }}
            QPushButton#tab_btn_active:hover {{ background-color: #d4d7dc; }}
            
            QPushButton#tab_btn {{ background-color: transparent; color: #5c5e66; border-radius: 6px; padding: 8px 15px; font-weight: bold; border: none; }}
            QPushButton#tab_btn:hover {{ background-color: #f0f2f5; color: #000000; }}
            
            QLineEdit#search_input {{ background-color: #f0f2f5; border: 1px solid #ccd0d5; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #000000; }}
            QLineEdit#search_input:focus {{ border: 2px solid #1877f2; background-color: #ffffff; }}

            QMessageBox {{ background-color: #ffffff; color: #000000; }}
            QMessageBox QLabel {{ color: #000000; background: transparent; }}
            QMessageBox QPushButton {{ background-color: #1877f2; color: white; border-radius: 6px; padding: 6px 15px; font-weight: bold; min-width: 60px; min-height: 25px; border: none; }}
            QMessageBox QPushButton:hover {{ background-color: #166fe5; }}
        """

def get_dialog_stylesheet(is_dark_mode):
    if is_dark_mode:
        return """
            QFrame#dialog_bg { background-color: #313338; border-radius: 12px; border: 1px solid #1e1f22; }
            QLabel#dialog_title { color: #ffffff; font-size: 20px; font-weight: 800; }
            QLabel#dialog_sub { color: #b5bac1; font-size: 13px; }
            
            QLineEdit { background-color: #1e1f22; border: 1px solid #1e1f22; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #dbdee1; }
            QLineEdit:focus { border: 1px solid #5865f2; }
            
            /* EKLENEN KISIM: AÇILIR LİSTE (COMBOBOX) İÇİN KOYU TEMA */
            QComboBox { background-color: #1e1f22; border: 1px solid #444; border-radius: 8px; padding: 10px 15px; font-size: 14px; color: #ffffff; }
            QComboBox:hover { border: 1px solid #5865f2; }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox QAbstractItemView { background-color: #2b2d31; color: #ffffff; border: 1px solid #444; border-radius: 8px; outline: none; }
            QComboBox QAbstractItemView::item { min-height: 35px; padding-left: 10px; color: #ffffff; }
            QComboBox QAbstractItemView::item:hover, QComboBox QAbstractItemView::item:selected { background-color: #35393f; color: #ffffff; }
            
            QListWidget#result_list { background-color: transparent; border: none; outline: none; color: #dbdee1;}
            QListWidget#result_list::item { background-color: #2b2d31; border-radius: 8px; margin-bottom: 5px; }
            QListWidget#result_list::item:hover { background-color: #35393f; }
            QLabel#row_email { color: #b5bac1; font-size: 11px; }
            
            QPushButton#dialog_btn_cancel { background-color: transparent; color: #b5bac1; font-size: 14px; font-weight: bold; border-radius: 6px; padding: 10px; border: none; }
            QPushButton#dialog_btn_cancel:hover { color: #ffffff; text-decoration: underline; }
            QPushButton#dialog_btn_ok { background-color: #5865f2; color: white; font-size: 13px; font-weight: bold; border-radius: 6px; padding: 8px; border: none; }
            QPushButton#dialog_btn_ok:hover { background-color: #4752c4; }
        """
    else:
        return """
            QFrame#dialog_bg { background-color: #ffffff; border-radius: 12px; border: 1px solid #dcdfe3; }
            QLabel#dialog_title { color: #000000; font-size: 20px; font-weight: 800; }
            QLabel#dialog_sub { color: #4e5058; font-size: 13px; }
            
            QLineEdit { background-color: #f0f2f5; border: 1px solid #ccd0d5; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #000000; }
            QLineEdit:focus { border: 1px solid #1877f2; background-color: #ffffff; }
            
            /* EKLENEN KISIM: AÇILIR LİSTE (COMBOBOX) İÇİN AÇIK TEMA */
            QComboBox { background-color: #f0f2f5; border: 1px solid #ccd0d5; border-radius: 8px; padding: 10px 15px; font-size: 14px; color: #000000; }
            QComboBox:hover { border: 1px solid #1877f2; background-color: #ffffff; }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox QAbstractItemView { background-color: #ffffff; color: #000000; border: 1px solid #ccd0d5; border-radius: 8px; outline: none; }
            QComboBox QAbstractItemView::item { min-height: 35px; padding-left: 10px; color: #000000; }
            QComboBox QAbstractItemView::item:hover, QComboBox QAbstractItemView::item:selected { background-color: #f0f2f5; color: #1877f2; }
            
            QListWidget#result_list { background-color: transparent; border: none; outline: none; color: #000000;}
            QListWidget#result_list::item { background-color: #f7f8fa; border: 1px solid #e3e5e8; border-radius: 8px; margin-bottom: 5px; }
            QListWidget#result_list::item:hover { background-color: #e3e5e8; }
            QLabel#row_email { color: #5c5e66; font-size: 11px; }
            
            QPushButton#dialog_btn_cancel { background-color: transparent; color: #4e5058; font-size: 14px; font-weight: bold; border-radius: 6px; padding: 10px; border: none; }
            QPushButton#dialog_btn_cancel:hover { color: #000000; text-decoration: underline; }
            QPushButton#dialog_btn_ok { background-color: #1877f2; color: white; font-size: 13px; font-weight: bold; border-radius: 6px; padding: 8px; border: none; }
            QPushButton#dialog_btn_ok:hover { background-color: #166fe5; }
        """

def get_settings_stylesheet(is_dark_mode):
    if is_dark_mode:
        return """
            QFrame#dialog_bg { background-color: #313338; border-radius: 12px; border: 1px solid #1e1f22; }
            QFrame#settings_sidebar { background-color: #2b2d31; border-top-left-radius: 12px; border-bottom-left-radius: 12px; }
            QListWidget#settings_list { background: transparent; border: none; outline: none; font-size: 14px; font-weight: bold; }
            QListWidget#settings_list::item { color: #b5bac1; padding: 12px 15px; border-radius: 6px; margin-bottom: 5px; }
            QListWidget#settings_list::item:hover { background-color: #35393f; color: #dcddde; }
            QListWidget#settings_list::item:selected { background-color: #404249; color: #ffffff; }
            QFrame#settings_content, QFrame#settings_page_frame { background-color: #313338; border-top-right-radius: 12px; border-bottom-right-radius: 12px; }
            QLabel#settings_title { color: #ffffff; font-size: 22px; font-weight: 800; border-bottom: 1px solid #444; padding-bottom: 10px; margin-top: 15px; }
            QLabel#bold_label { color: #dcddde; font-weight: bold; font-size: 13px; }
            QLabel#desc_label, QLabel#normal_label { color: #949ba4; font-size: 13px; }
            QLabel#big_avatar { background-color: #5865f2; color: white; font-size: 36px; border-radius: 40px; }
            QPushButton#settings_close_btn { background-color: transparent; color: #949ba4; font-weight: bold; font-size: 20px; border: none; }
            QPushButton#settings_close_btn:hover { color: #ffffff; }
            QLineEdit { background-color: #1e1f22; border: 1px solid #444; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #ffffff; }
            QLineEdit:focus { border: 1px solid #5865f2; }
            QLineEdit[readOnly="true"] { background-color: #232428; color: #87909c; border: 1px solid #1e1f22; }
            
            QComboBox { background-color: #1e1f22; border: 1px solid #444; border-radius: 8px; padding: 10px 15px; font-size: 14px; color: #ffffff; font-weight: bold; }
            QComboBox:hover { border: 1px solid #5865f2; }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox QAbstractItemView { background-color: #2b2d31; color: #ffffff; border: 1px solid #444; border-radius: 8px; outline: none; }
            QComboBox QAbstractItemView::item { min-height: 35px; padding-left: 10px; }
            
            QPushButton#primary_btn { background-color: #5865f2; color: white; border-radius: 6px; padding: 12px; font-weight: bold; font-size: 14px; border: none; }
            QPushButton#primary_btn:hover { background-color: #4752c4; }
            QPushButton#secondary_btn { background-color: #2b2d31; color: #dcddde; border: 1px solid #444; border-radius: 6px; padding: 10px; font-weight: bold; font-size: 13px; }
            QPushButton#secondary_btn:hover { background-color: #35393f; }
            QPushButton#success_btn { background-color: #23a559; color: white; border-radius: 6px; padding: 10px; font-weight: bold; font-size: 13px; border: none; }
            QPushButton#success_btn:hover { background-color: #1b8546; }
            
            QFrame#account_box { background-color: #2b2d31; border: 1px solid #1e1f22; border-radius: 8px; }
            QPushButton#upgrade_btn { background-color: #f1c40f; color: #000; font-weight: bold; border-radius: 6px; padding: 10px; font-size: 14px; border: none; }
            QPushButton#upgrade_btn:hover { background-color: #d4ac0d; }
            QScrollArea#settings_scroll { background: transparent; border: none; }
            QScrollArea#settings_scroll > QWidget > QWidget { background: transparent; }
            
            QListWidget#channel_settings_list { background-color: #1e1f22; border: 1px solid #444; border-radius: 8px; outline: none; color: #dcddde; padding: 5px;}
            QListWidget#channel_settings_list::item { background-color: #2b2d31; border-radius: 6px; margin-bottom: 3px; padding: 10px; }
            QListWidget#channel_settings_list::item:hover { background-color: #35393f; }
            QListWidget#channel_settings_list::item:selected { background-color: #404249; color: #ffffff; font-weight: bold; border: 1px solid #5865f2; }
            
            QMessageBox { background-color: #313338; color: #dcddde; }
            QMessageBox QLabel { color: #dcddde; background: transparent; }
            QMessageBox QPushButton { background-color: #5865f2; color: white; border-radius: 6px; padding: 6px 15px; font-weight: bold; min-width: 60px; min-height: 25px; border: none; }
            QMessageBox QPushButton:hover { background-color: #4752c4; }
        """
    else:
        return """
            QFrame#dialog_bg { background-color: #ffffff; border-radius: 12px; border: 1px solid #ccc; }
            QFrame#settings_sidebar { background-color: #f7f8fa; border-top-left-radius: 12px; border-bottom-left-radius: 12px; border-right: 1px solid #e3e5e8; }
            QListWidget#settings_list { background: transparent; border: none; outline: none; font-size: 14px; font-weight: bold; }
            QListWidget#settings_list::item { color: #4e5058; padding: 12px 15px; border-radius: 6px; margin-bottom: 5px; }
            QListWidget#settings_list::item:hover { background-color: #e3e5e8; color: #000000; }
            QListWidget#settings_list::item:selected { background-color: #d4d7dc; color: #000000; }
            QFrame#settings_content, QFrame#settings_page_frame { background-color: #ffffff; border-top-right-radius: 12px; border-bottom-right-radius: 12px; }
            QLabel#settings_title { color: #000000; font-size: 22px; font-weight: 800; border-bottom: 1px solid #e3e5e8; padding-bottom: 10px; margin-top: 15px; }
            QLabel#bold_label { color: #000000; font-weight: bold; font-size: 13px; }
            QLabel#desc_label, QLabel#normal_label { color: #5c5e66; font-size: 13px; }
            QLabel#big_avatar { background-color: #1877f2; color: white; font-size: 36px; border-radius: 40px; }
            QPushButton#settings_close_btn { background-color: transparent; color: #5c5e66; font-weight: bold; font-size: 20px; border: none; }
            QPushButton#settings_close_btn:hover { color: #000000; }
            QLineEdit { background-color: #f0f2f5; border: 1px solid #ccd0d5; border-radius: 8px; padding: 0 15px; font-size: 14px; color: #000000; }
            QLineEdit:focus { border: 2px solid #1877f2; background-color: #ffffff; }
            QLineEdit[readOnly="true"] { background-color: #e3e5e8; color: #5c5e66; border: 1px solid #ccc; }
            
            QComboBox { background-color: #f0f2f5; border: 1px solid #ccd0d5; border-radius: 8px; padding: 10px 15px; font-size: 14px; color: #000000; font-weight: bold; }
            QComboBox:hover { border: 1px solid #1877f2; background-color: #ffffff; }
            QComboBox::drop-down { border: none; width: 30px; }
            QComboBox QAbstractItemView { background-color: #ffffff; color: #000000; border: 1px solid #ccd0d5; border-radius: 8px; outline: none; }
            QComboBox QAbstractItemView::item { min-height: 35px; padding-left: 10px; color: #000000;}
            QComboBox QAbstractItemView::item:hover, QComboBox QAbstractItemView::item:selected { background-color: #f0f2f5; color: #1877f2; }
            
            QPushButton#primary_btn { background-color: #1877f2; color: white; border-radius: 6px; padding: 12px; font-weight: bold; font-size: 14px; border: none; }
            QPushButton#primary_btn:hover { background-color: #166fe5; }
            QPushButton#secondary_btn { background-color: #f7f8fa; color: #000000; border: 1px solid #ccd0d5; border-radius: 6px; padding: 10px; font-weight: bold; font-size: 13px; }
            QPushButton#secondary_btn:hover { background-color: #e3e5e8; }
            QPushButton#success_btn { background-color: #23a559; color: white; border-radius: 6px; padding: 10px; font-weight: bold; font-size: 13px; border: none; }
            QPushButton#success_btn:hover { background-color: #1b8546; }
            
            QFrame#account_box { background-color: #f7f8fa; border: 1px solid #e3e5e8; border-radius: 8px; }
            QPushButton#upgrade_btn { background-color: #f1c40f; color: #000; font-weight: bold; border-radius: 6px; padding: 10px; font-size: 14px; border: none; }
            QPushButton#upgrade_btn:hover { background-color: #d4ac0d; }
            QScrollArea#settings_scroll { background: transparent; border: none; }
            QScrollArea#settings_scroll > QWidget > QWidget { background: transparent; }
            
            QListWidget#channel_settings_list { background-color: #ffffff; border: 1px solid #ccd0d5; border-radius: 8px; outline: none; color: #000000; padding: 5px;}
            QListWidget#channel_settings_list::item { background-color: #f7f8fa; border-radius: 6px; margin-bottom: 3px; padding: 10px; color: #000000; }
            QListWidget#channel_settings_list::item:hover { background-color: #e3e5e8; }
            QListWidget#channel_settings_list::item:selected { background-color: #d4d7dc; color: #000000; font-weight: bold; border: 1px solid #1877f2; }
            
            QMessageBox { background-color: #ffffff; color: #000000; }
            QMessageBox QLabel { color: #000000; background: transparent; }
            QMessageBox QPushButton { background-color: #1877f2; color: white; border-radius: 6px; padding: 6px 15px; font-weight: bold; min-width: 60px; min-height: 25px; border: none; }
            QMessageBox QPushButton:hover { background-color: #166fe5; }
        """