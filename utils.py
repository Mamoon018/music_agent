from groq.types.chat.completion_create_params import ResponseFormat
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from langchain_groq import ChatGroq

def get_llm(model_name:str, temperature:float = 0,max_retries:int = 2, api_key:str =None):
    llm = ChatGroq(
    model=model_name,
    temperature=temperature,
    max_retries=max_retries,
    api_key=api_key
            )

    return llm

class Settings(BaseSettings):
    GROQ_API_KEY: str
    OPIK_API_KEY: str
    OPIK_WORKSPACE: str
    OPIK_PROJECT_NAME: str

    model_config = {
        "env_file": ".env"
    }

settings = Settings()




"""
# DO NOT REMOVE THIS CODE.
client = Groq(
    api_key=settings.GROQ_API_KEY
)

response = client.chat.completions.create(
    model="openai/gpt-oss-20b",
    messages=[
        {
            "role": "user",
            "content": "Search for recent AI developments and then visit the Groq website"
        }
    ],
    tools=[
        {
            "type": "browser_search"
        }
    ],
    temperature=0
)

print(response.choices[0].message.content)
"""