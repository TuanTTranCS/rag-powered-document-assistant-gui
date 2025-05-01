import os
import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv
import json
from pprint import pprint

class RAGAgent:
    def __init__(self):
        load_dotenv(override=True)

        vertexai.init(
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION"),
        )
        self.user_id = "123"
        self.agent_engine_id = os.getenv("AGENT_ENGINE_ID")
        self.agent_engine = agent_engines.get(self.agent_engine_id)
        self.session = self.agent_engine.create_session(user_id=self.user_id)

    def stream_query(self, message):
        return self.agent_engine.stream_query(
            user_id=self.user_id,
            session_id=self.session['id'],
            message=message,
        )
    
    def pretty_print_event(self, event):
        """Pretty prints an event with truncation for long content."""
        if "content" not in event:
            print(f"[{event.get('author', 'unknown')}]: {event}")
            return
            
        author = event.get("author", "unknown")
        parts = event["content"].get("parts", [])
        
        for part in parts:
            if "text" in part:
                text = part["text"]
                # Truncate long text to 200 characters
                if len(text) > 200:
                    text = text[:197] + "..."
                print(f"[{author}]: {text}")
            elif "functionCall" in part:
                func_call = part["functionCall"]
                print(f"[{author}]: Function call: {func_call.get('name', 'unknown')}")
                # Truncate args if too long
                args = json.dumps(func_call.get("args", {}))
                if len(args) > 100:
                    args = args[:97] + "..."
                print(f"  Args: {args}")
            elif "functionResponse" in part:
                func_response = part["functionResponse"]
                print(f"[{author}]: Function response: {func_response.get('name', 'unknown')}")
                # Truncate response if too long
                response = json.dumps(func_response.get("response", {}))
                if len(response) > 100:
                    response = response[:97] + "..."
                print(f"  Response: {response}")
    
    def get_agent_text_from_event(self, event):
        """Extracts text from the event."""
        author = event.get("author", "unknown")
        if author == 'ask_rag_agent' and "content" in event:
            parts = event["content"].get("parts", [])
            for part in parts:
                if "text" in part:
                    return part["text"]
        return None
    
rag_agent = RAGAgent()
# query = "Hi, how are you?"
# for event in rag_agent.stream_query(
#         user_id="123",
#         session_id=rag_agent.session['id'],
#         message=query,
#     ):
#     rag_agent.pretty_print_event(event)
#     # pprint(event)