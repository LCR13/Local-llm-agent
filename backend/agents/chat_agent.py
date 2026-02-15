from agents.base_agent import BaseAgent
from datetime import datetime

agent_system_prompt =  """
### ROLE: INTELLIGENT ASSISTANT (THE FINAL ANSWER)
You are the voice of the system. Your goal is to synthesize all available information into a perfect, coherent response.

### INPUT DATA SOURCES:
1. **User Query**: The latest request from the user.
2. **Context History**: Previous conversation turns.
3. **Tool Outputs (Crucial)**: Look for messages with role 'user' containing tool_output or code results. THIS IS YOUR GROUND TRUTH.

### THINKING PROTOCOL (Chain of Thought):
You MUST populate the `chain_of_thought` field by following these steps:
1. **Analyze Intent**: What does the user *really* want?
2. **Data Verification**: Do I have tool outputs (search results) in the context? 
   - IF YES: Extract key facts, dates, and numbers.
   - IF NO: Rely on internal knowledge or conversation history.
3. **Style Check**: Ensure the tone matches the requested persona (e.g., helpful, strict, or roleplay).
4. **Drafting Strategy**: How will I structure the answer? (Intro -> Facts -> Conclusion).

### RESPONSE RULES:
- **Comprehensive**: Do not be lazy. If you have search results, use them fully.
- **No Meta-Talk**: Do not say "Based on the search results...". Just answer naturally.
- **Language**: Answer in the same language as the user's query.

<json_formatting_rules>
    You MUST output a JSON object using this schema:
    1. "chain_of_thought": A detailed paragraph (minimum 100 words) explaining your reasoning process.
    2. "response": The final answer, analyze your chain of thought and synthesize a concise, accurate response to the user's original query. This should be in natural language, not referencing the chain of thought directly.
</json_formatting_rules>
"""

chat_json_schema = {
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "chain_of_thought": {"type": "string"},
                        "response": {"type":"string"}
                        },
                    "required": ["chain_of_thought", "response" ]
                }
}

class ChatAgent(BaseAgent):
    def _agent_logic(self, context) -> str:
        print('Chat Agent:\n')
        final_prompt = (
            f"Persona:{self.user_input.user_system_prompt}\n"
            f"{agent_system_prompt}\n"
            f"RELEVANT MEMORY:\n{self.rag_memory}"
        )
        current_context = context.copy()
        system_message = {
            "role": "system", 
            "content": final_prompt
        }
        current_context.insert(0, system_message)
        json_response_str = self.model.model_reply(chat_data=self.user_input, context=current_context, json_schema=chat_json_schema)
        
        return json_response_str