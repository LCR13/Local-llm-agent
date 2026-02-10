import json
from pydantic import BaseModel
from typing import final
from abc import ABC, abstractmethod

class ResponseModel(BaseModel):
    response: str
    chain_of_thought: str
    tool: str
    tool_input: str
    tool_output: str


class BaseAgent(ABC):
    def __init__(self, model, rag_db_memory, user_input):
        self.model = model
        self.rag_memory = rag_db_memory
        self.user_input = user_input
        self.tools = {}

    def generate_response(self, context)  -> ResponseModel:
        model_reply_string = self._agent_logic(context)
        parsed_response = self.parse_json_response_string(json_string=model_reply_string)
        return ResponseModel(**parsed_response)

    @abstractmethod
    def _agent_logic(self, context) -> str:
        """ Every agent must implement this method"""
        pass

    def parse_json_response_string(self, json_string) -> str:
        try:
            parsed_json = json.loads(json_string, strict=False)
        except json.JSONDecodeError:
            print(f"CRITICAL ERROR: '{json_string}'")
            parsed_json = {"response": "Error: Model failed to generate a valid JSON.", "chain_of_thought":"I failed to format my output correctly.", "tool": "", "tool_input": "", "tool_output": ""}
        response = parsed_json.get("response", "")
        chain_of_thought = parsed_json.get("chain_of_thought", "")
        tool = parsed_json.get("tool", "")
        tool_input = parsed_json.get("tool_input", "")
        tool_output = parsed_json.get("tool_output", "")
        return {"response":response, "chain_of_thought":chain_of_thought, "tool":tool, "tool_input":tool_input, "tool_output":tool_output}