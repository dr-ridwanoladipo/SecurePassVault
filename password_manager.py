import streamlit as st
import random
import string
import pyperclip
import json
import os
from cryptography.fernet import Fernet

# Set page config for a wider layout
st.set_page_config(page_title="Secure Password Manager", layout="wide")

# Custom CSS for a more attractive interface
st.markdown("""
<style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        padding: 10px 20px;
    }
    .stTextInput>div>div>input {
        background-color: #f0f0f0;
        border-radius: 5px;
        border: 1px solid #ddd;
        padding: 10px;
    }
    .stAlert {
        background-color: #d4edda;
        color: #155724;
        border-color: #c3e6cb;
        border-radius: 5px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'key' not in st.session_state:
    st.session_state.key = Fernet.generate_key()
    st.session_state.cipher_suite = Fernet(st.session_state.key)


# Encryption and decryption functions
def encrypt(text):
    return st.session_state.cipher_suite.encrypt(text.encode()).decode()


def decrypt(text):
    return st.session_state.cipher_suite.decrypt(text.encode()).decode()


# Password generation function
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))


# Save password function
def save_password(website, email, password):
    data = load_data()
    data[website] = {"email": email, "password": encrypt(password)}
    with open("passwords.json", "w") as file:
        json.dump(data, file)
    st.success("Password saved successfully!")


# Load data function
def load_data():
    if not os.path.exists("passwords.json"):
        return {}
    with open("passwords.json", "r") as file:
        return json.load(file)


# Main app
def main():
    st.title("🔐 Secure Password Manager")

    tab1, tab2 = st.tabs(["Add/Update Password", "Find Password"])

    with tab1:
        st.header("Add or Update Password")
        website = st.text_input("Website")
        email = st.text_input("Email/Username")
        password = st.text_input("Password", type="password")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate Password"):
                generated_password = generate_password()
                st.session_state.generated_password = generated_password
                st.code(generated_password)
                pyperclip.copy(generated_password)
                st.info("Password copied to clipboard!")

        with col2:
            if st.button("Save Password"):
                if website and email and password:
                    save_password(website, email, password)
                else:
                    st.warning("Please fill in all fields.")

    with tab2:
        st.header("Find Password")
        search_website = st.text_input("Enter website to search")
        if st.button("Search"):
            data = load_data()
            if search_website in data:
                email = data[search_website]["email"]
                password = decrypt(data[search_website]["password"])
                st.success(f"Website: {search_website}")
                st.info(f"Email: {email}")
                st.info(f"Password: {password}")
                if st.button("Copy Password"):
                    pyperclip.copy(password)
                    st.info("Password copied to clipboard!")
            else:
                st.error("Website not found in the database.")


if __name__ == "__main__":
    main()