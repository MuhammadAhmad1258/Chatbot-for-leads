# tools.py

from google.adk.tools import FunctionTool, ToolContext
from . import database  # apna database.py module


def search_faqs(query: str, tool_context: ToolContext) -> dict:
    """
    Searches the client's FAQ knowledge base for an answer matching the user's query.

    Args:
        query: The user's question, in their own words.

    Returns:
        dict with status and the matched FAQ answer(s), or a not_found status.
    """
    client_id = tool_context.state.get("client_id","demo_client")
    if not client_id:
        return {"status": "error", "error_message": "client_id missing from session state."}

    results = database.search_faqs(client_id=client_id, query=query)

    if not results:
        return {"status": "not_found", "message": "No matching FAQ found."}

    return {"status": "success", "results": results}


def capture_lead(name: str, contact: str, message: str, tool_context: ToolContext) -> dict:
    """
    Saves a potential lead's contact details when they express interest
    or when the FAQ can't answer their question.

    Args:
        name: The lead's name.
        contact: Email or phone number provided by the lead.
        message: What the lead is interested in / their query.

    Returns:
        dict confirming the lead was saved, with its id.
    """
    client_id = tool_context.state.get("client_id", "demo_client")
    if not client_id:
        return {"status": "error", "error_message": "client_id missing from session state."}

    if not name or not contact:
        return {"status": "error", "error_message": "Name and contact are required to save a lead."}

    lead = database.insert_lead(
        client_id=client_id,
        name=name,
        contact=contact,
        message=message,
    )

    return {"status": "success", "lead_id": lead.get("id"), "message": "Lead captured successfully."}


# Export as ADK FunctionTools
search_faqs_tool = FunctionTool(func=search_faqs)
capture_lead_tool = FunctionTool(func=capture_lead)