from openai import AsyncOpenAI # type: ignore
from ..config import settings # type: ignore

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class OpenAIService:
    @staticmethod
    async def analyze_data(text: str):
        # Create a prompt based on analysis type
        prompt = f"Analyze this real estate data and return a basic message about what you see. Please specifically tell me about any IRR esimations you can make and things that would maximize the investment: {text}"
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a real estate analysis expert."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
        