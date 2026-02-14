import uvicorn
from enum import Enum
from fastapi import FastAPI
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from model import llm_model
from database.db import save_message_db, get_chat_history, db_chat_reset
from database.vector_db import save_interaction_embedding, get_memory_block, vector_chat_reset

from agents.dispatcher_agent import DispatcherAgent
from agents.chat_agent import ChatAgent
from agents.search_agent import SearchAgent


app = FastAPI()
#creates llm_model instance that stores llm model created using llama-cpp-python and settings from config.json
model = llm_model()

class AgentType(str, Enum):
    CHAT = "chat"
    SEARCH = "search"
    CODE = "code_interpreter"
    FINAL = "final_answer"

AGENT_REGISTRY = {
    AgentType.CHAT.value: ChatAgent,
    AgentType.SEARCH.value: SearchAgent
}

class UserInput(BaseModel):
    message: str
    user_system_prompt: str
    temperature: float = 0.7
    repeat_penalty: float = 1.15
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

def add_tool_notation(tool_output, tool_name, tool_input):
    content = f"""
        <|start_header_id|>system<|end_header_id|>

        Tool '{tool_name}' executed successfully.
        Input: "{tool_input}"
        Output:
        {tool_output}

        INSTRUCTION: Use the above information to answer the user's request.
        <|eot_id|>
        """
    return {"role": "system", "content": content}

def context_cleaning(context):
    cleaned_context = []
    for message in context:
        # Filter out dispatcher thoughts to ensure correct turn-taking for agents
        if message['role'] == "assistant" and message.get('content', '').startswith("Dispatcher thoughts:"):
            continue
        cleaned_context.append(message)
    return cleaned_context
#chat completition endpoint
@app.post('/chat')
def chat(user_input: UserInput):
    now_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_query = f'Current Date: {now_timestamp}\n{user_input.message}'
    #saving last user message to db
    save_message_db(msg=user_query, role='user')
    #getting chat history from db in the form of the list of dictionaries
    session_context = get_chat_history()
    #getting rag memory
    rag_db_memory = get_memory_block(user_query)
    
    MAX_ITERATIONS = 3
    dispatcher_agent = DispatcherAgent(model=model, rag_db_memory=rag_db_memory, user_input=user_input)
    for i in range(MAX_ITERATIONS):
        print(f'Iteration {i+1}, Dispatcher:\n')
        dispatcher_response = dispatcher_agent.generate_response(context=session_context)
        chosen_agent_name = dispatcher_response.response
        #session_context.append({"role": "assistant",
        #                         "content": f"Dispatcher thoughts: {dispatcher_response.chain_of_thought}\nChosen agent: {chosen_agent_name}"})
        agent_class = AGENT_REGISTRY.get(chosen_agent_name)
        if chosen_agent_name == "chat":
            break

        if agent_class:
            agent_instance = agent_class(model=model, rag_db_memory=rag_db_memory, user_input=user_input)
            agent_response = agent_instance.generate_response(context=session_context)
            tool_output = add_tool_notation(agent_response.tool_output, chosen_agent_name, agent_response.tool_input)
            session_context.append({"role": "user", 
                                    "content": f"{tool_output}"})
    #final_context = context_cleaning(session_context)
    final_context = context_cleaning(session_context)
    final_agent = ChatAgent(model=model, rag_db_memory=rag_db_memory, user_input=user_input)
    final_response = final_agent.generate_response(context=final_context).response

    save_message_db(msg=final_response, role='assistant')
    save_interaction_embedding(user_msg=user_query, assistant_msg=final_response)

    response_dict = {"role":"assistant", "content": final_response, "timestamp":now_timestamp}
    return response_dict

@app.get('/history')
def get_history():
    return get_chat_history()

@app.get('/reset')
def reset_chat():
    db_chat_reset()
    vector_chat_reset()

if __name__ == '__main__':
    uvicorn.run(app, host='localhost', port=8000)