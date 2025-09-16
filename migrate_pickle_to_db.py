"""
Script de migração para converter dados do formato pickle para SQLAlchemy
"""
import pickle
import json
from datetime import datetime
from database_models import DatabaseManager
from typing import Dict, Any

def migrate_pickle_to_sqlite(pickle_file: str, database_url: str = "sqlite:///migrated_memory.db"):
    """
    Migra dados de um arquivo pickle para banco SQLite
    """
    print(f"🔄 Iniciando migração de {pickle_file} para {database_url}")
    
    try:
        # Carrega dados do pickle
        with open(pickle_file, 'rb') as f:
            memory_data = pickle.load(f)
        
        print(f"📂 Dados carregados do pickle:")
        print(f"   - Perfis de usuário: {len(memory_data.get('user_profiles', {}))}")
        print(f"   - Resumos de conversa: {len(memory_data.get('conversation_summaries', {}))}")
        print(f"   - Base de conhecimento: {len(memory_data.get('knowledge_base', {}))}")
        
        # Inicializa banco de dados
        db = DatabaseManager(database_url)
        
        # Migra perfis de usuário
        migrated_profiles = 0
        user_profiles = memory_data.get('user_profiles', {})
        
        for user_id, profile_data in user_profiles.items():
            try:
                # Cria ou atualiza perfil
                db.get_or_create_user_profile(user_id)
                
                # Prepara dados para atualização
                update_data = {}
                
                if profile_data.get('name'):
                    update_data['name'] = profile_data['name']
                
                if profile_data.get('interests'):
                    interests = profile_data['interests']
                    if isinstance(interests, list):
                        update_data['interests'] = interests
                    elif isinstance(interests, str):
                        # Se for string, tenta fazer parse como JSON
                        try:
                            update_data['interests'] = json.loads(interests)
                        except:
                            update_data['interests'] = [interests]
                
                if profile_data.get('preferences'):
                    update_data['preferences'] = profile_data['preferences']
                    
                if profile_data.get('context'):
                    update_data['context'] = profile_data['context']
                
                # Atualiza perfil se tiver dados
                if update_data:
                    db.update_user_profile(user_id, update_data)
                    migrated_profiles += 1
                    print(f"   ✅ Perfil migrado: {user_id}")
                
            except Exception as e:
                print(f"   ❌ Erro ao migrar perfil {user_id}: {e}")
        
        # Migra resumos de conversa
        migrated_summaries = 0
        conversation_summaries = memory_data.get('conversation_summaries', {})
        
        for user_id, summaries in conversation_summaries.items():
            try:
                # Garante que o perfil existe
                db.get_or_create_user_profile(user_id)
                
                if isinstance(summaries, list):
                    for summary in summaries:
                        db.add_conversation_summary(user_id, summary)
                        migrated_summaries += 1
                elif isinstance(summaries, str):
                    db.add_conversation_summary(user_id, summaries)
                    migrated_summaries += 1
                    
                print(f"   ✅ Resumos migrados para {user_id}")
                    
            except Exception as e:
                print(f"   ❌ Erro ao migrar resumos para {user_id}: {e}")
        
        print(f"\n🎉 Migração concluída com sucesso!")
        print(f"   - Perfis migrados: {migrated_profiles}")
        print(f"   - Resumos migrados: {migrated_summaries}")
        print(f"   - Banco de dados: {database_url}")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Arquivo pickle não encontrado: {pickle_file}")
        return False
    except Exception as e:
        print(f"❌ Erro durante migração: {e}")
        return False


def verify_migration(database_url: str = "sqlite:///migrated_memory.db"):
    """
    Verifica se a migração foi bem-sucedida
    """
    print(f"\n🔍 Verificando migração em {database_url}")
    
    db = DatabaseManager(database_url)
    
    try:
        with db.get_session() as session:
            from database_models import UserProfile, ConversationSummary, Message
            
            # Conta registros
            profile_count = session.query(UserProfile).count()
            summary_count = session.query(ConversationSummary).count()
            message_count = session.query(Message).count()
            
            print(f"📊 Dados no banco:")
            print(f"   - Perfis de usuário: {profile_count}")
            print(f"   - Resumos de conversa: {summary_count}")
            print(f"   - Mensagens: {message_count}")
            
            # Mostra alguns exemplos
            if profile_count > 0:
                print(f"\n👥 Exemplos de perfis migrados:")
                profiles = session.query(UserProfile).limit(3).all()
                for profile in profiles:
                    print(f"   - {profile.id}: {profile.name or 'Sem nome'}")
                    interests = profile.get_interests_list()
                    if interests:
                        print(f"     Interesses: {interests}")
            
            return True
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
        return False


def create_sample_pickle_data(filename: str = "sample_data.pkl"):
    """
    Cria dados de exemplo no formato pickle para testar a migração
    """
    print(f"📝 Criando dados de exemplo em {filename}")
    
    sample_data = {
        "user_profiles": {
            "user_001": {
                "name": "João Silva",
                "interests": ["programação", "games", "tecnologia"],
                "preferences": "Prefere respostas técnicas detalhadas",
                "context": "Desenvolvedor Python sênior",
                "first_interaction": datetime.now(),
                "last_interaction": datetime.now()
            },
            "user_002": {
                "name": "Maria Santos",
                "interests": ["fotografia", "viagem", "arte"],
                "preferences": "Gosta de conversas criativas",
                "context": "Fotógrafa profissional",
                "first_interaction": datetime.now(),
                "last_interaction": datetime.now()
            }
        },
        "conversation_summaries": {
            "user_001": [
                "João demonstrou interesse em arquiteturas de software e microservices.",
                "Discussão sobre boas práticas de desenvolvimento Python e testes automatizados."
            ],
            "user_002": [
                "Maria compartilhou experiências sobre fotografia de paisagens.",
                "Conversa sobre equipamentos fotográficos e técnicas de composição."
            ]
        },
        "knowledge_base": {
            "python_frameworks": "Django, Flask, FastAPI são os principais frameworks web Python",
            "photography_tips": "Regra dos terços, golden hour e composição são fundamentais"
        },
        "saved_at": datetime.now()
    }
    
    with open(filename, 'wb') as f:
        pickle.dump(sample_data, f)
    
    print(f"✅ Dados de exemplo criados em {filename}")
    return filename


def main():
    """
    Função principal para testar a migração
    """
    print("🚀 SCRIPT DE MIGRAÇÃO PICKLE -> SQLALCHEMY\n")
    
    # Opção 1: Criar dados de exemplo e testar migração
    print("1️⃣ Criando dados de exemplo...")
    sample_file = create_sample_pickle_data()
    
    print("\n2️⃣ Executando migração...")
    success = migrate_pickle_to_sqlite(sample_file, "sqlite:///test_migration.db")
    
    if success:
        print("\n3️⃣ Verificando migração...")
        verify_migration("sqlite:///test_migration.db")
    
    # Opção 2: Migrar arquivo real (descomente se tiver um arquivo real)
    # print("\n4️⃣ Migrando arquivo real...")
    # real_file = "ai_agent_memory.pkl"  # ou o nome do seu arquivo
    # migrate_pickle_to_sqlite(real_file, "sqlite:///real_migration.db")
    # verify_migration("sqlite:///real_migration.db")
    
    print(f"\n🎯 Uso do script:")
    print(f"   python migrate_pickle_to_db.py")
    print(f"   # Para migrar arquivo específico:")
    print(f"   # migrate_pickle_to_sqlite('meu_arquivo.pkl', 'sqlite:///meu_banco.db')")


if __name__ == "__main__":
    main()
