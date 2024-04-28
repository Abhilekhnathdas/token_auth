import os
import sys
import json
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Token Authentication")
        self.token_label = QLabel("Token:")
        self.token_edit = QLineEdit()
        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.authenticate_user)

        layout = QVBoxLayout()
        layout.addWidget(self.token_label)
        layout.addWidget(self.token_edit)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def authenticate_user(self):
        token = self.token_edit.text()
        if self.validate_token(token):
            # Store the authentication token in a secure location
            self.store_authentication_cookie(token)
            self.hide()
            self.open_homepage()
        else:
            self.token_edit.clear()
            QMessageBox.warning(self, "Authentication Failed", "Invalid token.")

    def validate_token(self, token):
        response = requests.post("http://127.0.0.1:5000/validate_token", json={"token": token})
        if response.status_code == 200:
            return True
        else:
            return False

    def store_authentication_cookie(self, token):
        # Determine the path for storing the cookie
        cookie_folder = os.path.expanduser('~\\.token')
        cookie_path = os.path.join(cookie_folder, 'cookie.txt')

        # Create the token folder if it doesn't exist
        if not os.path.exists(cookie_folder):
            os.makedirs(cookie_folder)

        # Write the token to the cookie file
        with open(cookie_path, 'w') as f:
            json.dump({'token': token}, f)

    def open_homepage(self):
        self.home_page = HomePage()
        self.home_page.show()

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Home Page")
        welcome_label = QLabel("Welcome!")
        layout = QVBoxLayout()
        layout.addWidget(welcome_label)
        self.setLayout(layout)


def check_authentication():
    # Check for the presence of the authentication cookie
    cookie_path = os.path.expanduser('~\\.token\\cookie.txt')
    print(cookie_path)
    if os.path.isfile(cookie_path):
        # If cookie exists, read it
        with open(cookie_path, 'r') as f:
            cookie_data = json.load(f)
            token = cookie_data.get('token')
        # If token is present, return True
        if token:
            return True
    return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    isauth = check_authentication()
    if isauth:
        home_page = HomePage()
        home_page.show()
    else:
        auth_window = AuthWindow()
        auth_window.show()
    sys.exit(app.exec_())
