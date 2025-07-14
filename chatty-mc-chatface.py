from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from collections import defaultdict

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Fastapi setup
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# chatmodel setup
## Initialise model and prompt format
chatModel = ChatOllama(model="llama3", num_gpu=1)
human_input = f"{{request}}"
prompt = ChatPromptTemplate.from_messages(
    [
        MessagesPlaceholder(variable_name="history"),
        ("human", human_input),
    ]
)

# Build chain base
chain = prompt | chatModel

# Define memory structure
store = defaultdict(lambda: InMemoryChatMessageHistory())

# Build chain with memory
chain_with_history = RunnableWithMessageHistory(
                        chain, 
                        lambda session_id: store[session_id], 
                        input_messages_key="request", 
                        history_messages_key="history")

@app.get("/", response_class=HTMLResponse)
def chat(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )

@app.get("/clear")
def clear():
    store.clear()
    return 'Memory cleared'

@app.websocket("/ws")
async def chat_response(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        response = chain_with_history.invoke(
            {"request": data}, 
            config={"configurable": {"session_id": "ID"}}
        )
        await websocket.send_text(f"{response.content}")