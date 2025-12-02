import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain_community.utilities import SQLDatabase

load_dotenv()
DB_PATH = os.path.join("data", "outlets.db")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", # Fast and free-tier eligible
    temperature=0,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

def get_db_path():
    return DB_PATH