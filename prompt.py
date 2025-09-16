EXTRACT_SYSTEM_MESSAGE = """
Analyze the following conversation and extract important information about the user:
{conversation_text}

Return a JSON with:
- name: User's name (if mentioned)
- interests: List of mentioned interests
- preferences: Expressed preferences
- context: Relevant context of the conversation

If no information is found, return empty fields.
"""

CREATE_SYSTEM_MESSAGE = """
Summarize the following conversation concisely, highlighting:
- Main topics discussed
- Important decisions or conclusions
- Relevant context for future conversations

Conversation:
{conversation_text}

Summary:
"""

# Função para formatar os prompts
def get_create_system_message(conversation_text: str) -> str:
    return CREATE_SYSTEM_MESSAGE.format(conversation_text=conversation_text)

def get_extract_system_message(conversation_text: str) -> str:
    return EXTRACT_SYSTEM_MESSAGE.format(conversation_text=conversation_text)
