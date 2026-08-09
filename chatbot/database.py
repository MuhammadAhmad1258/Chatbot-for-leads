"""
database.py
Handles all Supabase connections and queries for the FAQ Agent.
tools.py will import functions from here instead of using in-memory placeholders.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL or SUPABASE_KEY missing. Check your .env file."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================
# FAQ functions
# ============================================

def get_all_faqs(client_id: str = "demo_client"):
    """
    Fetch all FAQ question-answer pairs for a given client.
    Returns a list of dicts: [{"question": ..., "answer": ...}, ...]
    """
    response = (
        supabase.table("faqs")
        .select("question, answer")
        .eq("client_id", client_id)
        .execute()
    )
    return response.data


def search_faqs(client_id: str, query: str):
    """
    Search FAQs for a client matching a specific query.
    Performs keyword matching and falls back to returning all FAQs if no match is found.
    """
    faqs = get_all_faqs(client_id)
    if not query:
        return faqs

    query_words = set(query.lower().split())
    matched_faqs = []
    for faq in faqs:
        question = faq.get("question", "").lower()
        if any(word in question for word in query_words) or query.lower() in question or question in query.lower():
            matched_faqs.append(faq)
            
    return matched_faqs if matched_faqs else faqs


# ============================================
# Lead functions
# ============================================

def save_lead(name: str, phone: str, requirement: str, client_id: str = "demo_client"):
    """
    Insert a new lead into the leads table.
    Returns the inserted row (as a list with one dict) on success.
    """
    response = (
        supabase.table("leads")
        .insert({
            "client_id": client_id,
            "name": name,
            "phone": phone,
            "requirement": requirement,
        })
        .execute()
    )
    return response.data


def insert_lead(client_id: str, name: str, contact: str, message: str):
    """
    Insert a new lead, mapping 'contact' and 'message' to 'phone' and 'requirement',
    returning the single inserted record dictionary.
    """
    data = save_lead(name=name, phone=contact, requirement=message, client_id=client_id)
    return data[0] if data else {}


def get_all_leads(client_id: str = "demo_client"):
    """
    Fetch all leads for a given client (useful for testing/verification).
    """
    response = (
        supabase.table("leads")
        .select("*")
        .eq("client_id", client_id)
        .execute()
    )
    return response.data