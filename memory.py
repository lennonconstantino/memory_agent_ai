from collections import deque
from datetime import datetime
import json
from typing import Dict, List, Any
import openai
from dotenv import load_dotenv

from database_models import DatabaseManager, UserProfile, Message, ConversationSummary
from prompt import get_create_system_message, get_extract_system_message

_ = load_dotenv()  # força a execução


class SQLAlchemyMemoryAgent:
    """Sistema de memória usando SQLAlchemy para persistência"""
    
    def __init__(self, model: str = "gpt-3.5-turbo", short_term_limit: int = 10, 
                 max_tokens: int = 4000, database_url: str = "sqlite:///ai_memory.db"):
        # Configuração OpenAI
        self.client = openai.OpenAI()
        self.model = model
        self.max_tokens = max_tokens
        
        # Gerenciador de banco de dados
        self.db = DatabaseManager(database_url)
        
        # Memória de Curto Prazo - Contexto atual da conversa (ainda em memória para performance)
        self.conversation_history = deque(maxlen=short_term_limit)
        
        # Configurações de consolidação
        self.consolidation_threshold = 5  # Número de mensagens para consolidar
        self.summary_trigger = 15  # Gatilho para criar resumo
        self.max_messages_per_user = 100  # Limite de mensagens por usuário no BD
    
    def add_message(self, user_id: str, role: str, content: str, metadata: Dict = None):
        """Adiciona uma mensagem à memória de curto prazo e ao banco"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
            "user_id": user_id,
            "metadata": metadata or {}
        }
        
        # Adiciona à memória de curto prazo
        self.conversation_history.append(message)
        
        # Persiste no banco de dados
        self.db.add_message(user_id, role, content, metadata)
        
        # Verifica se precisa consolidar conhecimento
        if len([msg for msg in self.conversation_history if msg["user_id"] == user_id]) >= self.consolidation_threshold:
            self._extract_and_consolidate_information(user_id)
        
        # Cria resumo se conversa ficar muito longa
        if self.db.get_message_count(user_id) >= self.summary_trigger:
            self._create_conversation_summary(user_id)
            
        # Limpa mensagens antigas se necessário
        if self.db.get_message_count(user_id) > self.max_messages_per_user:
            deleted = self.db.cleanup_old_messages(user_id, keep_last=self.max_messages_per_user // 2)
            print(f"🗑️ Removed {deleted} old messages for user {user_id}")

    def _extract_and_consolidate_information(self, user_id: str):
        """Extrai informações importantes da conversa e consolida no perfil do usuário"""
        # Pega as últimas mensagens para análise
        recent_messages = [msg for msg in list(self.conversation_history)[-5:] 
                          if msg["user_id"] == user_id]
        
        if not recent_messages:
            return
        
        # Cria prompt para extrair informações
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" for msg in recent_messages
        ])
        
        extraction_prompt = get_extract_system_message(conversation_text=conversation_text)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": extraction_prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            extracted_info = response.choices[0].message.content
            
            # Tenta fazer parse do JSON
            try:
                user_info = json.loads(extracted_info)
                # Remove campos vazios
                user_info = {k: v for k, v in user_info.items() if v}
                
                if user_info:  # Só atualiza se tiver informações
                    self.db.update_user_profile(user_id, user_info)
                    print(f"📝 User profile {user_id} updated: {user_info}")
                    
            except json.JSONDecodeError:
                print(f"❌ Error parsing extracted information: {extracted_info}")
                
        except Exception as e:
            print(f"❌ Error extracting information: {str(e)}")

    def _create_conversation_summary(self, user_id: str):
        """Cria resumo da conversa atual e limpa parte da memória de curto prazo"""
        # Busca mensagens recentes do usuário no banco
        recent_messages = self.db.get_recent_messages(user_id, limit=20)
        
        if len(recent_messages) < 3:
            return
        
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" for msg in recent_messages
        ])
        
        summary_prompt = get_create_system_message(conversation_text=conversation_text)

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": summary_prompt}],
                max_tokens=300,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content
            
            # Armazena o resumo no banco
            self.db.add_conversation_summary(user_id, summary, len(recent_messages))
            
            print(f"📄 Conversation summary created for user {user_id}")
            
            # Limpa parte da memória de curto prazo
            self._compress_short_term_memory(user_id)
            
        except Exception as e:
            print(f"❌ Error creating summary: {str(e)}")

    def _compress_short_term_memory(self, user_id: str):
        """Remove mensagens antigas da memória de curto prazo, mantendo as mais recentes"""
        # Mantém apenas as últimas 5 mensagens do usuário
        user_messages = [msg for msg in self.conversation_history 
                        if msg["user_id"] == user_id]
        
        if len(user_messages) > 5:
            # Remove mensagens mais antigas
            messages_to_keep = user_messages[-5:]
            
            # Reconstrói a fila mantendo apenas as mensagens recentes
            new_history = deque(maxlen=self.conversation_history.maxlen)
            for msg in self.conversation_history:
                if msg["user_id"] != user_id or msg in messages_to_keep:
                    new_history.append(msg)
            
            self.conversation_history = new_history

    def get_user_profile(self, user_id: str) -> Dict:
        """Retorna o perfil completo do usuário"""
        return self.db.get_user_profile_dict(user_id)
    
    def get_conversation_summaries(self, user_id: str, limit: int = 5) -> List[str]:
        """Retorna resumos de conversas do usuário"""
        return self.db.get_conversation_summaries(user_id, limit)
    
    def save_memory(self, filename: str = None):
        """Compatibilidade: dados já estão persistidos no banco"""
        print(f"💾 Memory is automatically saved in database")
        if filename:
            print(f"   Note: SQLAlchemy version doesn't use file '{filename}' - data is in database")
    
    def load_memory(self, filename: str = None):
        """Compatibilidade: dados são carregados automaticamente do banco"""
        print(f"📂 Memory loaded from database automatically")
        if filename:
            print(f"   Note: SQLAlchemy version doesn't load from file '{filename}' - data comes from database")


class TestSQLAlchemyMemoryAgent:
    """Versão de teste com SQLAlchemy"""
    
    def __init__(self, model: str = "gpt-3.5-turbo", short_term_limit: int = 10, 
                 max_tokens: int = 4000, database_url: str = "sqlite:///test_ai_memory.db"):
        self.model = model
        self.short_term_limit = short_term_limit
        self.max_tokens = max_tokens
        self.memory_agent = SQLAlchemyMemoryAgent(
            model=model, 
            short_term_limit=short_term_limit, 
            max_tokens=max_tokens,
            database_url=database_url
        )

    async def generate_response(self, user_id: str, user_message: str) -> str:
        """Gera resposta considerando toda a memória disponível"""
        # Adiciona mensagem do usuário à memória
        self.memory_agent.add_message(user_id, "user", user_message)
        
        # Constrói contexto completo
        context_messages = self._build_context_for_user(user_id)
        
        try:
            # Chama OpenAI com contexto completo
            response = self.memory_agent.client.chat.completions.create(
                model=self.model,
                messages=context_messages,
                max_tokens=self.max_tokens,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            # Adiciona resposta à memória
            self.memory_agent.add_message(user_id, "assistant", ai_response)
            
            return ai_response
            
        except Exception as e:
            error_msg = f"Erro ao gerar resposta: {str(e)}"
            print(error_msg)
            return "Desculpe, ocorreu um erro ao processar sua mensagem."

    def _build_context_for_user(self, user_id: str) -> List[Dict]:
        """Constrói contexto completo para o usuário incluindo dados do banco"""
        messages = []
        
        # Sistema prompt com perfil do usuário
        system_prompt = self._create_system_prompt(user_id)
        messages.append({"role": "system", "content": system_prompt})
        
        # Adiciona resumos de conversas anteriores
        summaries = self.memory_agent.get_conversation_summaries(user_id, limit=3)
        if summaries:
            combined_summary = "\n\n".join(summaries)
            messages.append({
                "role": "system", 
                "content": f"Resumos de conversas anteriores:\n{combined_summary}"
            })
        
        # Adiciona histórico recente da conversa (memória de curto prazo)
        for msg in self.memory_agent.conversation_history:
            if msg["user_id"] == user_id:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Se não tiver mensagens na memória de curto prazo, busca do banco
        user_messages_in_memory = [msg for msg in self.memory_agent.conversation_history 
                                  if msg["user_id"] == user_id]
        
        if len(user_messages_in_memory) < 2:
            recent_db_messages = self.memory_agent.db.get_recent_messages(user_id, limit=5)
            for msg in recent_db_messages:
                # Evita duplicar mensagens que já estão na memória
                if not any(m["content"] == msg["content"] and m["role"] == msg["role"] 
                          for m in messages):
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
        
        return messages
    
    def _create_system_prompt(self, user_id: str) -> str:
        """Cria prompt do sistema baseado no perfil do usuário"""
        base_prompt = """Você é um assistente IA inteligente que mantém contexto de conversas. 
        Seja helpful, preciso e mantenha consistência baseada no que você sabe sobre o usuário."""
        
        profile = self.memory_agent.get_user_profile(user_id)
        if profile:
            profile_info = f"""
            
PERFIL DO USUÁRIO:
- Nome: {profile.get('name', 'Não informado')}
- Interesses: {', '.join(profile.get('interests', []))}
- Preferências: {profile.get('preferences', 'Não definidas')}
- Contexto: {profile.get('context', 'Não disponível')}
- Última interação: {profile.get('last_interaction', 'Primeira vez')}
"""
            base_prompt += profile_info
        
        return base_prompt
    
    def get_user_profile(self, user_id: str) -> Dict:
        """Retorna perfil do usuário"""
        return self.memory_agent.get_user_profile(user_id)
    
    def save_memory(self, filename: str):
        """Salva memória (compatibilidade)"""
        self.memory_agent.save_memory(filename)
    
    def add_message(self, user_id: str, role: str, content: str, metadata: Dict = None):
        """Adiciona mensagem (para compatibilidade com testes antigos)"""
        self.memory_agent.add_message(user_id, role, content, metadata)


# Classes de compatibilidade com a versão original
class MemoryAgent(SQLAlchemyMemoryAgent):
    """Alias para compatibilidade"""
    pass


class TestMemoryAgent(TestSQLAlchemyMemoryAgent):
    """Alias para compatibilidade"""
    pass
