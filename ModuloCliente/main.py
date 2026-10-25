import sys
import json
import urllib.request
import urllib.error
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QMessageBox
)
from PyQt5.QtCore import QTimer, Qt

class ChatClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Online — Design Patterns")
        self.setGeometry(200, 200, 520, 620)

        self.pending_messages = []
        self.last_messages_count = 0
        self.is_registered = False

        self.init_ui()
        self.apply_styles()

        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer_tick)
        self.timer.start(2000)

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(12)

        # Cabeçalho
        self.user_layout = QHBoxLayout()
        self.user_label = QLabel("Usuário:")
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Digite seu nome e clique em Entrar...")

        self.join_button = QPushButton("Entrar / Cadastrar")
        self.join_button.setCursor(Qt.PointingHandCursor)
        self.join_button.clicked.connect(self.register_user)

        self.user_layout.addWidget(self.user_label)
        self.user_layout.addWidget(self.user_input)
        self.user_layout.addWidget(self.join_button)
        self.main_layout.addLayout(self.user_layout)

        # Área do Chat
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.main_layout.addWidget(self.chat_display)

        # Entrada de Mensagem
        self.input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Registre-se para enviar mensagens...")
        self.message_input.setEnabled(False)
        self.message_input.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Enviar")
        self.send_button.setCursor(Qt.PointingHandCursor)
        self.send_button.setEnabled(False)
        self.send_button.clicked.connect(self.send_message)

        self.input_layout.addWidget(self.message_input)
        self.input_layout.addWidget(self.send_button)
        self.main_layout.addLayout(self.input_layout)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e2e; }
            QWidget { color: #cdd6f4; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14px; }
            QLabel { font-weight: bold; color: #a6adc8; }
            QLineEdit {
                background-color: #313244;
                border: 1px solid #45475a;
                border-radius: 8px;
                padding: 8px 12px;
                color: #cdd6f4;
            }
            QLineEdit:disabled { background-color: #181825; color: #585b70; }
            QLineEdit:focus { border: 1px solid #89b4fa; }
            QTextEdit {
                background-color: #181825;
                border: 1px solid #313244;
                border-radius: 10px;
                padding: 12px;
                color: #cdd6f4;
            }
            QPushButton {
                background-color: #89b4fa;
                color: #11111b;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 9px 16px;
            }
            QPushButton:hover { background-color: #b4befe; }
            QPushButton:disabled { background-color: #45475a; color: #6c7086; }
        """)

    def register_user(self):
        username = self.user_input.text().strip()
        if not username:
            QMessageBox.warning(self, "Aviso", "Digite um nome de usuário válido.")
            return

        payload = {"user": username}
        url = "http://127.0.0.1:5000/register"
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    res_data = json.loads(response.read().decode('utf-8'))
                    QMessageBox.information(self, "Sucesso", res_data.get("message"))
                    
                    self.is_registered = True
                    self.user_input.setEnabled(False)
                    self.join_button.setEnabled(False)
                    self.message_input.setEnabled(True)
                    self.send_button.setEnabled(True)
                    self.message_input.setPlaceholderText("Digite sua mensagem...")
                    self.fetch_messages()
        except urllib.error.HTTPError as e:
            error_data = json.loads(e.read().decode('utf-8'))
            QMessageBox.warning(self, "Erro de Registro", error_data.get("message"))
        except urllib.error.URLError:
            QMessageBox.critical(self, "Erro de Conexão", "Não foi possível conectar ao servidor para registrar.")

    def send_message(self):
        if not self.is_registered:
            QMessageBox.warning(self, "Aviso", "Registre-se primeiro!")
            return

        user = self.user_input.text().strip()
        content = self.message_input.text().strip()

        if not content:
            QMessageBox.warning(self, "Aviso", "Mensagem vazia não é permitida.")
            return

        payload = {"user": user, "type": "text", "content": content}

        success = self._post_to_server(payload)

        if success:
            self.message_input.clear()
            self.fetch_messages()
        else:
            # Requisito T1.3: Exibe mensagem de erro na tela e guarda para reenvio
            self.pending_messages.append(payload)
            self.chat_display.append(
                f"<div style='margin-bottom: 8px;'><span style='color: #f38ba8; font-weight: bold;'>{user} (ERRO DE ENVIO - AGUARDANDO RECONEXÃO):</span> <span style='color: #a6adc8;'><i>{content}</i></span></div>"
            )
            self.message_input.clear()

    def _post_to_server(self, payload_dict):
        url = "http://127.0.0.1:5000/send"
        data = json.dumps(payload_dict).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

        try:
            with urllib.request.urlopen(req) as response:
                return response.status == 200
        except urllib.error.HTTPError as e:
            error_data = json.loads(e.read().decode('utf-8'))
            QMessageBox.warning(self, "Aviso do Servidor", error_data.get("message", "Erro ao enviar"))
            return True
        except urllib.error.URLError:
            return False

    def on_timer_tick(self):
        # Tenta reenviar pendentes
        if self.pending_messages:
            to_remove = []
            for msg_payload in self.pending_messages:
                if self._post_to_server(msg_payload):
                    to_remove.append(msg_payload)
            
            for sent_msg in to_remove:
                self.pending_messages.remove(sent_msg)

        self.fetch_messages()

    def fetch_messages(self):
        url = "http://127.0.0.1:5000/messages"
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    messages = json.loads(response.read().decode('utf-8'))
                    if len(messages) != self.last_messages_count or self.pending_messages:
                        self.chat_display.clear()
                        for msg in messages:
                            sender = msg.get("sender")
                            text = msg.get("content")
                            msg_type = msg.get("type", "text")
                            user_color = msg.get("color", "#89b4fa")

                            if msg_type == "system":
                                self.chat_display.append(
                                    f"<div style='margin-bottom: 8px;'><span style='color: #f38ba8; font-weight: bold;'>[SISTEMA]:</span> <span style='color: #f9e2af;'>{text}</span></div>"
                                )
                            else:
                                self.chat_display.append(
                                    f"<div style='margin-bottom: 8px;'><span style='color: {user_color}; font-weight: bold;'>{sender}:</span> <span>{text}</span></div>"
                                )
                        
                        # Se houver mensagens ainda na fila de pendentes, renderiza ao final com o aviso em vermelho
                        for p_msg in self.pending_messages:
                            self.chat_display.append(
                                f"<div style='margin-bottom: 8px;'><span style='color: #f38ba8; font-weight: bold;'>{p_msg['user']} (FALHA NO ENVIO - REENTENTANDO...):</span> <span style='color: #a6adc8;'><i>{p_msg['content']}</i></span></div>"
                            )

                        self.last_messages_count = len(messages)
        except Exception:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = ChatClient()
    client.show()
    sys.exit(app.exec_())