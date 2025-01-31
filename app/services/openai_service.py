from openai import OpenAI
import asyncio
from typing import Dict, Any, List, Callable
from openai.types.chat import ChatCompletion
import time
import os
from ..config import Settings # type: ignore

settings = Settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

class OpenAIService:
    MAX_CHUNK_SIZE = 4000  # Smaller chunks for faster processing
    MODEL_NAME = "gpt-4-1106-preview"
    CONCURRENT_REQUESTS = 3  # Number of concurrent API calls

    @staticmethod
    def chunk_text(text: str) -> List[str]:
        """Split text into smaller chunks."""
        lines = text.split('\n')
        chunks: List[str] = []
        current_chunk: List[str] = []
        current_size: int = 0
        
        for line in lines:
            line_size = len(line) // 4
            if current_size + line_size > OpenAIService.MAX_CHUNK_SIZE:
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        return chunks

    @staticmethod
    async def process_chunk(chunk: str, file_type: str, chunk_num: int, total_chunks: int) -> str:
        """Process a single chunk with retry logic."""
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                system_message = OpenAIService.get_system_prompt(file_type, chunk_num, total_chunks)
                
                def run_completion() -> ChatCompletion:
                    return client.chat.completions.create(
                        model=OpenAIService.MODEL_NAME,
                        messages=[
                            {"role": "system", "content": system_message},
                            {"role": "user", "content": chunk}
                        ],
                        temperature=0.3,
                        max_tokens=1000
                    )
                
                completion = await asyncio.to_thread(run_completion)
                return completion.choices[0].message.content or ""
            except Exception as e:
                last_error = e
                if attempt == max_retries - 1:
                    print(f"Failed after {max_retries} attempts: {str(e)}")
                    return ""
                await asyncio.sleep(2 ** attempt)
        
        print(f"Unexpected error: {str(last_error)}")
        return ""

    @staticmethod
    async def process_chunks(chunks: List[str], file_type: str) -> List[str]:
        """Process chunks in parallel with rate limiting."""
        semaphore = asyncio.Semaphore(OpenAIService.CONCURRENT_REQUESTS)

        async def process_with_semaphore(chunk: str, index: int, total: int) -> str:
            async with semaphore:
                return await OpenAIService.process_chunk(chunk, file_type, index + 1, total)

        async def safe_process(chunk: str, index: int, total: int) -> str:
            try:
                return await process_with_semaphore(chunk, index, total)
            except Exception as e:
                print(f"Error processing chunk {index + 1}: {str(e)}")
                return ""

        tasks = [
            safe_process(chunk, i, len(chunks))
            for i, chunk in enumerate(chunks)
        ]

        try:
            return await asyncio.gather(*tasks)
        except Exception as e:
            print(f"Error in gather: {str(e)}")
            return [""] * len(chunks)

    @staticmethod
    async def analyze_data(text: str, file_type: str) -> Dict[str, Any]:
        """Analyze the text data efficiently."""
        try:
            # Split and process chunks in parallel
            chunks = OpenAIService.chunk_text(text)
            print(f"Processing {len(chunks)} chunks in parallel")
            
            # Process all chunks concurrently
            chunk_analyses = await OpenAIService.process_chunks(chunks, file_type)
            
            # Combine analyses
            combined_analysis = "\n\n".join([
                f"=== Section {i+1} Analysis ===\n{analysis}"
                for i, analysis in enumerate(chunk_analyses)
            ])
            
            # Get final summary
            print("Generating final summary")
            final_response = await OpenAIService.get_final_summary(combined_analysis, file_type)
            
            return {
                "filename": "analysis_result.txt",
                "file_type": file_type,
                "analysis": final_response,
                "raw_analyses": chunk_analyses  # Include raw analyses for future structured processing
            }
        except Exception as e:
            print(f"Error in analyze_data: {str(e)}")
            raise

    @staticmethod
    async def get_final_summary(analyses: str, file_type: str) -> str:
        """Get final summary using GPT-4."""
        try:
            system_message = OpenAIService.get_final_system_prompt(file_type)
            
            def run_completion() -> ChatCompletion:
                return client.chat.completions.create(
                    model=OpenAIService.MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": analyses}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
            
            completion = await asyncio.to_thread(run_completion)
            return completion.choices[0].message.content or ""
        except Exception as e:
            print(f"Error in final summary: {str(e)}")
            raise

    @staticmethod
    def get_system_prompt(file_type: str, chunk_num: int, total_chunks: int) -> str:
        """Get the appropriate system prompt based on file type."""
        base_prompt = f"Analyze part {chunk_num}/{total_chunks} of the data. Extract key metrics and facts only. Be concise and focus on numbers. "
        
        prompts = {
            "rent_roll": base_prompt + """List only:
- Total rent for units in this section
- Number and types of units
- Occupancy status
- Rent ranges""",
            
            "financials": base_prompt + """List only:
- Revenue items and amounts
- Expense items and amounts
- Key ratios if present
- Notable financial metrics""",
            
            "om": base_prompt + """List only:
- Property specifications
- Market data points
- Financial highlights
- Key features"""
        }
        
        return prompts.get(file_type, base_prompt + "Extract key facts and numbers.")

    @staticmethod
    def get_final_system_prompt(file_type: str) -> str:
        """Get the final analysis system prompt."""
        base_prompt = "Synthesize the section analyses into a concise summary. Focus on key metrics and insights. "
        
        prompts = {
            "rent_roll": base_prompt + """Provide:
1. Total property income and occupancy metrics
2. Unit mix summary
3. Key findings and recommendations""",
            
            "financials": base_prompt + """Provide:
1. Key financial metrics summary
2. Operating performance analysis
3. Investment considerations""",
            
            "om": base_prompt + """Provide:
1. Property overview
2. Market position
3. Investment highlights"""
        }
        
        return prompts.get(file_type, base_prompt + "Summarize key findings.")

    @staticmethod
    async def generate_investment_analysis(individual_results: List[Dict[str, Any]]) -> str:
        """Generate a comprehensive investment analysis combining all document analyses."""
        try:
            # Organize analyses by type
            analyses_by_type = {
                'om': [],
                'rent_roll': [],
                'financials': []
            }
            
            for result in individual_results:
                if result['file_type'] in analyses_by_type:
                    analyses_by_type[result['file_type']].append(result['analysis'])

            # Combine all analyses into a structured prompt
            combined_text = "=== Property Analysis Data ===\n\n"
            
            if analyses_by_type['om']:
                combined_text += "OFFERING MEMORANDUM INSIGHTS:\n"
                combined_text += "\n".join(analyses_by_type['om'])
                combined_text += "\n\n"
            
            if analyses_by_type['rent_roll']:
                combined_text += "RENT ROLL ANALYSIS:\n"
                combined_text += "\n".join(analyses_by_type['rent_roll'])
                combined_text += "\n\n"
            
            if analyses_by_type['financials']:
                combined_text += "FINANCIAL ANALYSIS:\n"
                combined_text += "\n".join(analyses_by_type['financials'])
                combined_text += "\n\n"

            # Create investment analysis prompt
            system_message = """You are an expert real estate investment analyst. Based on the provided analyses from multiple documents, 
generate a comprehensive investment analysis. Focus on:

1. Key Investment Metrics:
   - Projected IRR (if data available)
   - Equity Multiple (if data available)
   - Cap Rate (current and projected)
   - Cash-on-Cash Return
   - Break-even Analysis

2. Financial Analysis:
   - Net Operating Income (NOI)
   - Revenue Streams Breakdown
   - Operating Expense Ratio
   - Debt Service Coverage Ratio (if data available)

3. Market Analysis:
   - Location Strengths/Weaknesses
   - Market Trends
   - Competitive Position

4. Risk Assessment:
   - Tenant Risk Analysis
   - Market Risk Factors
   - Financial Risk Factors
   - Mitigation Strategies

5. Investment Recommendations:
   - Key Value-Add Opportunities
   - Suggested Investment Strategy
   - Exit Strategy Options
   - Recommended Hold Period

Format the output in a clear, structured manner with sections and bullet points.
Include specific numbers and calculations where possible.
If certain metrics cannot be calculated, explain why and what additional information would be needed.
Conclude with a clear investment recommendation."""

            def run_completion() -> ChatCompletion:
                return client.chat.completions.create(
                    model=OpenAIService.MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": combined_text}
                    ],
                    temperature=0.7,
                    max_tokens=3000
                )

            completion = await asyncio.to_thread(run_completion)
            return completion.choices[0].message.content or ""

        except Exception as e:
            print(f"Error in investment analysis: {str(e)}")
            raise