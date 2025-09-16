from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict, List, Any
import json

from db import Base

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
