import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
from dotenv import load_dotenv
import os

from langchain_community.utilities import SQLDatabase
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent
from langchain_community.llms import AzureOpenAI

# Load environment
load_dotenv()

# Azure OpenAI setup
llm = AzureOpenAI(
    openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)

# Sidebar for Db2 login
st.sidebar.header("🔐 Db2 Login")
db_user = st.sidebar.text_input("Username")
db_pass = st.sidebar.text_input("Password", type="password")
db_host = st.sidebar.text_input("Host", value="localhost")
db_port = st.sidebar.text_input("Port", value="50000")
db_name = st.sidebar.text_input("Database Name")

if st.sidebar.button("Connect"):
    try:
        db_uri = f"db2+ibm_db://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
        engine = create_engine(db_uri)
        db = SQLDatabase(engine)
        st.session_state['db'] = db
        st.success("Connected ✅")
    except Exception as e:
        st.error(f"Connection failed: {e}")

if 'db' in st.session_state:
    toolkit = SQLDatabaseToolkit(db=st.session_state['db'], llm=llm)
    agent = create_sql_agent(llm=llm, toolkit=toolkit, verbose=True)

    st.title("🧠 Healthcare Insights Assistant")
    query = st.text_input("Ask a question about your patient data:")

    if query:
        with st.spinner("Analyzing..."):
            try:
                response = agent.run(query)
                st.success("✅ Answer:")
                st.write(response)
            except Exception as e:
                st.error(f"Error: {e}")
else:
    st.warning("Please connect to the database first.")