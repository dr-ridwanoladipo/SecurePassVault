from tkinter import *
from tkinter import messagebox
from random import randint, choice, shuffle
import pyperclip
import json


# ---------------------------- PASSWORD GENERATOR ------------------------------- #


def generate_password():
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
               'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
               'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    password_letters = [choice(letters) for _ in range(randint(4, 7))]
    password_symbols = [choice(symbols) for _ in range(randint(2, 4))]
    password_numbers = [choice(numbers) for _ in range(randint(2, 4))]

    password_list = password_letters + password_symbols + password_numbers
    shuffle(password_list)

    password = "".join(password_list)
    password_entry.insert(0, password)
    pyperclip.copy(password)


# ---------------------------- ENCRYPT PASSWORD ------------------------------- #

def caesar(start_text, shift_amount, cipher_direction):
    alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
                'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
                'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y',
                'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '#', '$', '%', '&', '(',
                ')', '*', '+', '@', '^', '-', '_', '=', '>', '<', '{', '}', '/', '?', '.']
    end_text = ""

    if cipher_direction == "decode":
        shift_amount *= -1
    # for letter in start_text:
    for char in start_text:  # not only letter
        position = alphabet.index(char)
        new_position = (position + shift_amount) % len(alphabet)
        end_text += alphabet[new_position]
    return end_text


# ---------------------------- SAVE PASSWORD ------------------------------- #

def save():
    website = website_entry.get().capitalize().strip()
    email = email_entry.get().strip()
    password = password_entry.get().strip()
    cipher = caesar_entry.get()

    if len(website) == 0 or len(password) == 0 or len(cipher) == 0:
        messagebox.showinfo(title="Oops", message="Please make sure you haven't left any field empty.")
    else:
        cipher_int = int(caesar_entry.get())
        password = caesar(password, cipher_int, "encode")

        new_data = {
            website: {
                "email": email,
                "password": password,
            }
        }

        try:
            with open("data.json", "r") as data_file:
                # Reading old data
                data = json.load(data_file)
        except FileNotFoundError:
            with open("data.json", "w") as data_file:
                json.dump(new_data, data_file, indent=4)
        else:
            # Updating old data with new data
            data.update(new_data)

            with open("data.json", "w") as data_file:
                # Saving updated data
                json.dump(data, data_file, indent=4)
        finally:
            website_entry.delete(0, END)
            password_entry.delete(0, END)
            caesar_entry.delete(0, END)


# ---------------------------- FIND PASSWORD ------------------------------- #

def find_password():
    website = website_entry.get().capitalize()
    cipher = caesar_entry.get()

    if len(cipher) == 0:
        messagebox.showinfo(title="Oops", message="Please enter your security code correctly.")
    else:
        try:
            with open("data.json", "r") as data_file:
                data = json.load(data_file)
        except FileNotFoundError:
            messagebox.showinfo(title="Error", message="No Data File Found.")
        else:
            if website in data:
                email = data[website]["email"]
                password = data[website]["password"]

                cipher_int = int(caesar_entry.get())

                password = caesar(password, cipher_int, "decode")
                messagebox.showinfo(title=website, message=f"Email: {email}\nPassword: {password}")
                pyperclip.copy(password)
                caesar_entry.delete(0, END)
            else:
                messagebox.showinfo(title="Error", message=f"No details for {website} exists.")


# ---------------------------- UI SETUP ------------------------------- #

import os
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# UI SETUP
window = Tk()
window.title("Password Manager")
window.config(padx=60, pady=60)

canvas = Canvas(height=200, width=200)
logo_img = PhotoImage(file=resource_path("logo.png"))
canvas.create_image(100, 100, image=logo_img)
canvas.grid(row=0, column=0, columnspan=3) # Adjusted column span for logo

# Labels
website_label = Label(text="Website:")
website_label.grid(row=1, column=0)

email_label = Label(text="Email/Username:")
email_label.grid(row=2, column=0)

password_label = Label(text="Password:")
password_label.grid(row=3, column=0)

caesar_label = Label(text="Security Code:")
caesar_label.grid(row=4, column=0)

# Entries
website_entry = Entry(width=31)
website_entry.grid(row=1, column=1)
website_entry.focus()

email_entry = Entry(width=50)
email_entry.grid(row=2, column=1, columnspan=2)
email_entry.insert(0, "@gmail.com")

password_entry = Entry(width=31)
password_entry.grid(row=3, column=1)

caesar_entry = Entry(width=31)
caesar_entry.grid(row=4, column=1)

# Buttons
search_button = Button(text="Search", width=15, command=find_password, bd=1, relief="ridge")
search_button.grid(row=1, column=2)

generate_password_button = Button(text="Generate Password", width=15, command=generate_password, bd=1, relief="ridge")
generate_password_button.grid(row=3, column=2)  # Align to the west (left)

add_button = Button(text="Add", width=15, command=save, bd=1, relief="ridge")
# add_button = Button(text="Add", width=42, command=save, bd=1, relief="ridge")
# add_button.grid(row=4, column=1, columnspan=2)
add_button.grid(row=4, column=2)

window.mainloop()

