# Sistema de Memória IA com SQLAlchemy

Sistema avançado de memória para agentes de IA que mantém contexto e histórico de conversas longas, agora com persistência em banco de dados SQLite usando SQLAlchemy.

## 📋 Funcionalidades

### ✅ Funcionalidades Mantidas (Versão Original)
- ✅ Memória de curto prazo (contexto imediato da conversa)
- ✅ Memória de longo prazo (perfis de usuário persistentes)
- ✅ Extração automática de informações do usuário
- ✅ Consolidação inteligente de conhecimento
- ✅ Criação de resumos de conversas longas
- ✅ Compatibilidade com OpenAI GPT

### 🆕 Novas Funcionalidades (Versão SQLAlchemy)
- 🆕 **Persistência robusta** com SQLite + SQLAlchemy
- 🆕 **Estrutura de dados normalizada** com relacionamentos
- 🆕 **Performance otimizada** para conversas longas
- 🆕 **Limpeza automática** de mensagens antigas
- 🆕 **Múltiplos resumos** por usuário com histórico
- 🆕 **Migração de dados** do formato pickle
- 🆕 **Testes abrangentes** incluindo casos extremos

## 🏗️ Arquitetura

```
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   Memória Curto     │    │   Banco SQLite      │    │   OpenAI API        │
│   Prazo (deque)     │◄──►│   + SQLAlchemy      │◄──►│   GPT-3.5/4         │
│                     │    │                     │    │                     │
│ • Contexto atual    │    │ • Perfis usuários   │    │ • Geração respostas │
│ • Últimas msgs      │    │ • Histórico msgs    │    │ • Extração info     │
│ • Performance       │    │ • Resumos conversa  │    │ • Sumarização       │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
```

## 📁 Estrutura de Arquivos

```
projeto/
├── database_models.py      # 🆕 Modelos SQLAlchemy + DatabaseManager
├── memory_sqlalchemy.py    # 🆕 Sistema de memória com SQLAlchemy
├── migrate_pickle_to_db.py # 🆕 Script de migração de dados
├── memory.py              # ✅ Sistema original (mantido)
├── prompt.py              # ✅ Templates de prompts (mantido)
├── main.py               # ✅ Testes originais (mantido + novos)
├── requirements.txt      # 🆕 Dependências atualizadas
└── README.md            # 🆕 Esta documentação
```

## 🚀 Instalação

```bash
# Clone ou baixe os arquivos
pip install -r requirements.txt

# Configure sua API key OpenAI
echo "OPENAI_API_KEY=sua_chave_aqui" > .env
```

## 💾 Banco de Dados

### Estrutura das Tabelas

```sql
-- Perfis de usuários
CREATE TABLE user_profiles (
    id TEXT PRIMARY KEY,           -- user_id
    name TEXT,                    -- Nome do usuário
    interests TEXT,               -- JSON array de interesses
    preferences TEXT,             -- Preferências do usuário
    context TEXT,                -- Contexto relevante
    first_interaction DATETIME,   -- Primeira interação
    last_interaction DATETIME,    -- Última interação
    created_at DATETIME,          -- Data de criação
    updated_at DATETIME           -- Data de atualização
);

-- Mensagens do histórico
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,       -- Auto increment
    user_id TEXT,                -- FK para user_profiles
    role TEXT,                   -- 'user', 'assistant', 'system'
    content TEXT,                -- Conteúdo da mensagem
    timestamp DATETIME,          -- Timestamp da mensagem
    metadata TEXT                -- JSON com metadados
);

-- Resumos de conversas
CREATE TABLE conversation_summaries (
    id INTEGER PRIMARY KEY,       -- Auto increment
    user_id TEXT,                -- FK para user_profiles
    summary TEXT,                -- Resumo da conversa
    created_at DATETIME,         -- Data de criação
    message_count INTEGER        -- Número de mensagens resumidas
);

-- Base de conhecimento geral
CREATE TABLE knowledge_base (
    id INTEGER PRIMARY KEY,       -- Auto increment
    key TEXT UNIQUE,             -- Chave do conhecimento
    value TEXT,                  -- Valor/conteúdo
    category TEXT,               -- Categoria
    created_at DATETIME,         -- Data de criação
    updated_at DATETIME          -- Data de atualização
);
```

## 🔧 Como Usar

### Uso Básico (Nova Versão SQLAlchemy)

```python
import asyncio
from memory_sqlalchemy import TestSQLAlchemyMemoryAgent

async def exemplo_basico():
    # Inicializa sistema com SQLAlchemy
    memory_system = TestSQLAlchemyMemoryAgent(
        model="gpt-3.5-turbo",
        short_term_limit=10,
        database_url="sqlite:///minha_memoria.db"
    )
    
    user_id = "usuario_123"
    
    # Conversa é automaticamente persistida
    response = await memory_system.generate_response(
        user_id, 
        "Olá! Meu nome é João e trabalho com Python."
    )
    
    print(f"Assistente: {response}")
    
    # Perfil é consolidado automaticamente
    profile = memory_system.get_user_profile(user_id)
    print(f"Perfil: {profile}")

# Execute
asyncio.run(exemplo_basico())
```

### Compatibilidade com Versão Original

```python
# A nova versão mantém compatibilidade total
from memory_sqlalchemy import TestMemoryAgent  # Alias para compatibilidade
from memory import TestMemoryAgent as Original  # Versão original

# Ambas têm a mesma interface
memory_new = TestMemoryAgent()  # SQLAlchemy version
memory_old = Original()         # Pickle version
```

### Operações Avançadas do Banco

```python
from database_models import DatabaseManager

# Acesso direto ao banco
db = DatabaseManager("sqlite:///memoria.db")

# Operações manuais
db.update_user_profile("user123", {
    "name": "Maria Silva",
    "interests": ["IA", "Python", "Data Science"],
    "preferences": "Respostas técnicas detalhadas"
})

# Limpeza de dados antigos
deleted = db.cleanup_old_messages("user123", keep_last=50)
print(f"Removidas {deleted} mensagens antigas")

# Consultas personalizadas
recent_messages = db.get_recent_messages("user123", limit=10)
summaries = db.get_conversation_summaries("user123")
```

## 🔄 Migração de Dados

Se você tem dados na versão anterior (pickle), use o script de migração:

```python
from migrate_pickle_to_db import migrate_pickle_to_sqlite

# Migra arquivo pickle existente
success = migrate_pickle_to_sqlite(
    "ai_agent_memory.pkl",  # arquivo pickle
    "sqlite:///memoria.db"  # banco destino
)

if success:
    print("Migração concluída com sucesso!")
```

### Teste de Migração

```bash
# Executa script completo de migração
python migrate_pickle_to_db.py

# Cria dados de exemplo e testa migração
```

## 🧪 Executar Testes

### Testes Básicos (sem API key)

```bash
# Executa todos os testes que não precisam de API
python main.py
```

### Testes Completos (com API key)

```bash
# Configure sua API key primeiro
export OPENAI_API_KEY="sua_chave_aqui"

# Descomente as linhas com chamadas reais da API em main.py
# Depois execute:
python main.py
```

### Testes Individuais

```python
# Teste só o banco de dados
from main import test_database_operations
test_database_operations()

# Teste conversa longa
from main import test_long_conversation
import asyncio
asyncio.run(test_long_conversation())

# Comparação entre versões
from main import test_memory_comparison
test_memory_comparison()
```

## 📊 Performance e Otimizações

### Configurações Recomendadas

```python
memory_system = TestSQLAlchemyMemoryAgent(
    model="gpt-3.5-turbo",
    short_term_limit=10,        # Mensagens em memória
    max_tokens=4000,            # Tokens por resposta
    database_url="sqlite:///memoria.db"
)

# Configurações internas (via memory_agent)
memory_system.memory_agent.consolidation_threshold = 5   # Consolida a cada 5 msgs
memory_system.memory_agent.summary_trigger = 15         # Sumariza a cada 15 msgs
memory_system.memory_agent.max_messages_per_user = 100  # Máximo por usuário
```

### Otimizações Implementadas

- ✅ **Índices automáticos** nas chaves estrangeiras
- ✅ **Limpeza automática** de mensagens antigas
- ✅ **Memória híbrida**: curto prazo em RAM, longo prazo em DB
- ✅ **Consolidação inteligente** apenas quando necessário
- ✅ **Sessões otimizadas** do SQLAlchemy com context managers

## 🔍 Debugging e Monitoramento

### Logs de Debug

```python
# Ative logs para debug
import logging
logging.basicConfig(level=logging.INFO)

# O sistema mostrará:
# 📝 User profile {user_id} updated: {dados}
# 📄 Conversation summary created for user {user_id}
# 🗑️ Removed {n} old messages for user {user_id}
# 💾 Memory is automatically saved in database
```

### Verificar Estado do Sistema

```python
# Verificar dados de um usuário
profile = memory_system.get_user_profile("user_123")
print(f"Perfil: {profile}")

# Contar mensagens
message_count = memory_system.memory_agent.db.get_message_count("user_123")
print(f"Total de mensagens: {message_count}")

# Ver resumos
summaries = memory_system.memory_agent.get_conversation_summaries("user_123")
print(f"Resumos: {summaries}")
```

## ⚙️ Configurações Avançadas

### Customizar Banco de Dados

```python
# PostgreSQL
memory_system = TestSQLAlchemyMemoryAgent(
    database_url="postgresql://user:pass@localhost/memoria"
)

# MySQL
memory_system = TestSQLAlchemyMemoryAgent(
    database_url="mysql://user:pass@localhost/memoria"
)

# SQLite com configurações específicas
memory_system = TestSQLAlchemyMemoryAgent(
    database_url="sqlite:///memoria.db?check_same_thread=False"
)
```

### Customizar Prompts

```python
# Edite prompt.py para personalizar extração e sumarização
from prompt import get_extract_system_message, get_create_system_message

# Os prompts são templates que podem ser modificados
```

## 🚨 Tratamento de Erros

### Erros Comuns e Soluções

```python
# Erro: "no such table"
# Solução: O banco é criado automaticamente na primeira execução
db = DatabaseManager("sqlite:///novo_banco.db")  # Cria tabelas automaticamente

# Erro: "API key not found" 
# Solução: Configure a variável de ambiente
import os
os.environ["OPENAI_API_KEY"] = "sua_chave"

# Erro: "JSON decode error"
# Solução: Sistema ignora informações mal formatadas e continua
```

### Recuperação de Dados

```python
# Backup automático recomendado
import shutil
from datetime import datetime

# Backup diário
backup_name = f"memoria_backup_{datetime.now().strftime('%Y%m%d')}.db"
shutil.copy2("memoria.db", backup_name)
```

## 📈 Roadmap e Melhorias Futuras

### Em Desenvolvimento
- [ ] Suporte a múltiplos modelos de IA (Anthropic Claude, Gemini)
- [ ] Interface web para visualização de dados
- [ ] Análise de sentimentos automática
- [ ] Clustering de usuários por similaridade
- [ ] API REST para integração externa

### Possíveis Melhorias
- [ ] Cache em Redis para ultra performance
- [ ] Suporte a conversas em grupo
- [ ] Análise de padrões comportamentais
- [ ] Exportação para formatos diversos
- [ ] Dashboard de analytics

## 🤝 Contribuição

### Como Contribuir
1. Fork do projeto
2. Crie branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões de Código
- Use type hints em Python
- Docstrings no formato Google
- Testes para novas funcionalidades
- Mantenha compatibilidade com versão original

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para detalhes.

## 🏆 Comparação: Antes vs Depois

| Aspecto | Versão Original (Pickle) | Nova Versão (SQLAlchemy) |
|---------|-------------------------|--------------------------|
| **Persistência** | Arquivo pickle | Banco SQLite |
| **Performance** | Carrega tudo na RAM | Híbrido: RAM + DB |
| **Escalabilidade** | Limitada | Suporte a milhões de msgs |
| **Consultas** | Linear (O(n)) | Indexadas (O(log n)) |
| **Integridade** | Sem garantias | ACID compliance |
| **Backup** | Cópia de arquivo | Backup incremental |
| **Multi-usuário** | Não suportado | Totalmente suportado |
| **Análise** | Difícil | Queries SQL flexíveis |

## ❓ FAQ

**P: Preciso migrar meus dados antigos?**
R: Não é obrigatório. A nova versão funciona independentemente, mas o script de migração está disponível.

**P: A nova versão é mais lenta?**
R: Não. Na verdade é mais rápida para conversas longas devido ao sistema híbrido de memória.

**P: Posso usar ambas as versões no mesmo projeto?**
R: Sim, elas são compatíveis e podem coexistir.

**P: Qual banco de dados usar em produção?**
R: SQLite para até ~100k mensagens. PostgreSQL para escala maior.

**P: Como fazer backup dos dados?**
R: Copie o arquivo `.db` ou use ferramentas específicas do banco escolhido.

---

💡 **Dica**: Para começar rapidamente, execute `python main.py` e veja os exemplos funcionando!

🔗 **Links Úteis**: 
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [OpenAI API](https://platform.openai.com/docs)
- [SQLite Documentation](https://www.sqlite.org/docs.html)