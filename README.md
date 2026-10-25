# Chat Online — Design Patterns

Aplicação de chat cliente-servidor desenvolvida para a disciplina de Padrões de Projeto, demonstrando a aplicação dos padrões **Factory Method**, **Proxy** e **Observer**.

---

## 🏗️ Arquitetura e Padrões de Projeto

O projeto está dividido nos módulos exigidos:

* **`ModuloServidor/app.py`**: API REST em **Flask** contendo a lógica central:
  * **Factory Method**:
    * `UserFactory`: Instanciação dinâmica de utilizadores (`User`).
    * `MessageFactory`: Criação das mensagens de texto (`Message`) e avisos do sistema (`SystemMessage`).
  * **Proxy**:
    * `ChatProxy`: Validação de acesso ao chat (bloqueia utilizadores não registados) e controlo de regras de mensagens (mensagens vazias e limite de 500 caracteres).
  * **Observer**:
    * `ChatRoomSubject`: Registo e distribuição do histórico de mensagens aos clientes.
  * **Persistência Local**: Leitura e escrita num arquivo `data.json` sem uso de bancos de dados.

* **`ModuloCliente/main.py`**: Interface Gráfica interativa desenvolvida em **PyQt5**:
  * Tema Escuro (*Dark Mode*) responsivo.
  * Atribuição de cores únicas e aleatórias por perfil de utilizador.
  * Envio por tecla `Enter` e atualizações via *polling*.
  * Tratamento visual de erro e fila local de reenvio automático para cenários de servidor *offline*.

* **`tests/test_patterns.py`**: Suíte de testes automatizados unitários usando `unittest` para validação dos padrões e regras de negócio.

---

## 🚀 Como Executar

### 1. Instalar as Dependências
```bash
pip install -r requirements.txt
```

### 2. Iniciar o Servidor (Flask)
```bash
python ModuloServidor/app.py
```
O servidor iniciará em `http://127.0.0.1:5000`.

### 3. Iniciar o Cliente (PyQt5)
Em um novo terminal, execute:
```bash
python ModuloCliente/main.py
```

### 4. Executar os Testes Automatizados (T1.4)
```bash
python -m unittest discover -s tests
```

---

## 🧪 Cenários de Teste Cobertos

* **T1.1 — Envio e Atualização**: Envio de mensagens em tempo real com atualização periódica na interface.
* **T1.2 — Mensagem Vazia e Limite**: O `ChatProxy` bloqueia conteúdos inválidos ou que excedam 500 caracteres, emitindo alertas no cliente.
* **T1.3 — Falha de Conexão e Reenvio**: Em caso de queda do servidor, o cliente exibe um aviso visual em vermelho e guarda a mensagem numa fila local para reenvio automático assim que a conexão restabelecer.
* **T1.4 — Observer e Factory Method**: Verificação da criação de objetos e notificação garantida através da suíte em `tests/test_patterns.py`.