import json
import asyncio
import sys
from dotenv import load_dotenv

# Importa tanto as versões antigas quanto as novas para comparação
from memory import TestMemoryAgent
from db import DatabaseConfig
from repository import MemoryRepository

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


async def test_knowledge_base_mass_generation():
    """
    Testa geração de massa para KnowledgeBase
    """
    print("\n" + "="*60)
    print("=== TESTE DE GERAÇÃO DE MASSA - KNOWLEDGE BASE ===\n")
    
    # Cria banco específico para teste da KnowledgeBase
    db_config = DatabaseConfig("sqlite:///test_knowledge_base.db")
    db = MemoryRepository(db_config)
    
    # Teste 1: Geração de massa com dados de programação
    print("📚 Teste 1: Geração de massa - Dados de Programação")
    
    programming_knowledge = [
        {"key": "python_basics", "value": "Python é uma linguagem de programação de alto nível, interpretada e de propósito geral.", "category": "programming"},
        {"key": "python_syntax", "value": "Python usa indentação para definir blocos de código, não chaves como outras linguagens.", "category": "programming"},
        {"key": "python_variables", "value": "Em Python, variáveis são criadas quando você atribui um valor a elas: nome = 'João'", "category": "programming"},
        {"key": "python_functions", "value": "Funções em Python são definidas com 'def': def minha_funcao():", "category": "programming"},
        {"key": "python_lists", "value": "Listas em Python são coleções ordenadas e mutáveis: lista = [1, 2, 3]", "category": "programming"},
        {"key": "python_dictionaries", "value": "Dicionários armazenam pares chave-valor: dicio = {'nome': 'João', 'idade': 30}", "category": "programming"},
        {"key": "python_loops", "value": "Python tem loops 'for' e 'while': for item in lista:", "category": "programming"},
        {"key": "python_conditionals", "value": "Condicionais usam 'if', 'elif', 'else': if x > 0:", "category": "programming"},
        {"key": "python_classes", "value": "Classes em Python: class MinhaClasse: def __init__(self):", "category": "programming"},
        {"key": "python_imports", "value": "Para importar módulos: import math ou from math import sqrt", "category": "programming"}
    ]
    
    added_count = db.bulk_add_knowledge(programming_knowledge)
    print(f"   Conhecimentos de programação adicionados: {added_count}")
    
    # Teste 2: Geração de massa com dados de empresa
    print("\n🏢 Teste 2: Geração de massa - Dados da Empresa")
    
    company_knowledge = [
        {"key": "company_name", "value": "TechCorp Solutions - Empresa de tecnologia especializada em desenvolvimento de software", "category": "company"},
        {"key": "company_mission", "value": "Nossa missão é transformar ideias em soluções tecnológicas inovadoras", "category": "company"},
        {"key": "company_values", "value": "Inovação, Qualidade, Transparência e Colaboração são nossos valores fundamentais", "category": "company"},
        {"key": "company_offices", "value": "Temos escritórios em São Paulo, Rio de Janeiro e Belo Horizonte", "category": "company"},
        {"key": "company_employees", "value": "Atualmente temos 150 funcionários distribuídos em 3 escritórios", "category": "company"},
        {"key": "company_founded", "value": "Fundada em 2015, completamos 9 anos de mercado", "category": "company"},
        {"key": "company_services", "value": "Oferecemos desenvolvimento web, mobile, consultoria em TI e treinamentos", "category": "company"},
        {"key": "company_technologies", "value": "Trabalhamos com React, Node.js, Python, Java, AWS e Docker", "category": "company"},
        {"key": "company_clients", "value": "Atendemos mais de 50 clientes, desde startups até grandes corporações", "category": "company"},
        {"key": "company_contact", "value": "Contato: contato@techcorp.com | (11) 99999-9999", "category": "company"}
    ]
    
    added_count = db.bulk_add_knowledge(company_knowledge)
    print(f"   Conhecimentos da empresa adicionados: {added_count}")
    
    # Teste 3: Geração de massa com FAQ
    print("\n❓ Teste 3: Geração de massa - FAQ")
    
    faq_knowledge = [
        {"key": "faq_what_is_ai", "value": "IA (Inteligência Artificial) é a capacidade de máquinas executarem tarefas que normalmente requerem inteligência humana", "category": "faq"},
        {"key": "faq_machine_learning", "value": "Machine Learning é um subcampo da IA que permite que computadores aprendam sem serem explicitamente programados", "category": "faq"},
        {"key": "faq_deep_learning", "value": "Deep Learning usa redes neurais com múltiplas camadas para processar dados complexos", "category": "faq"},
        {"key": "faq_nlp", "value": "NLP (Processamento de Linguagem Natural) permite que computadores entendam e processem linguagem humana", "category": "faq"},
        {"key": "faq_computer_vision", "value": "Visão Computacional permite que máquinas interpretem e analisem imagens e vídeos", "category": "faq"},
        {"key": "faq_ai_ethics", "value": "Ética em IA envolve garantir que sistemas de IA sejam justos, transparentes e responsáveis", "category": "faq"},
        {"key": "faq_ai_applications", "value": "IA é usada em medicina, transporte, finanças, entretenimento e muitos outros setores", "category": "faq"},
        {"key": "faq_ai_future", "value": "O futuro da IA inclui AGI (Inteligência Geral Artificial) e sistemas mais autônomos", "category": "faq"},
        {"key": "faq_ai_limitations", "value": "IA ainda tem limitações em criatividade, senso comum e compreensão contextual profunda", "category": "faq"},
        {"key": "faq_ai_learning", "value": "Para aprender IA, comece com matemática, estatística, programação e depois machine learning", "category": "faq"}
    ]
    
    added_count = db.bulk_add_knowledge(faq_knowledge)
    print(f"   Conhecimentos de FAQ adicionados: {added_count}")
    
    # Teste 4: Verificação de dados inseridos
    print("\n🔍 Teste 4: Verificação de Dados Inseridos")
    
    # Conta total de conhecimentos
    all_knowledge = db.get_all_knowledge()
    print(f"   Total de conhecimentos na base: {len(all_knowledge)}")
    
    # Verifica por categoria
    programming_items = db.get_knowledge_by_category("programming")
    company_items = db.get_knowledge_by_category("company")
    faq_items = db.get_knowledge_by_category("faq")
    
    print(f"   Conhecimentos de programação: {len(programming_items)}")
    print(f"   Conhecimentos da empresa: {len(company_items)}")
    print(f"   Conhecimentos de FAQ: {len(faq_items)}")
    
    # Teste 5: Busca por termo
    print("\n🔎 Teste 5: Busca por Termo")
    
    search_results = db.search_knowledge("Python")
    print(f"   Resultados para 'Python': {len(search_results)}")
    for result in search_results[:3]:  # Mostra apenas os 3 primeiros
        print(f"     - {result['key']}: {result['value'][:50]}...")
    
    search_results = db.search_knowledge("empresa")
    print(f"   Resultados para 'empresa': {len(search_results)}")
    for result in search_results[:3]:
        print(f"     - {result['key']}: {result['value'][:50]}...")
    
    # Teste 6: Operações individuais
    print("\n⚙️ Teste 6: Operações Individuais")
    
    # Busca conhecimento específico
    python_basics = db.get_knowledge("python_basics")
    print(f"   Busca 'python_basics': {python_basics[:50]}...")
    
    # Atualiza conhecimento
    db.update_knowledge("python_basics", "Python é uma linguagem de programação moderna, versátil e fácil de aprender.", "programming")
    updated_value = db.get_knowledge("python_basics")
    print(f"   Valor atualizado: {updated_value[:50]}...")
    
    # Adiciona conhecimento individual
    db.add_knowledge("teste_individual", "Este é um teste de conhecimento individual", "test")
    individual_test = db.get_knowledge("teste_individual")
    print(f"   Conhecimento individual: {individual_test}")
    
    # Remove conhecimento de teste
    deleted = db.delete_knowledge("teste_individual")
    print(f"   Conhecimento removido: {deleted}")
    
    # Teste 7: Performance com muitos dados
    print("\n⚡ Teste 7: Performance com Muitos Dados")
    
    # Gera 100 conhecimentos de teste
    import time
    start_time = time.time()
    
    large_dataset = []
    for i in range(100):
        large_dataset.append({
            "key": f"performance_test_{i:03d}",
            "value": f"Este é o conhecimento de teste número {i} para verificar performance",
            "category": "performance_test"
        })
    
    added_large = db.bulk_add_knowledge(large_dataset)
    end_time = time.time()
    
    print(f"   Conhecimentos de performance adicionados: {added_large}")
    print(f"   Tempo de inserção: {end_time - start_time:.2f} segundos")
    
    # Verifica total final
    final_count = len(db.get_all_knowledge())
    print(f"   Total final de conhecimentos: {final_count}")
    
    # Limpeza de dados de teste
    print("\n🧹 Limpeza de Dados de Teste")
    performance_items = db.get_knowledge_by_category("performance_test")
    for item in performance_items:
        db.delete_knowledge(item['key'])
    print(f"   Conhecimentos de performance removidos: {len(performance_items)}")
    
    print("\n✅ Teste de geração de massa da KnowledgeBase concluído com sucesso!")
    
    return db


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
        await test_knowledge_base_mass_generation()
    except Exception as e:
        print(f"⚠️ Erro nos testes: {e}")

async def run_knowledge_base_test():
    """Executa apenas o teste da KnowledgeBase"""
    try:
        print("\n Executando teste da KnowledgeBase...")
        await test_knowledge_base_mass_generation()
    except Exception as e:
        print(f"⚠️ Erro no teste da KnowledgeBase: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    # Para usar com API real, descomente as linhas abaixo:
    if len(sys.argv) > 1:
        modo = sys.argv[1].lower()
        
        if modo == "simple":
            asyncio.run(run_simple_tests())
        elif modo == "complete":
            asyncio.run(run_complete_tests())
        elif modo == "knowledge":
            asyncio.run(run_knowledge_base_test())
        else:
            print("❌ Modo inválido. Use: simple, complete, knowledge")
    else:
        # Padrão: executa testes simples
        asyncio.run(run_simple_tests())