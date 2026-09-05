from serpapi import GoogleSearch
from langchain.tools import tool
from dotenv import load_dotenv
import os

load_dotenv()
serpapi_key = os.getenv("SERPAPI_KEY")

@tool
def ws(name: str):
    """
    Use this tool when the user wants to buy a product, compare prices,
    check product availability, or asks for the price of an item.
    """

    params = {
        "engine": "google_shopping",
        "q": name,
        "api_key": serpapi_key,
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    shopping_results = results.get("shopping_results", [])

    if not shopping_results:
        return "No shopping results found."

    return shopping_results[:5]