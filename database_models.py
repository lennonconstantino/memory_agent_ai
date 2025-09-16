from sqlalchemy import create_engine, Column, String, Text, DateTime, Integer, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Dict, List, Any
import json

Base = declarative_base()

class UserProfile(Base):
    """Tabela para armazenar perfis de usuários"""
    __tablename__ = 'user_profiles'
    
    id = Column(String, primary_key=True)  # user_id
    name = Column(String, nullable=True)
    interests = Column(Text, nullable=True)  # JSON string de lista
    preferences = Column(Text, nullable=True)
    context = Column(Text, nullable=True)
    first_interaction = Column(DateTime, default=datetime.now)
    last_interaction = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relacionamentos
    messages = relationship("Message", back_populates="user_profile", cascade="all, delete-orphan")
    summaries = relationship("ConversationSummary", back_populates="user_profile", cascade="all, delete-orphan")
    
    def get_interests_list(self) -> List[str]:
        """Retorna lista de interesses a partir do JSON"""
        if not self.interests:
            return []
        try:
            return json.loads(self.interests)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_interests_list(self, interests: List[str]):
        """Define lista de interesses como JSON"""
        self.interests = json.dumps(interests) if interests else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para compatibilidade"""
        return {
            "name": self.name or "",
            "interests": self.get_interests_list(),
            "preferences": self.preferences or "",
            "context": self.context or "",
            "first_interaction": self.first_interaction,
            "last_interaction": self.last_interaction
        }


class Message(Base):
    """Tabela para armazenar mensagens do histórico"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user_profiles.id'), nullable=False)
    role = Column(String, nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    message_metadata = Column(Text, nullable=True)  # JSON string
    
    # Relacionamentos
    user_profile = relationship("UserProfile", back_populates="messages")
    
    def get_metadata_dict(self) -> Dict[str, Any]:
        """Retorna metadata como dicionário"""
        if not self.message_metadata:
            return {}
        try:
            return json.loads(self.message_metadata)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def set_metadata_dict(self, metadata: Dict[str, Any]):
        """Define metadata como JSON"""
        self.message_metadata = json.dumps(metadata) if metadata else None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário para compatibilidade"""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
            "metadata": self.get_metadata_dict()
        }


class ConversationSummary(Base):
    """Tabela para armazenar resumos de conversas"""
    __tablename__ = 'conversation_summaries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user_profiles.id'), nullable=False)
    summary = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    message_count = Column(Integer, default=0)  # Número de mensagens resumidas
    
    # Relacionamentos
    user_profile = relationship("UserProfile", back_populates="summaries")


class KnowledgeBase(Base):
    """Tabela para base de conhecimento geral"""
    __tablename__ = 'knowledge_base'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(Text, nullable=False)
    category = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class DatabaseManager:
    """Gerenciador de conexão e operações com banco de dados"""
    
    def __init__(self, database_url: str = "sqlite:///ai_memory.db"):
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
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
