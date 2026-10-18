import sys
import json
import urllib.request
import urllib.error
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QMessageBox
)
from PyQt5.QtCore import QTimer

class ChatClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chat Online - Design Patterns")
        self.setGeometry(200, 200, 450, 500)

        # Fila local para mensagens pendentes de reenvio (Requisito T1.3)
        self.pending_messages = []

        # Layout Principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Nome do Usuário
        self.user_layout = QHBoxLayout()
        self.user_label = QLabel("Usuário:")
        self.user_input = QLineEdit()
        self.user_input.setText("nathan")
        self.user_layout.addWidget(self.user_label)
        self.user_layout.addWidget(self.user_input)
        self.layout.addLayout(self.user_layout)

        # Área de exibição de mensagens
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.layout.addWidget(self.chat_display)

        # Entrada de texto e botão enviar
        self.input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Digite sua mensagem...")
        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.send_message)
        
        self.input_layout.addWidget(self.message_input)
        self.input_layout.addWidget(self.send_button)
        self.layout.addLayout(self.input_layout)

        # Timer para buscar novas mensagens e tentar reenvio
        self.timer = QTimer()
        self.timer.timeout.connect(self.on_timer_tick)
        self.timer.start(2000)

        self.last_messages_count = 0

    def send_message(self):
        user = self.user_input.text().strip()
        content = self.message_input.text()

        payload = {"user": user, "type": "text", "content": content}

        # Tenta enviar a mensagem
        success = self._post_to_server(payload)

        if success:
            self.message_input.clear()
            self.fetch_messages()
        else:
            # Requisito T1.3: Se falhar a conexão, guarda na fila para reenvio
            self.pending_messages.append(payload)
            self.chat_display.append("<i>[Aviso]: Servidor offline. Mensagem guardada para reenvio automático...</i>")
            self.message_input.clear()

    def _post_to_server(self, payload_dict):
        url = "http://127.0.0.1:5000/send"
        data = json.dumps(payload_dict).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

        try:
            with urllib.request.urlopen(req) as response:
                return response.status == 200
        except urllib.error.HTTPError as e:
            # Erros de validação do Proxy (ex: mensagem vazia/limite)
            error_data = json.loads(e.read().decode('utf-8'))
            QMessageBox.warning(self, "Aviso do Servidor", error_data.get("message", "Erro ao enviar"))
            return True  # Não guarda na fila de reenvio se for erro de validação do Proxy
        except urllib.error.URLError:
            return False  # Falha de conexão real (servidor desligado)

    def on_timer_tick(self):
        # 1. Tenta reenviar mensagens pendentes se o servidor tiver voltado
        if self.pending_messages:
            to_remove = []
            for msg_payload in self.pending_messages:
                if self._post_to_server(msg_payload):
                    to_remove.append(msg_payload)
            
            for sent_msg in to_remove:
                self.pending_messages.remove(sent_msg)

        # 2. Busca novas mensagens da sala
        self.fetch_messages()

    def fetch_messages(self):
        url = "http://127.0.0.1:5000/messages"
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    messages = json.loads(response.read().decode('utf-8'))
                    if len(messages) != self.last_messages_count:
                        self.chat_display.clear()
                        for msg in messages:
                            sender = msg.get("sender")
                            text = msg.get("content")
                            self.chat_display.append(f"<b>{sender}:</b> {text}")
                        self.last_messages_count = len(messages)
        except Exception:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = ChatClient()
    client.show()
    sys.exit(app.exec_())