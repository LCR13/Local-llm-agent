from sqlmodel import SQLModel, Field, create_engine, Session, select, delete
from typing import Optional
from datetime import datetime

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    role: str
    content: str
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)
SQLModel.metadata.create_all(engine)
#suboptimal
def save_message_db(msg:str, role:str):
    with Session(engine) as session:
        #making instances of message class that can be added to db
        msg_db = Message(role=role, content=msg)
        session.add(msg_db)
        session.commit()

def get_chat_history():
    chat_history = []
    with Session(engine) as session:
        # Get the latest 50 messages (descending order), then reverse to chronological
        statement = select(Message).order_by(Message.timestamp.desc()).limit(50)
        results = session.exec(statement).all()
        # SQLModel results are objects, easy to reverse
        results.reverse()
        
        for message in results:
            # Removed redundant timestamp in content, standard {'role': role, 'content': content}
            chat_history.append({"role": message.role, "content": message.content})
        return chat_history
def db_chat_reset():
    with Session(engine) as session:
        statement = delete(Message)
        session.exec(statement)
        session.commit()