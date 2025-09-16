
import json
import os
from dotenv import load_dotenv

from memory import TestMemoryAgent
_ = load_dotenv() # forcar a execucao

# Exemplo de uso prático
async def exemplo_chatbot_com_memoria():
    """
    Demonstração prática de um chatbot com sistema de memória
    """
    # IMPORTANTE: Substitua pela sua API key real
    #API_KEY = os.getenv("OPENAI_API_KEY")
    
    print("=== CHATBOT COM SISTEMA DE MEMÓRIA ===\n")
    
    # Inicializa o sistema de memória
    memory_system = TestMemoryAgent(
        #openai_api_key=API_KEY,
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
    
    # Salva a memória
    memory_system.save_memory("teste.pkl")
    
    return memory_system

# Versão síncrona para teste sem async
class SimpleChatbot:
    """
    Versão simplificada para demonstração sem async
    """
    def __init__(self, api_key: str):
        self.memory = TestMemoryAgent(api_key)
    
    def chat(self, user_id: str, message: str) -> str:
        """Versão síncrona do chat"""
        # Simula uma resposta baseada na memória
        self.memory.add_message(user_id, "user", message)
        
        # Resposta simulada (substitua pela chamada real da OpenAI)
        if "nome" in message.lower() and "maria" in message.lower():
            response = "Prazer em conhecê-la, Maria! Vou lembrar que você gosta de fotografia."
        elif "câmera" in message.lower():
            response = "Para iniciantes em fotografia, recomendo câmeras como Canon EOS Rebel ou Nikon D3500."
        elif "hobby" in message.lower():
            profile = self.memory.get_user_profile(user_id)
            interests = profile.get("interesses", ["fotografia"])
            response = f"Você mencionou que gosta de {', '.join(interests)}!"
        else:
            response = "Posso ajudá-la com algo relacionado à fotografia ou outros assuntos!"
        
        self.memory.add_message(user_id, "assistant", response)
        return response

def exemplo_simples():
    """
    Exemplo sem necessidade de API key real
    """
    print("=== EXEMPLO SIMPLIFICADO (SEM API) ===\n")
    
    chatbot = SimpleChatbot("fake-api-key")
    user_id = "user_456"
    
    # Simulação de conversa
    messages = [
        "Oi! Eu sou a Maria e adoro fotografia!",
        "Pode me recomendar uma câmera boa?",
        "Qual é mesmo o meu hobby favorito?",
    ]
    
    for msg in messages:
        print(f"👤 Usuário: {msg}")
        response = chatbot.chat(user_id, msg)
        print(f"🤖 Chatbot: {response}\n")
    
    # Mostra perfil
    profile = chatbot.memory.get_user_profile(user_id)
    print(f"📋 Perfil: {profile}")

# Executa a demonstração
if __name__ == "__main__":
    # Executa exemplo simplificado
    #exemplo_simples()
    
    print("\n"*3)
    # Para usar com API real, descomente a linha abaixo:
    import asyncio
    asyncio.run(exemplo_chatbot_com_memoria())