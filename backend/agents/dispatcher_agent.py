from agents.base_agent import BaseAgent
from datetime import datetime

agent_system_prompt = f"""
### ROLE: CENTRAL DISPATCHER
You are a Supervisor that routes messages to 'search' or 'chat'.
Your ONLY goal is to satisfy the user's *original* request using usage history.

### INPUT ANALYSIS (CRITICAL):
Look at the **most recent messages** in the conversation history (bottom of the context).

1. **CHECK FOR TOOL RESULTS**:
   - Do you see a message containing `### SYSTEM NOTIFICATION: tool: ... results ###`?
   - **YES_RESULTS_FOUND**: This means the data has been retrieved. 
     -> **ACTION**: FORCE 'chat' to generate the answer. 
     -> **STOP SEARCHING**.

2. **CHECK USER INTENT (Only if no recent tool results)**:
   - Does the user ask for real-time info (News, Weather, Stocks, "Who is X")? -> 'search'
   - Does the user ask for creative, general, or coding tasks? -> 'chat'

### ANTI-LOOPING RULES:
- If you see `tool: search results` in the history, the SEARCH IS DONE. Do not search again for the same query.
- Even if the search results say "No results found", switch to 'chat' so the assistant can apologize or ask for clarification.

### DECISION LOGIC:
IF (Last_Message contains "SYSTEM NOTIFICATION") -> RESPONSE = "chat"
ELSE IF (User_Request needs external_data) -> RESPONSE = "search"
ELSE -> RESPONSE = "chat"
"""

dispatcher_json_schema = {
    "type": "json_object",
    "schema": {
        "type": "object",
        "properties": {
            "chain_of_thought": {
                "type": "string",
                "description": "Step 1: Did I see 'SYSTEM NOTIFICATION' in the last message? Step 2: If yes, output 'chat'. If no, analyze user request."
            },
            "response": {
                "type": "string",
                "enum": ["chat", "search"],
                "description": "The selected agent."
            }
        },
        "required": ["chain_of_thought", "response"]
    }
}

class DispatcherAgent(BaseAgent):
    def _agent_logic(self, context) -> str:
        final_prompt = (
            f"Persona:{self.user_input.user_system_prompt}\n"
            f"{agent_system_prompt}\n"
            f"RELEVANT MEMORY:\n{self.rag_memory}"
        )
        current_context = context.copy()
        system_message = {
            "role": "system", 
            "content": final_prompt, 
        }
        current_context.insert(0, system_message)
        json_response_str = self.model.model_reply(
            chat_data=self.user_input, 
            context=current_context, 
            json_schema=dispatcher_json_schema, 
            agent_temperature=0.1)
        
        return json_response_str
