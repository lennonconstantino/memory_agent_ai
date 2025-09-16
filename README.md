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

### 📋 Explicação Detalhada das Tabelas

#### 🧑‍💼 **UserProfile** - Perfis de Usuários
**Para que serve:** Armazena informações personalizadas e contexto de cada usuário individual.

**Campos principais:**
- `id`: Identificador único do usuário (chave primária)
- `name`: Nome do usuário (extraído automaticamente das conversas)
- `interests`: Lista de interesses em formato JSON (ex: `["programação", "música", "viagem"]`)
- `preferences`: Preferências de comunicação (ex: "respostas técnicas detalhadas")
- `context`: Contexto relevante sobre o usuário (ex: "estudante de engenharia")
- `first_interaction` / `last_interaction`: Controle temporal das interações

**Como é usado:**
- ✅ **Personalização**: Respostas adaptadas ao perfil do usuário
- ✅ **Contexto persistente**: Lembra informações entre sessões
- ✅ **Extração automática**: IA identifica e armazena dados relevantes
- ✅ **Relacionamentos**: Conecta com mensagens e resumos

**Exemplo de uso:**
```python
# Perfil criado automaticamente
profile = {
    "name": "Maria Silva",
    "interests": ["Python", "Machine Learning", "Data Science"],
    "preferences": "Explicações técnicas detalhadas",
    "context": "Desenvolvedora com 3 anos de experiência"
}
```

#### 💬 **Message** - Histórico de Mensagens
**Para que serve:** Armazena todo o histórico de conversas entre usuários e o assistente.

**Campos principais:**
- `id`: Identificador único da mensagem (auto increment)
- `user_id`: Referência ao usuário (chave estrangeira)
- `role`: Tipo de mensagem (`user`, `assistant`, `system`)
- `content`: Conteúdo da mensagem
- `timestamp`: Quando a mensagem foi enviada
- `metadata`: Dados extras em JSON (ex: sentimento, tópicos, etc.)

**Como é usado:**
- ✅ **Histórico completo**: Todas as conversas ficam salvas
- ✅ **Contexto imediato**: Últimas mensagens para respostas
- ✅ **Análise temporal**: Padrões de conversa ao longo do tempo
- ✅ **Auditoria**: Rastreamento completo das interações

**Exemplo de uso:**
```python
# Mensagem salva automaticamente
message = {
    "user_id": "user_123",
    "role": "user",
    "content": "Como implementar machine learning em Python?",
    "timestamp": "2024-01-15 14:30:00",
    "metadata": {"sentiment": "curious", "topic": "ml"}
}
```

#### 📄 **ConversationSummary** - Resumos de Conversas
**Para que serve:** Resumos inteligentes de conversas longas para manter contexto sem sobrecarregar o sistema.

**Campos principais:**
- `id`: Identificador único do resumo
- `user_id`: Referência ao usuário
- `summary`: Resumo gerado pela IA das conversas
- `created_at`: Quando o resumo foi criado
- `message_count`: Quantas mensagens foram resumidas

**Como é usado:**
- ✅ **Otimização de performance**: Evita usar todas as mensagens como contexto
- ✅ **Preservação de contexto**: Informações importantes não se perdem
- ✅ **Economia de tokens**: Reduz custos da API OpenAI
- ✅ **Escalabilidade**: Suporta conversas muito longas

**Exemplo de resumo:**
```
"Maria é uma desenvolvedora Python interessada em machine learning e data science. 
Ela tem 3 anos de experiência e prefere explicações técnicas detalhadas. 
Na conversa atual, discutimos implementação de algoritmos de classificação 
usando scikit-learn e TensorFlow."
```

#### 🧠 **KnowledgeBase** - Base de Conhecimento Geral
**Para que serve:** Armazena conhecimento compartilhado e informações gerais que não são específicas de usuários.

**Campos principais:**
- `id`: Identificador único do conhecimento
- `key`: Chave única para identificar o conhecimento (ex: "python_basics")
- `value`: Conteúdo do conhecimento
- `category`: Categoria para organização (ex: "programming", "company", "faq")
- `created_at` / `updated_at`: Controle temporal

**Como é usado:**
- ✅ **FAQ da empresa**: Perguntas e respostas frequentes
- ✅ **Políticas**: Regras e diretrizes da organização
- ✅ **Dicas técnicas**: Conhecimento técnico compartilhado
- ✅ **Procedimentos**: Passo a passo de processos
- ✅ **Informações gerais**: Dados acessíveis por todos os usuários

**Exemplo de uso:**
```python
# Conhecimento adicionado
knowledge = {
    "key": "python_best_practices",
    "value": "Sempre use type hints e docstrings em Python para melhor legibilidade",
    "category": "programming"
}
```

### 🔄 Relacionamentos entre Tabelas

```mermaid
erDiagram
    UserProfile ||--o{ Message : "tem"
    UserProfile ||--o{ ConversationSummary : "possui"
    
    UserProfile {
        string id PK
        string name
        string interests
        string preferences
        string context
        datetime first_interaction
        datetime last_interaction
        datetime created_at
        datetime updated_at
    }
    
    Message {
        int id PK
        string user_id FK
        string role
        text content
        datetime timestamp
        text metadata
    }
    
    ConversationSummary {
        int id PK
        string user_id FK
        text summary
        datetime created_at
        int message_count
    }
    
    KnowledgeBase {
        int id PK
        string key UK
        text value
        string category
        datetime created_at
        datetime updated_at
    }
```

### 🎯 Casos de Uso Práticos

#### **1. Sistema de Suporte ao Cliente**
```python
# Cenário: Cliente com problema técnico
# UserProfile: Armazena histórico do cliente, preferências de atendimento
# Message: Registra toda conversa de suporte
# ConversationSummary: Resume problemas anteriores para contexto
# KnowledgeBase: FAQ, procedimentos de suporte, soluções comuns
```

#### **2. Assistente Educacional**
```python
# Cenário: Estudante aprendendo programação
# UserProfile: Nível de conhecimento, linguagens de interesse
# Message: Perguntas e explicações durante as aulas
# ConversationSummary: Resumo do progresso de aprendizado
# KnowledgeBase: Conceitos de programação, exercícios, tutoriais
```

#### **3. Consultor de Negócios**
```python
# Cenário: Consultoria empresarial
# UserProfile: Empresa do cliente, setor, necessidades
# Message: Discussões sobre estratégias e implementações
# ConversationSummary: Resumo de reuniões e decisões
# KnowledgeBase: Metodologias, frameworks, cases de sucesso
```

#### **4. Chatbot de E-commerce**
```python
# Cenário: Loja online
# UserProfile: Preferências de compra, histórico de pedidos
# Message: Consultas sobre produtos e pedidos
# ConversationSummary: Padrões de compra e preferências
# KnowledgeBase: Catálogo de produtos, políticas da loja, FAQ
```

### ⚡ Fluxo de Funcionamento do Sistema

```mermaid
graph TD
    A[Usuário envia mensagem] --> B[Sistema adiciona à Message]
    B --> C[Atualiza UserProfile se necessário]
    C --> D{Conversa tem 15+ mensagens?}
    D -->|Sim| E[IA cria ConversationSummary]
    D -->|Não| F[Usa contexto atual]
    E --> G[Salva resumo no banco]
    G --> H[Limpa mensagens antigas da memória]
    H --> F
    F --> I[Busca KnowledgeBase se necessário]
    I --> J[Gera resposta com contexto completo]
    J --> K[Salva resposta como Message]
    K --> L[Retorna resposta ao usuário]
```

### 📊 Vantagens da Arquitetura

| Aspecto | Benefício |
|---------|-----------|
| **Personalização** | Cada usuário tem perfil único e contexto preservado |
| **Performance** | Resumos evitam sobrecarga com conversas longas |
| **Escalabilidade** | Suporta milhares de usuários e mensagens |
| **Flexibilidade** | KnowledgeBase permite conhecimento compartilhado |
| **Auditoria** | Histórico completo de todas as interações |
| **Inteligência** | IA extrai e consolida informações automaticamente |

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

### 🧠 Trabalhando com KnowledgeBase

```python
from db import DatabaseConfig
from repository import MemoryRepository

# Configuração
db_config = DatabaseConfig("sqlite:///minha_base.db")
db = MemoryRepository(db_config)

# Adicionar conhecimento individual
db.add_knowledge(
    key="python_tip",
    value="Use list comprehensions para operações em listas",
    category="programming"
)

# Geração de massa
conhecimentos = [
    {"key": "python_basics", "value": "Python é uma linguagem interpretada", "category": "programming"},
    {"key": "company_policy", "value": "Horário de trabalho: 9h às 18h", "category": "company"},
    {"key": "faq_what_is_ai", "value": "IA é a capacidade de máquinas executarem tarefas inteligentes", "category": "faq"}
]

added_count = db.bulk_add_knowledge(conhecimentos)
print(f"Adicionados {added_count} conhecimentos")

# Buscar conhecimento
python_tip = db.get_knowledge("python_tip")
print(f"Dica Python: {python_tip}")

# Buscar por categoria
programming_tips = db.get_knowledge_by_category("programming")
print(f"Dicas de programação: {len(programming_tips)}")

# Buscar por termo
results = db.search_knowledge("Python")
print(f"Resultados para 'Python': {len(results)}")

# Atualizar conhecimento
db.update_knowledge("python_tip", "Use list comprehensions para operações eficientes em listas")

# Remover conhecimento
db.delete_knowledge("python_tip")
```

### 📚 Exemplos de Conhecimento por Categoria

#### **Programação**
```python
programming_knowledge = [
    {"key": "python_functions", "value": "Funções em Python: def nome_funcao():", "category": "programming"},
    {"key": "python_classes", "value": "Classes: class MinhaClasse: def __init__(self):", "category": "programming"},
    {"key": "python_imports", "value": "Imports: import math ou from math import sqrt", "category": "programming"}
]
```

#### **Empresa**
```python
company_knowledge = [
    {"key": "company_mission", "value": "Nossa missão é inovar em tecnologia", "category": "company"},
    {"key": "company_values", "value": "Valores: Inovação, Qualidade, Transparência", "category": "company"},
    {"key": "company_contact", "value": "Contato: contato@empresa.com | (11) 99999-9999", "category": "company"}
]
```

#### **FAQ**
```python
faq_knowledge = [
    {"key": "faq_what_is_ml", "value": "Machine Learning permite que computadores aprendam sem programação explícita", "category": "faq"},
    {"key": "faq_how_to_start", "value": "Para começar em IA: Python, matemática, estatística, machine learning", "category": "faq"},
    {"key": "faq_ai_ethics", "value": "Ética em IA: transparência, justiça, responsabilidade", "category": "faq"}
]
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

# Executa todos os testes incluindo KnowledgeBase
python main.py complete
```

### Testes Específicos

```bash
# Teste apenas da KnowledgeBase (geração de massa)
python main.py knowledge

# Teste simples (chatbot básico)
python main.py simple
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

# Teste da KnowledgeBase
from main import test_knowledge_base_mass_generation
import asyncio
asyncio.run(test_knowledge_base_mass_generation())
```

### 🧠 Teste da KnowledgeBase

O teste da KnowledgeBase demonstra todas as funcionalidades de geração de massa:

```bash
python main.py knowledge
```

**O que o teste faz:**
- ✅ **Geração de massa** com 30 conhecimentos (programação, empresa, FAQ)
- ✅ **Operações CRUD** completas (criar, ler, atualizar, deletar)
- ✅ **Busca por termo** e categoria
- ✅ **Teste de performance** com 100+ registros
- ✅ **Validação de dados** inseridos
- ✅ **Limpeza automática** de dados de teste

**Resultado esperado:**
```
📚 Teste 1: Geração de massa - Dados de Programação
   Conhecimentos de programação adicionados: 10

🏢 Teste 2: Geração de massa - Dados da Empresa
   Conhecimentos da empresa adicionados: 10

❓ Teste 3: Geração de massa - FAQ
   Conhecimentos de FAQ adicionados: 10

🔍 Teste 4: Verificação de Dados Inseridos
   Total de conhecimentos na base: 30

⚡ Teste 7: Performance com Muitos Dados
   Conhecimentos de performance adicionados: 100
   Tempo de inserção: 0.01 segundos
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