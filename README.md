Local llm agent with web interface.

Functionality:
1. Chat completition
2. RAG for long-term memory
3. Basic Duck Duck Go search
User can tweak following response generating parameters:
1. Temperature
2. Repeat penalty
3. User's system prompt

How to use:
Path to model in .gguf extension is specified in config.json file (there is an template, just change the name to config.json and specify parameters suitable to your's machine)

To run:
Use docker compose up --build in core folder
Right now it's installing 12.4 cuda version distro, 