from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from typing import Dict, List, Any
import json

from db import DatabaseConfig
from models import Base, ConversationSummary, Message, UserProfile, KnowledgeBase

class MemoryRepository:
    """Gerenciador de conexão e operações com banco de dados"""
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = create_engine(
            config.connection_string,
            echo=False,  # Mude para True para ver as queries SQL
            pool_pre_ping=True if config.database_type == "postgresql" else False
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.create_tables()
    
    def create_tables(self):
        """Cria todas as tabelas"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Retorna nova sessão de banco de dados"""
        return self.SessionLocal()
    
    def get_or_create_user_profile(self, user_id: str) -> UserProfile:
        """Obtém ou cria um perfil de usuário"""
        with self.get_session() as session:
            profile = session.query(UserProfile).filter(UserProfile.id == user_id).first()
            
            if not profile:
                profile = UserProfile(
                    id=user_id,
                    name="",
                    interests=json.dumps([]),
                    preferences="",
                    context="",
                    first_interaction=datetime.now(),
                    last_interaction=datetime.now()
                )
                session.add(profile)
                session.commit()
                session.refresh(profile)
            
            return profile
    
    def update_user_profile(self, user_id: str, updates: Dict[str, Any]):
        """Atualiza perfil do usuário"""
        with self.get_session() as session:
            profile = session.query(UserProfile).filter(UserProfile.id == user_id).first()
            
            if not profile:
                profile = self.get_or_create_user_profile(user_id)
                session = self.get_session()
                profile = session.query(UserProfile).filter(UserProfile.id == user_id).first()
            
            # Atualiza campos com tratamento de tipos
            for key, value in updates.items():
                if not value:  # Ignora valores vazios
                    continue
                    
                if key == "interests":
                    # Trata interesses como lista
                    if isinstance(value, list):
                        # Mescla interesses existentes com novos
                        existing_interests = set(profile.get_interests_list())
                        new_interests = set(value)
                        merged_interests = list(existing_interests.union(new_interests))
                        profile.set_interests_list(merged_interests)
                    elif isinstance(value, str):
                        # Se for string, tenta fazer parse JSON ou adiciona como único interesse
                        try:
                            interest_list = json.loads(value)
                            if isinstance(interest_list, list):
                                existing_interests = set(profile.get_interests_list())
                                new_interests = set(interest_list)
                                merged_interests = list(existing_interests.union(new_interests))
                                profile.set_interests_list(merged_interests)
                        except (json.JSONDecodeError, TypeError):
                            # Adiciona como interesse único
                            existing_interests = set(profile.get_interests_list())
                            existing_interests.add(value)
                            profile.set_interests_list(list(existing_interests))
                            
                elif key == "preferences":
                    # Trata preferências como string
                    if isinstance(value, list):
                        # Se for lista, junta em string
                        profile.preferences = ", ".join(str(v) for v in value if v)
                    elif isinstance(value, str):
                        profile.preferences = value
                        
                elif key in ["name", "context"]:
                    # Campos de texto simples
                    if isinstance(value, list):
                        # Se for lista, junta em string
                        setattr(profile, key, ", ".join(str(v) for v in value if v))
                    elif isinstance(value, str):
                        setattr(profile, key, value)
                        
                elif hasattr(profile, key) and isinstance(value, str):
                    # Outros campos que devem ser strings
                    setattr(profile, key, value)
            
            profile.last_interaction = datetime.now()
            session.commit()
    
    def add_message(self, user_id: str, role: str, content: str, metadata: Dict[str, Any] = None):
        """Adiciona mensagem ao histórico"""
        with self.get_session() as session:
            # Garante que o perfil existe
            self.get_or_create_user_profile(user_id)
            
            message = Message(
                user_id=user_id,
                role=role,
                content=content,
                timestamp=datetime.now()
            )
            
            if metadata:
                message.set_metadata_dict(metadata)
            
            session.add(message)
            session.commit()
    
    def get_recent_messages(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtém mensagens recentes do usuário"""
        with self.get_session() as session:
            messages = session.query(Message)\
                             .filter(Message.user_id == user_id)\
                             .order_by(Message.timestamp.desc())\
                             .limit(limit)\
                             .all()
            
            return [msg.to_dict() for msg in reversed(messages)]
    
    def add_conversation_summary(self, user_id: str, summary: str, message_count: int = 0):
        """Adiciona resumo de conversa"""
        with self.get_session() as session:
            # Garante que o perfil existe
            self.get_or_create_user_profile(user_id)
            
            summary_obj = ConversationSummary(
                user_id=user_id,
                summary=summary,
                message_count=message_count
            )
            
            session.add(summary_obj)
            session.commit()
    
    def get_conversation_summaries(self, user_id: str, limit: int = 5) -> List[str]:
        """Obtém resumos de conversas do usuário"""
        with self.get_session() as session:
            summaries = session.query(ConversationSummary)\
                              .filter(ConversationSummary.user_id == user_id)\
                              .order_by(ConversationSummary.created_at.desc())\
                              .limit(limit)\
                              .all()
            
            return [summary.summary for summary in summaries]
    
    def get_user_profile_dict(self, user_id: str) -> Dict[str, Any]:
        """Retorna perfil do usuário como dicionário"""
        with self.get_session() as session:
            profile = session.query(UserProfile).filter(UserProfile.id == user_id).first()
            
            if not profile:
                return {}
            
            return profile.to_dict()
    
    def cleanup_old_messages(self, user_id: str, keep_last: int = 50):
        """Remove mensagens antigas, mantendo apenas as mais recentes"""
        with self.get_session() as session:
            # Obtém IDs das mensagens mais recentes para manter
            recent_message_ids = session.query(Message.id)\
                                       .filter(Message.user_id == user_id)\
                                       .order_by(Message.timestamp.desc())\
                                       .limit(keep_last)\
                                       .scalar_subquery()
            
            # Remove mensagens antigas
            deleted = session.query(Message)\
                            .filter(Message.user_id == user_id)\
                            .filter(~Message.id.in_(recent_message_ids))\
                            .delete(synchronize_session=False)
            
            session.commit()
            return deleted
    
    def get_message_count(self, user_id: str) -> int:
        """Retorna número total de mensagens do usuário"""
        with self.get_session() as session:
            return session.query(Message).filter(Message.user_id == user_id).count()
    
    # ========== MÉTODOS PARA KNOWLEDGE BASE ==========
    
    def add_knowledge(self, key: str, value: str, category: str = None):
        """Adiciona conhecimento à base geral"""
        with self.get_session() as session:
            # Verifica se já existe
            existing = session.query(KnowledgeBase).filter(KnowledgeBase.key == key).first()
            if existing:
                # Atualiza se já existe
                existing.value = value
                existing.category = category
                existing.updated_at = datetime.now()
            else:
                # Cria novo
                knowledge = KnowledgeBase(
                    key=key,
                    value=value,
                    category=category
                )
                session.add(knowledge)
            session.commit()
    
    def get_knowledge(self, key: str) -> str:
        """Busca conhecimento por chave"""
        with self.get_session() as session:
            kb = session.query(KnowledgeBase).filter(KnowledgeBase.key == key).first()
            return kb.value if kb else None
    
    def get_knowledge_by_category(self, category: str) -> List[Dict]:
        """Busca conhecimento por categoria"""
        with self.get_session() as session:
            kb_items = session.query(KnowledgeBase)\
                             .filter(KnowledgeBase.category == category)\
                             .all()
            return [{"key": item.key, "value": item.value, "created_at": item.created_at} for item in kb_items]
    
    def update_knowledge(self, key: str, value: str, category: str = None):
        """Atualiza conhecimento existente"""
        with self.get_session() as session:
            kb = session.query(KnowledgeBase).filter(KnowledgeBase.key == key).first()
            if kb:
                kb.value = value
                if category:
                    kb.category = category
                kb.updated_at = datetime.now()
                session.commit()
                return True
            return False
    
    def delete_knowledge(self, key: str) -> bool:
        """Remove conhecimento da base"""
        with self.get_session() as session:
            kb = session.query(KnowledgeBase).filter(KnowledgeBase.key == key).first()
            if kb:
                session.delete(kb)
                session.commit()
                return True
            return False
    
    def get_all_knowledge(self) -> List[Dict]:
        """Retorna todo o conhecimento da base"""
        with self.get_session() as session:
            kb_items = session.query(KnowledgeBase).all()
            return [{"key": item.key, "value": item.value, "category": item.category, 
                    "created_at": item.created_at, "updated_at": item.updated_at} for item in kb_items]
    
    def search_knowledge(self, search_term: str) -> List[Dict]:
        """Busca conhecimento por termo (busca em key, value e category)"""
        with self.get_session() as session:
            kb_items = session.query(KnowledgeBase)\
                             .filter(
                                 (KnowledgeBase.key.contains(search_term)) |
                                 (KnowledgeBase.value.contains(search_term)) |
                                 (KnowledgeBase.category.contains(search_term))
                             ).all()
            return [{"key": item.key, "value": item.value, "category": item.category} for item in kb_items]
    
    def bulk_add_knowledge(self, knowledge_items: List[Dict]) -> int:
        """Adiciona múltiplos conhecimentos de uma vez"""
        added_count = 0
        with self.get_session() as session:
            for item in knowledge_items:
                key = item.get('key')
                value = item.get('value')
                category = item.get('category')
                
                if not key or not value:
                    continue
                
                # Verifica se já existe
                existing = session.query(KnowledgeBase).filter(KnowledgeBase.key == key).first()
                if not existing:
                    knowledge = KnowledgeBase(
                        key=key,
                        value=value,
                        category=category
                    )
                    session.add(knowledge)
                    added_count += 1
                else:
                    # Atualiza existente
                    existing.value = value
                    if category:
                        existing.category = category
                    existing.updated_at = datetime.now()
            
            session.commit()
        return added_count
