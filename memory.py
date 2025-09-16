
from collections import deque
from datetime import datetime
import json
import pickle
from typing import Dict, List

import openai

from dotenv import load_dotenv
_ = load_dotenv() # forcar a execucao

from prompt import get_create_system_message, get_extract_system_message

class MemoryAgent:
    def __init__(self, model: str = "gpt-3.5-turbo", short_term_limit: int = 10, max_tokens: int = 4000):
        # Configuração OpenAI
        self.client = openai.OpenAI()
        self.model = model
        self.max_tokens = max_tokens

        # Memória de Curto Prazo - Contexto atual da conversa
        self.conversation_history = deque(maxlen=short_term_limit)

        # Memória de Longo Prazo - Informações persistentes
        self.user_profiles = {}  # Perfis dos usuários
        self.knowledge_base = {}  # Base de conhecimento geral
        self.conversation_summaries = {}  # Resumos de conversas anteriores
        
        # Configurações de consolidação
        self.consolidation_threshold = 5  # Número de mensagens para consolidar
        self.summary_trigger = 15  # Gatilho para criar resumo

    def add_message(self, user_id: str, role: str, content: str, metadata: Dict = None):
        """
        Adds a message to short-term memory
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
            "user_id": user_id,
            "metadata": metadata or {}
        }
        
        self.conversation_history.append(message)
        
        # Verifica se precisa consolidar conhecimento
        if len(self.conversation_history) >= self.consolidation_threshold:
            self._extract_and_consolidate_information(user_id)
        
        # Cria resumo se conversa ficar muito longa
        if len(self.conversation_history) >= self.summary_trigger:
            self._create_conversation_summary(user_id)

    def _update_user_profile(self, user_id: str, new_info: Dict):
        """
        Updates the user profile with new information
        """
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "name": "",
                "interests": [],
                "preferences": "",
                "context": "",
                "first_interaction": datetime.now(),
                "last_interaction": datetime.now()
            }
        
        profile = self.user_profiles[user_id]
        
        # Atualiza campos não vazios
        for key, value in new_info.items():
            if value and key in profile:
                if key == "interests" and isinstance(value, list):
                    # Adiciona novos interesses sem duplicar
                    existing_interests = set(profile["interests"])
                    new_interests = set(value)
                    profile["interests"] = list(existing_interests.union(new_interests))
                else:
                    profile[key] = value
        
        profile["last_interaction"] = datetime.now()
        
        print(f" User profile {user_id} updated: {new_info}")

    def _extract_and_consolidate_information(self, user_id: str):
        """
        Extracts important information from the conversation and consolidates it into the user profile
        """
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
                self._update_user_profile(user_id, user_info)
            except json.JSONDecodeError:
                print(f"Error parsing extracted information: {extracted_info}")
                
        except Exception as e:
            print(f"Error extracting information: {str(e)}")

    def _compress_short_term_memory(self, user_id: str):
        """
        Removes old messages from short-term memory, keeping the most recent ones
        """
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

    def _create_conversation_summary(self, user_id: str):
        """
        Creates summary of current conversation and clears short-term memory
        """
        user_messages = [msg for msg in self.conversation_history 
                        if msg["user_id"] == user_id]
        
        if len(user_messages) < 3:
            return
        
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" for msg in user_messages
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
            
            # Armazena o resumo
            if user_id not in self.conversation_summaries:
                self.conversation_summaries[user_id] = []
            
            self.conversation_summaries[user_id] = summary
            
            print(f"Conversation summary created for user {user_id}")
            
            # Limpa parte da memória de curto prazo
            self._compress_short_term_memory(user_id)
            
        except Exception as e:
            print(f"Error creating summary: {str(e)}")


    def get_user_profile(self, user_id: str) -> Dict:
        """
        Returns the user's full profile
        """
        return self.user_profiles.get(user_id, {})
    
    def save_memory(self, filename: str):
        """
        Saves all long-term memory
        """
        memory_data = {
            "user_profiles": self.user_profiles,
            "knowledge_base": self.knowledge_base,
            "conversation_summaries": self.conversation_summaries,
            "saved_at": datetime.now()
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(memory_data, f)
        
        print(f" Memory saved in {filename}")

    def load_memory(self, filename: str = "ai_agent_memory.pkl"):
        """
        Loads saved long-term memory
        """
        try:
            with open(filename, 'rb') as f:
                memory_data = pickle.load(f)
            
            self.user_profiles = memory_data.get("user_profiles", {})
            self.knowledge_base = memory_data.get("knowledge_base", {})
            self.conversation_summaries = memory_data.get("conversation_summaries", {})
            
            print(f" Memory loaded from {filename}")
            print(f"   - {len(self.user_profiles)} user profiles")
            print(f"   - {len(self.conversation_summaries)} conversation summaries")
            
        except FileNotFoundError:
            print(f" File {filename} not found")
        except Exception as e:
            print(f" Error loading memory: {str(e)}")


class TestMemoryAgent:
    def __init__(self, model: str = "gpt-3.5-turbo", short_term_limit: int = 10, max_tokens: int = 4000):
        self.model = model
        self.short_term_limit = short_term_limit
        self.max_tokens = max_tokens
        self.memory_agent = MemoryAgent(model=model, short_term_limit=short_term_limit, max_tokens=max_tokens)
        

    async def generate_response(self, user_id: str, user_message: str) -> str:
        """
        Gera resposta considerando toda a memória disponível
        """
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
        """
        Constrói contexto completo para o usuário incluindo:
        - Perfil do usuário
        - Resumos de conversas anteriores
        - Histórico recente
        """
        messages = []
        
        # Sistema prompt com perfil do usuário
        system_prompt = self._create_system_prompt(user_id)
        messages.append({"role": "system", "content": system_prompt})
        
        # Adiciona resumo de conversas anteriores se existir
        if user_id in self.memory_agent.conversation_summaries:
            summary = self.memory_agent.conversation_summaries[user_id]
            messages.append({
                "role": "system", 
                "content": f"Resumo de conversas anteriores: {summary}"
            })
        
        # Adiciona histórico recente da conversa
        for msg in self.memory_agent.conversation_history:
            if msg["user_id"] == user_id:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        return messages
    
    def _create_system_prompt(self, user_id: str) -> str:
        """
        Cria prompt do sistema baseado no perfil do usuário
        """
        base_prompt = """Você é um assistente IA inteligente que mantém contexto de conversas. 
        Seja helpful, preciso e mantenha consistência baseada no que você sabe sobre o usuário."""
        
        if user_id in self.memory_agent.user_profiles:
            profile = self.memory_agent.user_profiles[user_id]
            profile_info = f"""
            
PERFIL DO USUÁRIO:
- Nome: {profile.get('nome', 'Não informado')}
- Interesses: {', '.join(profile.get('interesses', []))}
- Preferências: {profile.get('preferencias', 'Não definidas')}
- Contexto: {profile.get('contexto', 'Não disponível')}
- Última interação: {profile.get('ultima_interacao', 'Primeira vez')}
"""
            base_prompt += profile_info
        
        return base_prompt
    
    def get_user_profile(self, user_id: str) -> Dict:
        return self.memory_agent.get_user_profile(user_id=user_id)
    
    def save_memory(self, filename: str):
        self.memory_agent.save_memory(filename=filename)
