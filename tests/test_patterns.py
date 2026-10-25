import unittest
from ModuloServidor.app import (
    MessageFactory, Message, SystemMessage, 
    UserFactory, User, 
    ChatRoomSubject, ChatProxy
)

class TestDesignPatterns(unittest.TestCase):

    def test_factory_method_messages(self):
        # Criação de mensagem normal via Factory
        msg_text = MessageFactory.create_message("text", "Manuel", "Olá")
        self.assertIsInstance(msg_text, Message)
        self.assertEqual(msg_text.to_dict()["type"], "text")

        # Criação de mensagem de sistema via Factory
        msg_sys = MessageFactory.create_message("system", "SISTEMA", "Servidor atualizado")
        self.assertIsInstance(msg_sys, SystemMessage)
        self.assertEqual(msg_sys.to_dict()["sender"], "SISTEMA")

    def test_factory_method_users(self):
        # 1. Teste da criação de usuário comum pela Factory
        user = UserFactory.create_user("Nathan")
        self.assertIsInstance(user, User)
        self.assertEqual(user.username, "Nathan")
        self.assertIsNotNone(user.color)

        # 2. Teste de rejeição de usuário com nome vazio
        with self.assertRaises(ValueError):
            UserFactory.create_user("")

    def test_observer_subject(self):
        subject = ChatRoomSubject()
        msg = MessageFactory.create_message("text", "bob", "Teste Observer")
        
        subject.notify(msg)
        messages = subject.get_messages()
        
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["content"], "Teste Observer")

    def test_proxy_validations(self):
        subject = ChatRoomSubject()
        proxy = ChatProxy(subject)

        # Usuário não cadastrado deve ser bloqueado pelo Proxy
        success, msg = proxy.send_message("usuario_nao_registrado", "text", "Olá")
        self.assertFalse(success)

        # Registro do usuário
        proxy.register_user("Toriel")

        # Envio de mensagem vazia deve ser bloqueado pelo Proxy
        success, msg = proxy.send_message("Toriel", "text", "")
        self.assertFalse(success)

        # Envio de mensagem válida
        success, msg = proxy.send_message("Toriel", "text", "Mensagem válida!")
        self.assertTrue(success)

if __name__ == "__main__":
    unittest.main()