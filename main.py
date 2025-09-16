import json
import asyncio
import sys
from dotenv import load_dotenv

# Importa tanto as versões antigas quanto as novas para comparação
from memory import TestMemoryAgent
from db import DatabaseConfig

_ = load_dotenv()  # força a execução

async def exemplo_chatbot_com_memoria():
    """
    Demonstração prática de um chatbot com sistema de memória
    """
    print("=== CHATBOT COM SISTEMA DE MEMÓRIA ===\n")
    
    # Inicializa o sistema de memória original
    memory_system = TestMemoryAgent(
        model="gpt-3.5-turbo",
        short_term_limit=8
    )
    
    # Simula uma conversa
    user_id = "usuario_123"
    
    # Primeira interação
    print("👤 Usuário: Olá! Meu nome é Maria e eu gosto muito de fotografia.")
    response1 = await memory_system.generate_response(
        user_id, 
        "Olá! Meu nome é Maria e eu gosto muito de fotografia."
    )
    print(f"🤖 Assistente: {response1}\n")
    
    # Segunda interação
    print("👤 Usuário: Você poderia me recomendar uma boa câmera para iniciantes?")
    response2 = await memory_system.generate_response(
        user_id,
        "Você poderia me recomendar uma boa câmera para iniciantes?"
    )
    print(f"🤖 Assistente: {response2}\n")
    
    # Terceira interação (testando memória)
    print("👤 Usuário: Qual era mesmo meu hobby favorito?")
    response3 = await memory_system.generate_response(
        user_id,
        "Qual era mesmo meu hobby favorito?"
    )
    print(f"🤖 Assistente: {response3}\n")
    
    # Mostra perfil consolidado
    profile = memory_system.get_user_profile(user_id)
    print(f"📋 Perfil consolidado: {json.dumps(profile, indent=2, default=str)}")
    
    return memory_system

async def exemplo_chatbot_sqlalchemy():
    """
    Demonstração prática de um chatbot com sistema de memória - VERSÃO SQLALCHEMY
    """
    print("\n" + "="*60)
    print("=== CHATBOT COM SQLALCHEMY MEMORY SYSTEM ===\n")
    
    # Inicializa o sistema de memória SQLAlchemy
    memory_system = TestMemoryAgent(
        model="gpt-3.5-turbo",
        short_term_limit=8,
        database_url="sqlite:///test_chat_memory.db"
    )
    
    # Simula uma conversa
    user_id = "usuario_sqlalchemy_123"
    
    # Primeira interação
    print("👤 Usuário: Olá! Meu nome é Ana e eu sou desenvolvedora Python.")
    response1 = await memory_system.generate_response(
        user_id, 
        "Olá! Meu nome é Ana e eu sou desenvolvedora Python."
    )
    print(f"🤖 Assistente: {response1}\n")
    
    # Segunda interação
    print("👤 Usuário: Você conhece SQLAlchemy? Estou aprendendo sobre ORMs.")
    response2 = await memory_system.generate_response(
        user_id,
        "Você conhece SQLAlchemy? Estou aprendendo sobre ORMs."
    )
    print(f"🤖 Assistente: {response2}\n")
    
    # Terceira interação (testando memória)
    print("👤 Usuário: Qual é minha profissão mesmo?")
    response3 = await memory_system.generate_response(
        user_id,
        "Qual é minha profissão mesmo?"
    )
    print(f"🤖 Assistente: {response3}\n")
    
    # Quarta interação - teste de persistência
    print("👤 Usuário: Também gosto de machine learning e data science.")
    response4 = await memory_system.generate_response(
        user_id,
        "Também gosto de machine learning e data science."
    )
    print(f"🤖 Assistente: {response4}\n")
    
    # Mostra perfil consolidado
    profile = memory_system.get_user_profile(user_id)
    print(f"📋 Perfil consolidado SQLAlchemy: {json.dumps(profile, indent=2, default=str)}")
    
    # Mostra resumos de conversa
    summaries = memory_system.memory_agent.get_conversation_summaries(user_id)
    if summaries:
        print(f"📄 Resumos de conversa: {summaries}")
    
    return memory_system


async def test_database_operations():
    """
    Testa operações específicas do banco de dados
    """
    print("\n" + "="*60)
    print("=== TESTE DE OPERAÇÕES DO BANCO DE DADOS ===\n")
    
    # Cria gerenciador de banco
    db = DatabaseConfig("sqlite:///test_operations.db")
    
    test_user_id = "test_user_db"
    
    # Teste 1: Criar e atualizar perfil
    print("📝 Teste 1: Criação e atualização de perfil")
    profile = db.get_or_create_user_profile(test_user_id)
    print(f"   Perfil criado: {profile.id}")
    
    # Atualizar perfil
    updates = {
        "name": "João Silva",
        "interests": ["programação", "games", "música"],
        "preferences": "Prefere respostas detalhadas",
        "context": "Estudante de engenharia"
    }
    db.update_user_profile(test_user_id, updates)
    
    updated_profile = db.get_user_profile_dict(test_user_id)
    print(f"   Perfil atualizado: {updated_profile}")
    print("   ✅ Teste 1 passou\n")
    
    # Teste 2: Adicionar mensagens
    print("📨 Teste 2: Adição de mensagens")
    messages_to_add = [
        ("user", "Olá, eu gosto de programação"),
        ("assistant", "Oi! Legal saber que você gosta de programação. Em que linguagens você trabalha?"),
        ("user", "Principalmente Python e JavaScript"),
        ("assistant", "Excelentes escolhas! Python é ótimo para data science e JavaScript para web.")
    ]
    
    for role, content in messages_to_add:
        db.add_message(test_user_id, role, content, {"test": True})
    
    recent_messages = db.get_recent_messages(test_user_id, limit=5)
    print(f"   Mensagens adicionadas: {len(recent_messages)}")
    for msg in recent_messages:
        print(f"     {msg['role']}: {msg['content'][:50]}...")
    print("   ✅ Teste 2 passou\n")
    
    # Teste 3: Resumos de conversa
    print("📄 Teste 3: Resumos de conversa")
    db.add_conversation_summary(test_user_id, "Usuário João Silva demonstrou interesse em programação, especialmente Python e JavaScript.", 4)
    
    summaries = db.get_conversation_summaries(test_user_id)
    print(f"   Resumos criados: {len(summaries)}")
    for i, summary in enumerate(summaries):
        print(f"     {i+1}: {summary[:60]}...")
    print("   ✅ Teste 3 passou\n")
    
    # Teste 4: Limpeza de mensagens antigas
    print("🗑️ Teste 4: Limpeza de mensagens antigas")
    # Adiciona mais mensagens para testar limpeza
    for i in range(10):
        db.add_message(test_user_id, "user", f"Mensagem de teste {i}", {"test": True})
    
    total_before = db.get_message_count(test_user_id)
    deleted = db.cleanup_old_messages(test_user_id, keep_last=5)
    total_after = db.get_message_count(test_user_id)
    
    print(f"   Mensagens antes: {total_before}")
    print(f"   Mensagens removidas: {deleted}")
    print(f"   Mensagens depois: {total_after}")
    print("   ✅ Teste 4 passou\n")


async def test_long_conversation():
    """
    Testa comportamento com conversas longas
    """
    print("\n" + "="*60)
    print("=== TESTE DE CONVERSA LONGA ===\n")
    
    memory_system = TestMemoryAgent(
        short_term_limit=5,  # Limite baixo para forçar consolidação
        database_url="sqlite:///long_conversation_test.db"
    )
    
    user_id = "long_conversation_user"
    
    # Simula conversa longa
    conversation_topics = [
        "Olá! Sou Maria, desenvolvedora full-stack",
        "Trabalho principalmente com React e Node.js",
        "Tenho 3 anos de experiência em desenvolvimento web",
        "Atualmente estou aprendendo sobre microservices",
        "Também me interesso por DevOps e containerização",
        "Uso Docker no meu trabalho diário",
        "Estou estudando Kubernetes agora",
        "Minha empresa está migrando para a nuvem",
        "Prefiro AWS como cloud provider",
        "Também tenho interesse em machine learning",
        "Estou fazendo um curso de Python para data science",
        "Qual é minha linguagem principal mesmo?"  # Teste de memória
    ]
    
    print("🔄 Simulando conversa longa...")
    for i, message in enumerate(conversation_topics):
        print(f"   {i+1:2d}/12: Processando mensagem...")
        
        if i < len(conversation_topics) - 1:  # Não chama API na última (é só teste)
            # Simula resposta sem chamar API real
            memory_system.add_message(user_id, "user", message)
            memory_system.add_message(user_id, "assistant", f"Resposta simulada para: {message[:30]}...")
        else:
            # Última mensagem - teste de memória
            try:
                response = await memory_system.generate_response(user_id, message)
                print(f"🤖 Resposta final: {response}")
            except Exception as e:
                print(f"💡 Simulando resposta (sem API): Baseado no seu perfil, você trabalha principalmente com React e Node.js!")
    
    # Verifica estado final
    final_profile = memory_system.get_user_profile(user_id)
    message_count = memory_system.memory_agent.db.get_message_count(user_id)
    summaries = memory_system.memory_agent.get_conversation_summaries(user_id)
    
    print(f"\n📊 Resultado do teste de conversa longa:")
    print(f"   Mensagens total: {message_count}")
    print(f"   Resumos criados: {len(summaries)}")
    print(f"   Perfil final: {final_profile}")
    print("   ✅ Teste de conversa longa concluído")


async def run_simple_tests():
    try:
        print(" Executando testes")
        await exemplo_chatbot_com_memoria()
    except Exception as e:
        print(f"⚠️ Erro no teste simples: {e}")

async def run_complete_tests():  
    try:
        print("\n Executando testes completos ...")
        await exemplo_chatbot_sqlalchemy() 
        await test_database_operations()
        await test_long_conversation()
    except Exception as e:
        print(f"⚠️ Erro nos testes: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    # Para usar com API real, descomente as linhas abaixo:
    if len(sys.argv) > 1:
        modo = sys.argv[1].lower()
        
        if modo == "simple":
            asyncio.run(run_simple_tests())
        elif modo == "complete":
            asyncio.run(run_complete_tests())
        else:
            print("❌ Modo inválido. Use: simples, completo, database, ou memoria")
    else:
        # Padrão: executa testes simples
        asyncio.run(run_simple_tests())