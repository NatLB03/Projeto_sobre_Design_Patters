# Chat Online — Design Patterns

Projeto de chat cliente-servidor desenvolvido para a disciplina de Padrões de Projeto, demonstrando os padrões **Factory Method**, **Proxy** e **Observer**.

---

## 🏗️ Arquitetura do Projeto

* **`ModuloServidor/app.py`**: API REST desenvolvida em **Flask** contendo os 3 padrões de projeto:
  * **Factory Method**: Instanciação dinâmica de `User`/`AdminUser` e `Message`/`SystemMessage`.
  * **Proxy**: Controle de permissões de usuários autorizados e validação de regras de mensagens (não vazia e limite de caracteres).
  * **Observer**: Gerenciamento do histórico e distribuição de mensagens.
* **`ModuloCliente/main.py`**: Interface Gráfica interativa construída com **PyQt5** para envio, recepção via polling e fila local para reenvio automático em caso de queda de conexão.
* **`tests/test_patterns.py`**: Suíte de testes automatizados unitários usando `unittest`.

---

## 🚀 Como Executar

### 1. Instalar as dependências
```bash
pip install -r requirements
```

### 2. Executar o Servidor (Flask)
```bash
python ModuloServidor/app.py
```
O servidor estará rodando em `http://127.0.0.1:5000`.

### 3. Executar o Cliente (PyQt5)
Em um novo terminal, execute:
```bash
python ModuloCliente/main.py
```

### 4. Executar os Testes Automatizados (T1.4)
```bash
python -m unittest discover -s tests
```

---

## 🧪 Cenários de Teste Demonstrados

* **T1.1 — Envio e atualização da conversa**: Envio de mensagem pela interface gráfica, processada pela Factory/Proxy no servidor e atualizada no chat.
* **T1.2 — Mensagem vazia e limite de tamanho**: O `ChatProxy` bloqueia mensagens vazias ou com mais de 500 caracteres, exibindo alertas `QMessageBox` no cliente.
* **T1.3 — Falha de conexão e reenvio**: Se o servidor for interrompido, as mensagens enviadas ficam na fila `pending_messages` do cliente e são retransformadas/reenviadas automaticamente quando o servidor voltar.
* **T1.4 — Observer e Factory Method**: Cobertura realizada pelos testes unitários no módulo `tests/`.