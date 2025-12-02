from langchain.tools import tool
from app.services.rag_service import RAGService
from app.services.sql_service import SQLService
from dependencies import llm, get_db_path

# 1. Initialize Services
rag_service = RAGService(llm)
sql_service = SQLService(llm, get_db_path())

# 2. Define the Calculator Tool
@tool
def calculator(expression: str) -> str:
    """Calculate the result of a mathematical expression. 
    Useful for calculating prices, discounts, or converting units.
    Input should be a valid Python math expression like '200 * 0.8'."""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"Error calculating: {e}"

# 3. Wrap RAG (Products) as a Tool
@tool
def product_search(query: str) -> str:
    """Search for drinkware, tumblers, or merchandise information in the product catalog.
    Useful when the user asks about product prices, features, or availability."""
    try:
        from app.main import ml_models 
        
        result = rag_service.search_and_summarize(query, top_k=3, ml_models=ml_models)
        return result["summary"]
    except Exception as e:
        return f"Error searching products: {e}"

# 4. Wrap Text-to-SQL (Outlets) as a Tool
@tool
def outlet_search(query: str) -> str:
    """Search for ZUS Coffee outlet locations, hours, or specific features..."""
    print(f"DEBUG: Agent called outlet_search with query: '{query}'") # <--- ADD THIS
    try:
        result = sql_service.process_natural_language_query(query)
        if result["count"] == 0:
            return "No outlets found matching that description."
        
        # Format the raw rows into a readable string for the LLM
        formatted_results = "\n".join([str(row) for row in result["results"]])
        return f"Found {result['count']} outlets:\n{formatted_results}"
    except Exception as e:
        return f"Error searching outlets: {e}"

# List of tools to export
tools = [calculator, product_search, outlet_search]