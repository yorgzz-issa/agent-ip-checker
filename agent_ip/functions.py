from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field
from langchain.prompts import PromptTemplate
from pydantic import BaseModel, Field
from langchain.llms.base import LLM
from typing import Any, List, Optional, Dict
from groq import Groq
import os
from langchain_community.callbacks.manager import get_openai_callback
from langchain.chains import RetrievalQA

class GroqLLMConfig(BaseModel):
    model_name: str = Field(..., description="The name of the Groq model to use.")
    temperature: float = Field(0.0, description="The temperature to use for sampling.")
    groq_api_key: str = Field(..., description="The API key for Groq.")

class GroqLLM(LLM):
    config: GroqLLMConfig
    client: Any = None

    def __init__(self, model_name: str, temperature: float = 0.0, groq_api_key: Optional[str] = None):
        super().__init__()
        groq_api_key = groq_api_key
        if not groq_api_key:
            raise ValueError("Groq API key must be provided or set as GROQ_API_KEY environment variable.")
        self.config = GroqLLMConfig(
            model_name=model_name,
            temperature=temperature,
            groq_api_key=groq_api_key
        )
        self.client = Groq(api_key=self.config.groq_api_key)

    @property
    def config(self) -> GroqLLMConfig:
        return self._config

    @config.setter
    def config(self, value: GroqLLMConfig):
        self._config = value

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.config.model_name,
            temperature=self.config.temperature,
        )
        return response.choices[0].message.content

    @property
    def _llm_type(self) -> str:
        return "Groq"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model_name": self.config.model_name, "temperature": self.config.temperature}

llm = GroqLLM(
 model_name="llama-3.3-70b-versatile", # "llama-3.1-70b-versatile"
temperature=0.1,
groq_api_key="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")

template = """Answer the following Question:
The given IP reputation score indicates the status of the IP's behavior based on its history and the presence of any malicious activity(a score of 0 means that the IP is clean, and a score of 100 means that the IP is abusive and high risk). Below is the IP reputation score along with other relevant details:

IP Reputation Score: {input_question}  
Additional Information: {additional_info}

Question: Based on the IP reputation score provided above, explain whether this IP is considered trustworthy or potentially harmful. What actions should be taken if this IP is found to be harmful?

Answer:"""

PROMPT_chats= PromptTemplate(
template=template, input_variables=["input_question","additional_info"]
)

def get_answer(input_question,additional_info):
    prompt = PROMPT_chats.format(input_question=input_question,additional_info=additional_info)

    with get_openai_callback():
        answer = llm(prompt)
    answer = answer.replace('"', '')
    return answer
