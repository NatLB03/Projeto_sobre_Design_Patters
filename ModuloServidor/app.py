from flask import Flask, request, jsonify

app = Flask(__name__)

# --- 1. DESIGN PATTERN: FACTORY METHOD ---
class Message:
    def __init__(self, sender, content):
        self.sender = sender
        self.content = content

    def to_dict(self):
        return {"sender": self.sender, "content": self.content, "type": "text"}

class SystemMessage(Message):
    def to_dict(self):
        return {"sender": "SISTEMA", "content": self.content, "type": "system"}

class MessageFactory:
    @staticmethod
    def create_message(msg_type, sender, content):
        if msg_type == "text":
            return Message(sender, content)
        elif msg_type == "system":
            return SystemMessage("SISTEMA", content)
        else:
            raise ValueError(f"Tipo de mensagem inválido: {msg_type}")


# --- 2. DESIGN PATTERN: OBSERVER ---
class ChatRoomSubject:
    def __init__(self):
        self._messages = []  # Histórico em memória

    def notify(self, message_obj):
        data = message_obj.to_dict()
        self._messages.append(data)

    def get_messages(self):
        return self._messages

chat_room = ChatRoomSubject()


# --- 3. DESIGN PATTERN: PROXY ---
class ChatProxy:
    def __init__(self, subject):
        self._subject = subject
        self._allowed_users = ["alice", "bob", "carol", "nathan","Josué","Josue"]  # Usuários autorizados

    def send_message(self, user, msg_type, content):
        # Validação 1: Permissão/Identidade
        if user not in self._allowed_users:
            return False, "Acesso negado: Usuário não cadastrado/permitido."

        # Validação 2: Requisito T1.2 - Mensagem vazia e limite de tamanho
        clean_content = content.strip()
        if not clean_content:
            return False, "Mensagem vazia não é permitida."
        if len(clean_content) > 500:
            return False, "Mensagem excede o limite de 500 caracteres."

        # Se passou na verificação do Proxy, usa a Factory e notifica o Objeto Real
        msg_obj = MessageFactory.create_message(msg_type, user, clean_content)
        self._subject.notify(msg_obj)
        return True, "Mensagem enviada com sucesso!"

chat_proxy = ChatProxy(chat_room)


# --- ENDPOINTS FLASK ---
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