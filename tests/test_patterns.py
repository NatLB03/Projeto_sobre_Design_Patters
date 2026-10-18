import unittest
from ModuloServidor.app import (
    MessageFactory, Message, SystemMessage, 
    UserFactory, User, AdminUser, 
    ChatRoomSubject
)

class TestDesignPatterns(unittest.TestCase):

    def test_factory_method_messages(self):
        # Teste da criação de mensagem normal
        msg_text = MessageFactory.create_message("text", "alice", "Olá")
        self.assertIsInstance(msg_text, Message)
        self.assertEqual(msg_text.to_dict()["type"], "text")

        # Teste da criação de mensagem do sistema
        msg_sys = MessageFactory.create_message("system", "admin", "Manutenção")
        self.assertIsInstance(msg_sys, SystemMessage)
        self.assertEqual(msg_sys.to_dict()["sender"], "SISTEMA")

    def test_factory_method_users(self):
        # 1. Teste da criação de usuário comum pela Factory
        user_common = UserFactory.create_user("usuário_comum", role="user")
        self.assertIsInstance(user_common, User)
        self.assertEqual(user_common.username, "usuário_comum")
        self.assertEqual(user_common.role, "user")

        # 2. Teste da criação de usuário Admin pela Factory
        user_admin = UserFactory.create_user("boss", role="admin")
        self.assertIsInstance(user_admin, AdminUser)
        self.assertEqual(user_admin.username, "boss")
        self.assertEqual(user_admin.role, "admin")

        # 3. Teste do comportamento de erro (garante que a Factory rejeita papéis inválidos)
        with self.assertRaises(ValueError):
            UserFactory.create_user("errado", role="nãoexistente")

    def test_observer_subject(self):
        subject = ChatRoomSubject()
        msg = MessageFactory.create_message("text", "bob", "Teste Observer")
        
        subject.notify(msg)
        messages = subject.get_messages()
        
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["content"], "Teste Observer")

if __name__ == "__main__":
    unittest.main()