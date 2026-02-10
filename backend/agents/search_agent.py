from agents.base_agent import BaseAgent
from tools.search import ddgs_search
from datetime import datetime
import json

search_agent_system_prompt = """
<core_instruction>
    1. You are the Search Agent.
    2. Your goal is to formulate the best possible search query for the user's request.
    3. Analyze the user's message and the conversation context.
    4. Output a search query that will retrieve the most relevant information.
    5. Be specific and include keywords like years (e.g., 2026) to get recent data if needed.
    6. You have access to the conversation history and any search tool which searches the internet.
</core_instruction>
<json_formatting_rules>
    You MUST output a JSON object using this schema:
    1. "chain_of_thought": 
       - Explain why you chose this query.
    2. "tool_input": 
        - The actual search string to execute.
</json_formatting_rules>
"""

search_json_schema = {
    "type": "json_object",
    "schema": {
        "type": "object",
        "properties": {
            "chain_of_thought": {"type": "string"},
            "tool_input": {"type": "string"}
        },
        "required": ["chain_of_thought", "tool_input"]
    }
}

class SearchAgent(BaseAgent):
    def _agent_logic(self, context) -> str:
        print('\nSearch Agent:\n')
        final_prompt = (
            f"{self.user_input.user_system_prompt}\n"
            f"{search_agent_system_prompt}\n"
            f"RELEVANT MEMORY:\n{self.rag_memory}"
        )
        current_context = context.copy()
        system_message = {
            "role": "system",
            "content": final_prompt
        }
        current_context.insert(0, system_message)
        
        # 1. Ask model for query
        json_response_str = self.model.model_reply(chat_data=self.user_input, context=current_context, json_schema=search_json_schema)
        
        # 2. Parse model response to get query
        try:
            parsed_json = json.loads(json_response_str, strict=False)
            query = parsed_json.get("tool_input")
            chain_of_thought = parsed_json.get("chain_of_thought", "")
        except json.JSONDecodeError:
            return json.dumps({
                "response": "Error: Failed to generate search query.",
                "chain_of_thought": "Model failed JSON generation.",
                "tool": "error",
                "tool_input": "",
                "tool_output": "System Error: The model failed to generate a valid search query JSON. Please switch to chat or try again."
            })
        print(query, '\n')
        # 3. Execute Search Tool
        if query:
            search_results = ddgs_search(query)
        else:
            search_results = "No query generated."
        
        # 4. Construct response compatible with BaseAgent.parse_json_response_string
        # The 'response' field will contain the tool output which main.py puts into 'user' role
        print('response from search tool:\n', search_results[0:200], '\n')
        result_pkg = {
            "response": "",
            "chain_of_thought": chain_of_thought,
            "tool": "web_search",
            "tool_input": query,
            "tool_output": search_results
        }
        
        return json.dumps(result_pkg)
