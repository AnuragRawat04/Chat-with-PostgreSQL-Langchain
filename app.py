import streamlit as st
from pathlib import Path
import os

from dotenv import load_dotenv
load_dotenv()
api_key_groq = os.getenv("GROK_API_KEY")

# LangChain and DB tools
from langchain_groq import ChatGroq
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.callbacks.streamlit import StreamlitCallbackHandler
from sqlalchemy import create_engine

# Streamlit page setup
st.set_page_config(
    page_title="LangChain: Chat with PostgreSQL DB",
    page_icon="🐘"
)
st.title("LangChain: Chat with PostgreSQL DB")

# ⚠️ Injection Security Warning
INJECTION_WARNING = """
⚠️ **Security Warning:**  
The SQL agent can be vulnerable to **prompt injection** attacks. It is strongly recommended to use a **database role with limited permissions** (e.g., read-only).

🔗 [Read more here](https://python.langchain.com/docs/security)
"""
st.sidebar.markdown(INJECTION_WARNING)

# Sidebar for PostgreSQL config
st.sidebar.subheader("PostgreSQL Connection Details")
pg_host = st.sidebar.text_input("Host", value="localhost")
pg_port = st.sidebar.text_input("Port", value="5432")
pg_user = st.sidebar.text_input("Username", value="postgres")
pg_password = st.sidebar.text_input("Password", type="password")
pg_db = st.sidebar.text_input("Database Name", value="Lancgchain")

# API key input (although already loaded from .env)
api_key = st.sidebar.text_input("GROQ API Key", type="password", value=api_key_groq)

if not api_key:
    st.warning("Please provide the GROQ API Key.")
    st.stop()

# Connect to LLM
llm = ChatGroq(model="llama3-8b-8192", api_key=api_key_groq, streaming=True)


# PostgreSQL connection
@st.cache_resource(ttl="2h")
def configure_postgresql(user, password, host, port, dbname):
    engine_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    return SQLDatabase.from_uri(engine_url)

try:
    db = configure_postgresql(pg_user, pg_password, pg_host, pg_port, pg_db)
except Exception as e:
    st.error(f"❌ Failed to connect to PostgreSQL: {e}")
    st.stop()

# LangChain SQL agent setup
toolkit = SQLDatabaseToolkit(db=db, llm=llm)
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

# Chat History
if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [
        {"role": "assistant", "content": "👋 Hi! I’m your SQL assistant. Ask me anything about your PostgreSQL database!"}
    ]

# Display chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
user_query = st.chat_input("Type your SQL-related question...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container())
        try:
            response = agent.run(user_query, callbacks=[streamlit_callback])
        except Exception as e:
            response = f"❌ Error: {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)
