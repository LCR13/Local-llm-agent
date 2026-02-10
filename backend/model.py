import json
import os
import sys
from llama_cpp import Llama

CONFIG_FILE = 'config.json'
print('\ninitializing model\n')

default_json_schema = {
                "type": "json_object",
                "schema": {
                    "type": "object",
                    "properties": {
                        "chain_of_thought": {"type": "string"},
                        "tool":{"type":"string"},
                        "tool_input":{"type":"string"},
                        "response": {"type":"string"},
                        },
                    "required": ["chain_of_thought", "tool", "tool_input","response" ]
                }
}

class llm_model:
    def __init__(self):
        self.model = self.model_init()

    #load config.json for model initialization
    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            print('Config file not found')
            sys.exit(1)
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print('Syntax error in json')
            sys.exit(1)

    #init model from config
    def model_init(self):
        config = self.load_config()
        settings = config.get('model_settings', {})
        
        model_path = settings.get('model_path')
        if not os.path.exists(model_path):
            print(f'Model not found by the path: {model_path}')
            sys.exit(1)
        
        llm = Llama(
            model_path=model_path,
            n_ctx=settings.get('n_ctx', 8192),
            n_gpu_layers=settings.get('n_gpu_layers', -1),
            verbose=settings.get('varbose', False),
            chat_format='llama-3'
        )
        return llm

    #returns json in the form of a string from a chat chat_data
    def model_reply(self, chat_data, context, json_schema=default_json_schema, max_tokens=4096, agent_temperature=None):
        temperature = agent_temperature if agent_temperature else chat_data.temperature
        stream_response = self.model.create_chat_completion(
            messages = context,
            #Lower the temperature higher the chance of most probable tokens to be selected
            temperature=temperature,
            #repeat_penalty > 1 pelizes repetition by making repeated tokens less likely to be selected
            repeat_penalty=chat_data.repeat_penalty,
            #stream true to see the output as a stream in the console
            stream=True,
            max_tokens=max_tokens,
            response_format= json_schema,
            stop=[
             #   "<|eot_id|>",
              #  "<|start_header_id|>",
               # "<|end_of_text|>"
            ]

            )
        json_string = ''
        for chunk in stream_response:
            delta = chunk['choices'][0]['delta'].get('content', '')
            if delta:
                print(delta, end='', flush=True)
                json_string += delta
        return json_string