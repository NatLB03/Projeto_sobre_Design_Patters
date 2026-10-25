import os
import json
import random
from flask import Flask, request, jsonify

app = Flask(__name__)

DATA_FILE = "data.json"

# --- 1. DESIGN PATTERN: FACTORY METHOD ---

class Message:
    def __init__(self, sender, content, color="#89b4fa"):
        self.sender = sender
        self.content = content
        self.color = color

    def to_dict(self):
        return {
            "sender": self.sender, 
            "content": self.content, 
            "type": "text",
            "color": self.color
        }

class SystemMessage(Message):
    def to_dict(self):
        return {
            "sender": "SISTEMA", 
            "content": self.content, 
            "type": "system",
            "color": "#f38ba8"
        }


class User:
    AVAILABLE_COLORS = [
        "#89b4fa", "#f5e0dc", "#FB91EF", "#f5c2e7", "#cba6f7", 
        "#f38ba8", "#fab387", "#f9e2af", "#a6e3a1", "#94e2d5", 
        "#89dceb", "#e5e87f", "#79BD8E"
    ]
    _color_queue = []

    def __init__(self, username, color=None):
        self.username = username
        self.color = color if color else self._get_next_unique_color()

    @classmethod
    def _get_next_unique_color(cls):
        if not cls._color_queue:
            cls._color_queue = cls.AVAILABLE_COLORS.copy()
            random.shuffle(cls._color_queue)
        return cls._color_queue.pop(0)


class MessageFactory:
    @staticmethod
    def create_message(msg_type, sender, content, color="#89b4fa"):
        if msg_type == "text":
            return Message(sender, content, color=color)
        elif msg_type == "system":
            return SystemMessage("SISTEMA", content)
        else:
            raise ValueError(f"Tipo de mensagem inválido: {msg_type}")

class UserFactory:
    @staticmethod
    def create_user(username, color=None):
        if not username or not username.strip():
            raise ValueError("Nome de usuário inválido/vazio.")
        return User(username.strip(), color=color)


# --- 2. DESIGN PATTERN: OBSERVER ---
class ChatRoomSubject:
    def __init__(self):
        self._messages = []

    def notify(self, message_obj):
        data = message_obj.to_dict()
        self._messages.append(data)

    def get_messages(self):
        return self._messages

    def load_messages(self, messages_list):
        self._messages = messages_list

chat_room = ChatRoomSubject()


# --- 3. DESIGN PATTERN: PROXY ---
class ChatProxy:
    def __init__(self, subject):
        self._subject = subject
        self._registered_users = {}
        self._load_data()

    def _save_data(self):
        """Salva usuários e mensagens num arquivo JSON local (sem banco de dados)."""
        data = {
            "users": {name: user.color for name, user in self._registered_users.items()},
            "messages": self._subject.get_messages()
        }
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def _load_data(self):
        """Carrega dados salvos quando o servidor inicia."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    # Recria os objetos User via UserFactory
                    saved_users = data.get("users", {})
                    for name, color in saved_users.items():
                        user_obj = UserFactory.create_user(name, color=color)
                        self._registered_users[name] = user_obj
                    
                    # Restaura as mensagens no Observer
                    saved_msgs = data.get("messages", [])
                    self._subject.load_messages(saved_msgs)
            except Exception as e:
                print(f"Erro ao carregar dados salvos: {e}")

    def register_user(self, user_name):
        clean_name = user_name.strip()
        if not clean_name:
            return False, "Nome de usuário não pode ser vazio."
        
        # Se já existe, re-conecta mantendo os dados
        if clean_name in self._registered_users:
            return True, f"Bem-vindo de volta, {clean_name}!"

        user_obj = UserFactory.create_user(clean_name)
        self._registered_users[user_obj.username] = user_obj
        
        sys_msg = MessageFactory.create_message("system", "SISTEMA", f"{user_obj.username} entrou no chat.")
        self._subject.notify(sys_msg)
        self._save_data()
        
        return True, f"Usuário '{clean_name}' registrado com sucesso!"

    def send_message(self, user_name, msg_type, content):
        if user_name not in self._registered_users:
            return False, "Acesso negado: Usuário não cadastrado. Registre-se primeiro!"

        clean_content = content.strip()
        if not clean_content:
            return False, "Mensagem vazia não é permitida."
        if len(clean_content) > 500:
            return False, "Mensagem excede o limite de 500 caracteres."

        user_obj = self._registered_users[user_name]
        msg_obj = MessageFactory.create_message(msg_type, user_name, clean_content, color=user_obj.color)
        
        self._subject.notify(msg_obj)
        self._save_data()
        return True, "Mensagem enviada com sucesso!"

chat_proxy = ChatProxy(chat_room)


# --- ENDPOINTS FLASK ---
@app.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    user = data.get("user", "")

    success, result_message = chat_proxy.register_user(user)

    if success:
        return jsonify({"status": "ok", "message": result_message}), 200
    else:
        return jsonify({"status": "error", "message": result_message}), 400

@app.route("/send", methods=["POST"])
def send_message():
    data = request.json or {}
    user = data.get("user", "")
    msg_type = data.get("type", "text")
    content = data.get("content", "")

    success, result_message = chat_proxy.send_message(user, msg_type, content)

    if success:
        return jsonify({"status": "ok", "message": result_message}), 200
    else:
        return jsonify({"status": "error", "message": result_message}), 400

@app.route("/messages", methods=["GET"])
def get_messages():
    return jsonify(chat_room.get_messages()), 200

if __name__ == "__main__":
    print("Servidor rodando em http://127.0.0.1:5000")
    app.run(debug=True, port=5000)