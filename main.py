import tkinter as tk
from tkinter import messagebox
from random import randint, choice, shuffle
import pyperclip
import json
import os
import sys


# ---------------------------- PASSWORD GENERATOR ------------------------------- #

def generate_password():
    """Generate a random password and insert it into the password entry field."""
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
               'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
               'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    password_list = [choice(letters) for _ in range(randint(4, 7))] + \
                    [choice(symbols) for _ in range(randint(2, 4))] + \
                    [choice(numbers) for _ in range(randint(2, 4))]

    shuffle(password_list)
    password = "".join(password_list)

    password_entry.delete(0, tk.END)
    password_entry.insert(0, password)
    pyperclip.copy(password)


# ---------------------------- ENCRYPT PASSWORD ------------------------------- #

def caesar(start_text, shift_amount, cipher_direction):
    """Encrypt or decrypt text using Caesar cipher."""
    alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
                'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
                'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '#', '$', '%', '&', '(',
                ')', '*', '+', '@', '^', '-', '_', '=', '>', '<', '{', '}', '/', '?', '.']

    shift_amount *= -1 if cipher_direction == "decode" else 1
    return ''.join(alphabet[(alphabet.index(char) + shift_amount) % len(alphabet)] for char in start_text)


# ---------------------------- SAVE PASSWORD ------------------------------- #

def save():
    """Save the entered website, email, and encrypted password to a JSON file."""
    website = website_entry.get().capitalize().strip()
    email = email_entry.get().strip()
    password = password_entry.get().strip()
    cipher = caesar_entry.get()

    if not all([website, password, cipher]):
        messagebox.showinfo(title="Oops", message="Please make sure you haven't left any field empty.")
        return

    password = caesar(password, int(cipher), "encode")

    new_data = {
        website: {
            "email": email,
            "password": password,
        }
    }

    try:
        with open("data.json", "r") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        data = new_data
    else:
        data.update(new_data)

    with open("data.json", "w") as data_file:
        json.dump(data, data_file, indent=4)

    website_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    caesar_entry.delete(0, tk.END)


# ---------------------------- FIND PASSWORD ------------------------------- #

def find_password():
    """Retrieve and decrypt the password for a given website."""
    website = website_entry.get().capitalize()
    cipher = caesar_entry.get()

    if not cipher:
        messagebox.showinfo(title="Oops", message="Please enter your security code correctly.")
        return

    try:
        with open("data.json", "r") as data_file:
            data = json.load(data_file)
    except FileNotFoundError:
        messagebox.showinfo(title="Error", message="No Data File Found.")
    else:
        if website in data:
            email = data[website]["email"]
            password = caesar(data[website]["password"], int(cipher), "decode")
            messagebox.showinfo(title=website, message=f"Email: {email}\nPassword: {password}")
            pyperclip.copy(password)
            caesar_entry.delete(0, tk.END)
        else:
            messagebox.showinfo(title="Error", message=f"No details for {website} exists.")


# ---------------------------- UI SETUP ------------------------------- #

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# Main window setup
window = tk.Tk()
window.title("Password Manager")
window.config(padx=60, pady=60)

# UI Components
canvas = tk.Canvas(height=200, width=200)
logo_img = tk.PhotoImage(file=resource_path("logo.png"))
canvas.create_image(100, 100, image=logo_img)
canvas.grid(row=0, column=0, columnspan=3)

# Labels
labels = [
    ("Website:", 1), ("Email/Username:", 2),
    ("Password:", 3), ("Security Code:", 4)
]
for text, row in labels:
    tk.Label(text=text).grid(row=row, column=0)

# Entries
website_entry = tk.Entry(width=31)
website_entry.grid(row=1, column=1)
website_entry.focus()

email_entry = tk.Entry(width=50)
email_entry.grid(row=2, column=1, columnspan=2)
email_entry.insert(0, "@gmail.com")

password_entry = tk.Entry(width=31)
password_entry.grid(row=3, column=1)

caesar_entry = tk.Entry(width=31)
caesar_entry.grid(row=4, column=1)

# Buttons
search_button = tk.Button(text="Search", width=15, command=find_password, bd=1, relief="ridge")
search_button.grid(row=1, column=2)

generate_password_button = tk.Button(text="Generate Password", width=15, command=generate_password, bd=1,
                                     relief="ridge")
generate_password_button.grid(row=3, column=2)

add_button = tk.Button(text="Add", width=15, command=save, bd=1, relief="ridge")
add_button.grid(row=4, column=2)

window.mainloop()