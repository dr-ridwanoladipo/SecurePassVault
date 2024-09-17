import streamlit as st
import random
import string
import json
import os
import base64
from cryptography.fernet import Fernet
import hashlib

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

# Hash function for security key
def hash_security_key(security_key):
    return hashlib.sha256(security_key.encode()).hexdigest()

# Initialize session state
if 'cipher_suite' not in st.session_state:
    if 'security_key_hash' not in st.session_state and os.path.exists("security_key_hash.txt"):
        with open("security_key_hash.txt", "r") as file:
            st.session_state.security_key_hash = file.read().strip()

    if 'security_key_hash' in st.session_state:
        # Use the security key hash to generate a consistent encryption key
        encryption_key = hashlib.sha256(st.session_state.security_key_hash.encode()).digest()
        st.session_state.cipher_suite = Fernet(base64.urlsafe_b64encode(encryption_key))
    else:
        st.warning("Please set up your security key first.")

if 'clear_inputs' not in st.session_state:
    st.session_state.clear_inputs = False

if 'generated_password' not in st.session_state:
    st.session_state.generated_password = ""

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
def save_password(website, email, password, security_key):
    data = load_data()
    if website.lower() not in data:
        data[website.lower()] = []
    data[website.lower()].append({"email": email, "password": encrypt(password)})
    with open("passwords.json", "w") as file:
        json.dump(data, file, indent=4)
    st.success("Password saved successfully!")
    st.session_state.clear_inputs = True

# Load data function
def load_data():
    if not os.path.exists("passwords.json"):
        return {}
    with open("passwords.json", "r") as file:
        return json.load(file)

# Delete entry function
def delete_entry(website, index):
    data = load_data()
    if website.lower() in data:
        if 0 <= index < len(data[website.lower()]):
            del data[website.lower()][index]
            if not data[website.lower()]:
                del data[website.lower()]
            with open("passwords.json", "w") as file:
                json.dump(data, file)
            return True
    return False

# Main app
def main():
    st.title("🔐 Secure Password Manager")

    security_key = st.sidebar.text_input("Enter your security key", type="password")

    if security_key:
        new_security_key_hash = hash_security_key(security_key)
        if 'security_key_hash' not in st.session_state:
            st.session_state.security_key_hash = new_security_key_hash
            with open("security_key_hash.txt", "w") as file:
                file.write(st.session_state.security_key_hash)
            # Initialize cipher suite with the new security key
            encryption_key = hashlib.sha256(st.session_state.security_key_hash.encode()).digest()
            st.session_state.cipher_suite = Fernet(base64.urlsafe_b64encode(encryption_key))
        elif new_security_key_hash != st.session_state.security_key_hash:
            st.error("Incorrect security key! Please enter the correct one.")
            return

    tab1, tab2, tab3 = st.tabs(["Add/Update Password", "Find Password", "Delete Entry"])

    with tab1:
        st.header("Add or Update Password")

        # Clear inputs if flag is set
        if st.session_state.clear_inputs:
            st.session_state.website = ""
            st.session_state.email = ""
            st.session_state.generated_password = ""
            st.session_state.clear_inputs = False

        website = st.text_input("Website", key="website", value=st.session_state.get('website', ''))
        email = st.text_input("Email/Username", key="email", value=st.session_state.get('email', ''))
        password = st.text_input("Password", type="password", key="password",
                                 value=st.session_state.get('generated_password', ''))

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Generate Password"):
                generated_password = generate_password()
                st.session_state.generated_password = generated_password
                st.code(generated_password)
                st.info("Password generated. Please copy it manually.")

        with col2:
            if st.button("Save Password"):
                if website and email and password and security_key:
                    save_password(website, email, password, security_key)
                else:
                    st.warning("Please fill in all fields including the security key.")

    with tab2:
        st.header("Find Password")
        search_website = st.text_input("Enter website to search")

        if 'search_clicked' not in st.session_state:
            st.session_state.search_clicked = False

        if st.button("Search", key="search_button"):
            st.session_state.search_clicked = True

        if st.session_state.search_clicked:
            if security_key:
                data = load_data()
                if search_website.lower() in data:
                    st.success(f"Website: {search_website}")
                    for i, entry in enumerate(data[search_website.lower()]):
                        email = entry["email"]
                        try:
                            password = decrypt(entry["password"])
                        except:
                            st.error(
                                f"Error decrypting password for entry {i + 1}. It may have been encrypted with a different key.")
                            continue

                        st.info(f"Entry {i + 1}:")
                        st.info(f"Email: {email}")
                        st.info(f"Password: {password}")
                else:
                    st.error("Website not found in the database.")
            else:
                st.warning("Please enter your security key to search.")

    with tab3:
        st.header("Delete Entry")
        delete_website = st.text_input("Enter website to delete")

        if 'delete_search_clicked' not in st.session_state:
            st.session_state.delete_search_clicked = False

        if st.button("Search for Deletion", key="delete_search_button"):
            st.session_state.delete_search_clicked = True

        if st.session_state.delete_search_clicked:
            if security_key:
                data = load_data()
                if delete_website.lower() in data:
                    st.success(f"Website: {delete_website}")
                    for i, entry in enumerate(data[delete_website.lower()]):
                        st.info(f"Entry {i + 1}:")
                        st.info(f"Email: {entry['email']}")
                        if st.button(f"Delete Entry {i + 1}", key=f"delete_{delete_website}_{i}"):
                            if delete_entry(delete_website, i):
                                st.session_state.delete_success = f"Entry {i + 1} for {delete_website} deleted successfully!"
                                st.session_state.delete_search_clicked = False
                                st.rerun()
                else:
                    st.error("Website not found in the database.")
            else:
                st.warning("Please enter your security key to delete entries.")

        if st.session_state.get('delete_success'):
            st.success(st.session_state.delete_success)
            del st.session_state.delete_success

if __name__ == "__main__":
    main()