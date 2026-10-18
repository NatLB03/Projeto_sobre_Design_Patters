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

        # Layout Principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Nome do Usuário
        self.user_layout = QHBoxLayout()
        self.user_label = QLabel("Usuário:")
        self.user_input = QLineEdit()
        self.user_input.setText("nathan")  # Usuário padrão do Proxy
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

        # Timer para buscar novas mensagens periodicamente (Polling)
        self.timer = QTimer()
        self.timer.timeout.connect(self.fetch_messages)
        self.timer.start(2000)  # Atualiza a cada 2 segundos

        self.last_messages_count = 0

    def send_message(self):
        user = self.user_input.text().strip()
        content = self.message_input.text()

        url = "http://127.0.0.1:5000/send"
        payload = json.dumps({
            "user": user,
            "type": "text",
            "content": content
        }).encode('utf-8')

        req = urllib.request.Request(
            url, 
            data=payload, 
            headers={'Content-Type': 'application/json'}
        )

        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    self.message_input.clear()
                    self.fetch_messages()
        except urllib.error.HTTPError as e:
            # Captura a validação do Proxy (ex: mensagem vazia, limite de caracteres ou usuário inválido)
            error_data = json.loads(e.read().decode('utf-8'))
            QMessageBox.warning(self, "Aviso do Servidor", error_data.get("message", "Erro ao enviar"))
        except urllib.error.URLError:
            # Requisito T1.3: Tratamento de falha de conexão
            QMessageBox.critical(self, "Erro de Conexão", "Não foi possível conectar ao servidor Flask.")

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
            pass  # Ignora erros temporários na atualização de fundo

if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = ChatClient()
    client.show()
    sys.exit(app.exec_())