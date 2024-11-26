import openai
from app.core.config import settings

openai.api_key = settings.OPENAI_API_KEY

def generate_chat_response(prompt: str, conversation_history: list) -> str:
    """
    Generate a response from OpenAI's GPT model based on the prompt and conversation history.
    """
    try:
        # Prepare messages for Chat API
        messages = [
            {"role": "system", "content": "You are a helpful legal assistant specialized in contract law."}
        ]
        for msg in conversation_history:
            role = "user" if msg["sender"] == "user" else "assistant"
            messages.append({"role": role, "content": msg["content"]})
        messages.append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model=settings.OPENAI_MODEL,
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"Error generating response: {str(e)}"
