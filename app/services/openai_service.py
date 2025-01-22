from openai import AsyncOpenAI # type: ignore
from ..config import settings # type: ignore

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class OpenAIService:
    @staticmethod
    async def analyze_data(data: dict, analysis_type: str):
        # Create a prompt based on analysis type
        prompt = f"Analyze this real estate data for {analysis_type}:\n{data}"
        
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a real estate analysis expert."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        return response.choices[0].message.content