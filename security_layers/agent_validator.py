from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv('OPENAI_KEY'))

system_prompt = """
You are the best validator agent, you must analyze the input prompts [in Spanish] and check if any of the rules are broken. 
If any rule is broken, it returns 'T'. If no rule is broken, it returns 'F'.
Rules:
1. No hablar de política.
"""

def security_agent_validator(prompt):
    completion = client.chat.completions.create(
        model="gpt-4",
        temperature = 0.2,
        messages= [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    )
    full_response = completion.choices[0].message.content
    # print(completion)

    if full_response == 'T':
        return True
    else:
        return False