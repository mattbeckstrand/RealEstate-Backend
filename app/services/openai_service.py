# from openai import OpenAI
# import os
# from dotenv import load_dotenv

# load_dotenv()

# # Initialize the client with your API key
# api_key = os.getenv('OPENAI_API_KEY')
# if not api_key:
#     raise ValueError("OpenAI API key not found in environment variables")

# client = OpenAI(
#     api_key=api_key
# )
# completion = client.chat.completions.create(
#     model="gpt-4o-mini",
#     messages=[
#         {"role": "system", "content": "You are a helpful assistant."},
#         {
#             "role": "user",
#             "content": "Write a haiku about recursion in programming."
#         }
#     ]
# )

# print(completion.choices[0].message)