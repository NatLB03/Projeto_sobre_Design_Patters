import unittest
from ModuloServidor.app import MessageFactory, Message, SystemMessage, ChatRoomSubject

class TestDesignPatterns(unittest.TestCase):

    def test_factory_method(self):
        # Teste da criação de mensagem normal
        msg_text = MessageFactory.create_message("text", "alice", "Olá")
        self.assertIsInstance(msg_text, Message)
        self.assertEqual(msg_text.to_dict()["type"], "text")

        # Teste da criação de mensagem do sistema
        msg_sys = MessageFactory.create_message("system", "admin", "Manutenção")
        self.assertIsInstance(msg_sys, SystemMessage)
        self.assertEqual(msg_sys.to_dict()["sender"], "SISTEMA")

    def test_observer_subject(self):
        subject = ChatRoomSubject()
        msg = MessageFactory.create_message("text", "bob", "Teste Observer")
        
        subject.notify(msg)
        messages = subject.get_messages()
        
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["content"], "Teste Observer")

if __name__ == "__main__":
    unittest.main()