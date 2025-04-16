# # llm_client.py
# import os

# DEPLOYMENT = os.getenv("DEPLOYMENT", "personal")

# if DEPLOYMENT == "client":
#     from langchain_openai import AzureChatOpenAI

#     class LLMWrapper:
#         def __init__(self):
#             self.model = AzureChatOpenAI(
#                 azure_deployment="gpt-4",
#                 azure_endpoint="https://your-client-endpoint.openai.azure.com/",
#                 api_key=os.getenv("AZURE_OPENAI_API_KEY"),
#                 api_version="2023-05-15",
#             )

#         async def chat(self, messages, model, temperature):
#             # AzureChatOpenAI returns a LangChain `AIMessage`
#             response = await self.model.ainvoke(messages, temperature=temperature)
#             return {"content": response.content}

# elif DEPLOYMENT == "personal":
#     from openai import AsyncOpenAI

#     class LLMWrapper:
#         def __init__(self):
#             self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#         async def chat(self, messages, model, temperature):
#             response = await self.client.chat.completions.create(
#                 model=model,
#                 messages=messages,
#                 temperature=temperature
#             )
#             return {"content": response.choices[0].message.content}

# else:
#     raise EnvironmentError("DEPLOYMENT must be either 'client' or 'personal'")

# llm = LLMWrapper()
import os
from langchain_openai import AzureChatOpenAI
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

DEPLOYMENT = os.getenv("DEPLOYMENT")  # either "azure" or "openai"

if DEPLOYMENT == "azure":
    llm_raw = AzureChatOpenAI(
        azure_deployment=os.getenv("AZURE_DEPLOYMENT_NAME"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0.2
    )

    class AzureWrapper:
        async def chat(self, model: str, messages: list, temperature: float = 0.2):
            result = await llm_raw.ainvoke(messages)
            return {"content": result.content}

    llm = AzureWrapper()

else:
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    class OpenAIWrapper:
        async def chat(self, model: str, messages: list, temperature: float = 0.2):
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            return {"content": response.choices[0].message.content}

    llm = OpenAIWrapper()

