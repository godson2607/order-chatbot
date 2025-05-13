import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv

import os

# ------------------------------
# 🔐 Set your OpenAI API Key
# ------------------------------
load_dotenv()

# ------------------------------
# 🧠 Grocery Items (editable)
# ------------------------------
GROCERY_ITEMS = [
    "rice", "wheat", "sugar", "salt", "milk", "bread", "eggs", "onions", "potatoes", "tomatoes",
    "oil", "butter", "cheese", "yogurt", "tea", "coffee", "soap", "shampoo", "toothpaste"
]

# ------------------------------
# 🔧 LangChain LLM Setup
# ------------------------------
llm = ChatOpenAI( model="gpt-3.5-turbo")

# ------------------------------
# 📦 Streamlit UI Setup
# ------------------------------
st.set_page_config(page_title="🛒 Grocery Shop Chatbot", page_icon="🛍️")
st.title("🛍️ Grocery Shop Chatbot")

# ------------------------------
# 💾 Initialize Session State
# ------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "text": "Welcome to FreshMart! 🛒 What groceries do you need today?"}
    ]
if "cart" not in st.session_state:
    st.session_state.cart = []

# ------------------------------
# 📜 Display Chat History
# ------------------------------
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["text"])

# ------------------------------
# 📤 LLM Order Parsing Function
# ------------------------------
def extract_grocery_items(user_input):
    system_prompt = (
        f"You are a helpful grocery assistant. Extract grocery items and their quantities from user messages.\n"
        f"Valid items: {', '.join(GROCERY_ITEMS)}\n"
        f"Reply ONLY with a JSON list like this:\n"
        f'[{{"item": "rice", "quantity": "2 kg"}}, {{"item": "eggs", "quantity": "1 dozen"}}]'
    )
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_input)
    ]
    response = llm(messages).content
    try:
        parsed = eval(response)
        # Validate items
        parsed = [entry for entry in parsed if entry["item"] in GROCERY_ITEMS]
        return parsed
    except Exception as e:
        return []

# ------------------------------
# 🗨️ Chat Input Handler
# ------------------------------
user_input = st.chat_input("Enter your grocery list...")

if user_input:
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "text": user_input})

    items = extract_grocery_items(user_input)

    if items:
        st.session_state.cart.extend(items)
        response = f"🧺 Added to cart: " + ", ".join(f'{i["quantity"]} {i["item"]}' for i in items)
    else:
        response = "❌ Sorry, I couldn't understand. Please use common grocery terms."

    st.chat_message("assistant").write(response)
    st.session_state.messages.append({"role": "assistant", "text": response})

# ------------------------------
# 🧾 Sidebar Cart Summary
# ------------------------------
if st.session_state.cart:
    st.sidebar.header("🧾 Your Grocery Cart")
    for entry in st.session_state.cart:
        st.sidebar.write(f'{entry["item"].title()}: {entry["quantity"]}')
    
    if st.sidebar.button("✅ Confirm Order"):
        st.sidebar.success("Order placed! 🛒 Thank you.")
        st.session_state.messages.append({"role": "assistant", "text": "Your order has been confirmed! ✅"})
        st.session_state.cart = []
