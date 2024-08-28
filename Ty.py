import tkinter as tk
from tkinter import Label, Toplevel, Text, Scrollbar, VERTICAL
from tkinter import PhotoImage, Menu, messagebox
import time
import re
import random
import pymongo
import bcrypt
# Connect to MongoDB
try:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["typing_speed_db"]
    users_collection = db["users"]
    print("Connected to MongoDB successfully")
except pymongo.errors.ConnectionError as e:
    print(f"Could not connect to MongoDB: {e}")

# Sample list of easy and hard words
easy_words = [
    "apple", "banana", "orange", "grape", "mango", "peach", "plum", "cherry", "pear", "kiwi",
    "melon", "berry", "fig", "lemon", "lime", "apricot", "nectarine", "papaya", "pineapple", "coconut"
]

hard_words = [
    "avocado", "blueberry", "cranberry", "dragonfruit", "elderberry", "gooseberry", "jackfruit",
    "kumquat", "mandarin", "mulberry", "pomegranate", "raspberry", "starfruit", "tangerine", "watermelon",
    "durian", "grapefruit", "honeydew", "mangosteen", "persimmon"
]

class TypingSpeedTest:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Speed Test")
        self.root.geometry("800x400")
        
        self.text = ""
        self.current_index = 0
        self.start_time = None
        self.typing_started = False
        self.num_words = 15  # Default number of words
        self.default_time_limit = 60  # Default time limit in seconds
        self.time_limit = self.default_time_limit  # Current time limit
        self.time_remaining = self.time_limit
        self.timer_running = False  # To track if the timer is running
        self.word_mode = "easy"  # Default mode is easy
        self.email = None
        
        # Initialize username_entry
        self.username_entry = None

        self.create_widgets()
        self.layout_widgets()
        
        self.username_label = tk.Label(self.top_bar, text="", font=("Helvetica", 12), padx=10, bg="#2fc9d0", fg="white")
        self.username_label.pack(side="right")
        
    def create_widgets(self):
        # Top bar
        self.top_bar = tk.Frame(self.root, bg="#2fc9d0", pady=10)
        self.top_bar.pack(fill="x")

        #self.keyboard_image = PhotoImage(file="keyboard.png").subsample(18, 18)  # Resize the image
  # Resize the image
        #self.keyboard_label = tk.Label(self.top_bar, image=self.keyboard_image, padx=10, bg="#2fc9d0")
        #self.keyboard_label.pack(side="left")

        self.interface_label = tk.Label(self.top_bar, text="TYPE SPEED", font=("Helvetica", 18, "bold"), padx=10, bg="#03000a", fg="white")
        self.interface_label.pack(side="left")

        # Timer display
        self.timer_label = tk.Label(self.root, text="", font=("Helvetica", 18), padx=10, bg="#2fc9d0", fg="white")

        # Options bar
        self.options_bar = tk.Frame(self.root, bg="#fff", pady=10)
        self.options_bar.pack(fill="x")

        # Add Beginner and Veteran buttons
        self.beginner_button = tk.Button(self.options_bar, text="Beginner", command=self.set_easy_words, bg="#1a1a1a", fg="white", relief="flat", padx=10, font=("Helvetica", 12, "bold"))
        self.beginner_button.pack(side="left", padx=10)
        self.veteran_button = tk.Button(self.options_bar, text="Veteran", command=self.set_hard_words, bg="#1a1a1a", fg="white", relief="flat", padx=10, font=("Helvetica", 12, "bold"))
        self.veteran_button.pack(side="left", padx=10)
        
        self.logout_button = tk.Button(self.options_bar, text="Log Out", command=self.logout, bg="#1a1a1a", fg="white", relief="flat", padx=10, font=("Helvetica", 12, "bold"))
        self.logout_button.pack(side="right", padx=10)
        self.logout_button.pack_forget()

        self.time_button = tk.Menubutton(self.options_bar, text="Time", bg="#1a1a1a", fg="white", relief="flat", padx=10, font=("Helvetica", 12, "bold"))
        self.time_menu = Menu(self.time_button, tearoff=0)
        self.time_menu.add_command(label="10 sec", command=lambda: self.set_time_limit(10))
        self.time_menu.add_command(label="15 sec", command=lambda: self.set_time_limit(15))
        self.time_menu.add_command(label="30 sec", command=lambda: self.set_time_limit(30))
        self.time_button.config(menu=self.time_menu)
        self.time_button.pack(side="right", padx=10)

        self.punctuations_button = tk.Button(self.options_bar, text="Punctuations", command=self.show_punctuations, bg="#1a1a1a", fg="white", relief="flat", padx=10, font=("Helvetica", 12, "bold"))
        self.punctuations_button.pack(side="right", padx=10)

        self.words_button = tk.Menubutton(self.options_bar, text="Words", bg="#1a1a1a", fg="white", relief="flat", padx=10, font=("Helvetica", 12, "bold"))
        self.words_menu = Menu(self.words_button, tearoff=0)
        self.words_menu.add_command(label="10", command=lambda: self.set_num_words(10))
        self.words_menu.add_command(label="15", command=lambda: self.set_num_words(15))
        self.words_menu.add_command(label="20", command=lambda: self.set_num_words(20))
        self.words_button.config(menu=self.words_menu)
        self.words_button.pack(side="right", padx=10)

        # Login and Sign Up buttons
        self.login_button = tk.Button(self.options_bar, text="Login", command=self.show_login_window, bg="#1a1a1a", fg="white", relief="flat", padx=10, font=("Helvetica", 12, "bold"))
        self.login_button.pack(side="right", padx=10)
        self.signup_button = tk.Button(self.options_bar, text="Sign Up", command=self.show_signup_window, bg="#1a1a1a", fg="white", relief="flat", padx=10, font=("Helvetica", 12, "bold"))
        self.signup_button.pack(side="right", padx=10)

        # Main content
        self.text_frame = tk.Frame(self.root)
        self.text_frame.pack(pady=20)

        self.result_label = tk.Label(self.root, text="", wraplength=750, font=("Helvetica", 14))
        self.result_label.pack(pady=20)

        # Refresh button
        self.refresh_button = tk.Button(self.root, text="Refresh", command=self.refresh_and_hide_timer, bg="#1a1a1a", fg="white", relief="flat", padx=20, pady=10, font=("Helvetica", 12, "bold"))
        self.refresh_button.pack(pady=20)
        
        # history button
        self.history_button = tk.Button(self.options_bar, text="History", command=self.show_history, bg="#1a1a1a", fg="white", relief="flat", padx=10, font=("Helvetica", 12, "bold"))
        self.history_button.pack(side="right", padx=10)
        self.history_button.pack_forget()
    
    def show_history(self):
        # Retrieve the user's typing history from MongoDB
        user_email = self.email  # Assuming the email is stored in self.email after login
        user = users_collection.find_one({"email": user_email})
        if user and "typing_history" in user:
            typing_history = user["typing_history"]
            # Select the last 8 results if there are more than 8, otherwise select all
            past_results = typing_history[-8:]

            # Create a string to display in the Text widget
            display_text = ""
            for i, result in enumerate(past_results, start=1):
                display_text += f"Trial {i}:\n"
                display_text += f"Elapsed Time: {result['elapsed_time']} seconds\nWPM: {result['wpm']:.2f}\nAccuracy: {result['accuracy']:.2f}%\n\n"
            # Create the history window and widgets
            history_window = Toplevel(self.root)
            history_window.title("Typing Test History")
            history_window.geometry("600x400")

            history_label = Label(history_window, text="Typing Test History", font=("Helvetica", 18, "bold"))
            history_label.pack(pady=10)

            history_text = Text(history_window, wrap="word", font=("Helvetica", 12))
            history_text.pack(fill="both", expand=True, padx=10, pady=5)

            scrollbar = Scrollbar(history_window, orient=VERTICAL, command=history_text.yview)
            scrollbar.pack(side="right", fill="y")
            history_text.config(yscrollcommand=scrollbar.set)

        # Insert the display text into the Text widget
            history_text.insert("end", display_text)
            history_text.config(state="disabled")  # Disable editing of the Text widget
        else:
        # If user or typing history not found, display a message
            messagebox.showinfo("Typing Test History", "No typing history found.")
  
    def layout_widgets(self):
        pass
    
    def set_easy_words(self):
        self.word_mode = "easy"
        self.generate_sentence()

    def set_hard_words(self):
        self.word_mode = "hard"
        self.generate_sentence()
    
    def set_num_words(self, num_words):
        self.num_words = num_words
        self.generate_sentence()
        
    def set_time_limit(self, time_limit):
        self.time_limit = time_limit
        self.time_remaining = time_limit
        self.timer_label.config(text=f"Time: {self.time_limit} s" if self.time_limit > 0 else "")
        self.timer_label.pack()  # Ensure the timer label is visible
        self.generate_sentence()  # Generate a new sentence to start fresh

    def refresh_and_hide_timer(self):
        self.time_limit = self.default_time_limit  # Reset time limit to default
        self.time_remaining = self.default_time_limit  # Reset time remaining to default
        self.generate_sentence()  # Generate new sentence
        self.timer_label.pack_forget()  # Hide the timer label

    def generate_sentence(self):
        if self.word_mode == "easy":
            selected_words = random.sample(easy_words, self.num_words)  # Pick easy words
        else:
            selected_words = random.sample(hard_words, self.num_words)  # Pick hard words
        
        self.text = " ".join(selected_words)
        for widget in self.text_frame.winfo_children():
            widget.destroy()
        self.text_display = []

        # Split text into two lines
        words_list = self.text.split()
        mid_point = len(words_list) // 2
        first_line = " ".join(words_list[:mid_point])
        second_line = " ".join(words_list[mid_point:])

        first_line_frame = tk.Frame(self.text_frame)
        first_line_frame.pack()
        second_line_frame = tk.Frame(self.text_frame)
        second_line_frame.pack()

        for char in first_line:
            lbl = tk.Label(first_line_frame, text=char, font=("Helvetica", 18))
            lbl.pack(side=tk.LEFT)
            self.text_display.append(lbl)

        for char in " " + second_line:
            lbl = tk.Label(second_line_frame, text=char, font=("Helvetica", 18))
            lbl.pack(side=tk.LEFT)
            self.text_display.append(lbl)

        self.result_label.config(text="")
        self.start_time = None  # Reset start time
        self.typing_started = False  # Reset typing started flag
        self.current_index = 0  # Reset current index
        self.time_remaining = self.time_limit  # Reset time remaining

        self.root.unbind("<Key>")
        self.root.bind("<Key>", self.start_typing)  # Bind key press event to start typing

    def start_typing(self, event):
        if self.time_limit != 0:  # Check if time limit is set
            if not self.typing_started:
                self.start_time = time.time()  # Start timing
                self.typing_started = True
                if self.time_limit != 0:
                    self.timer_running = True
                    self.update_timer()
            self.check_typing(event)
        else:
            self.check_typing(event)



    def update_timer(self):
        if self.timer_running and self.time_remaining > 0:
            self.time_remaining -= 1
            self.timer_label.config(text=f"Time: {self.time_remaining} s")
            self.root.after(1000, self.update_timer)
        elif self.time_remaining == 0:
            self.timer_running = False
            self.end_test()
            if self.time_limit != 0:
                messagebox.showinfo("Time's Up!", "Maximum time limit reached.")
                self.generate_sentence()  # Generate a new sentence after closing the popup

    def check_typing(self, event):
        if self.current_index < len(self.text):
            char = event.char
            if event.keysym in ["Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R"]:
                return  # Ignore modifier keys

            if event.keysym == "BackSpace":
                if self.current_index > 0:
                    self.current_index -= 1
                    self.text_display[self.current_index].config(fg="black")
            elif event.keysym == "space":
                while self.current_index < len(self.text) and self.text[self.current_index] != " ":
                    self.text_display[self.current_index].config(fg="red")
                    self.current_index += 1
                if self.current_index < len(self.text) and self.text[self.current_index] == " ":
                    self.text_display[self.current_index].config(fg="black")
                    self.current_index += 1
            else:
                if char == self.text[self.current_index]:
                    self.text_display[self.current_index].config(fg="green")
                else:
                    self.text_display[self.current_index].config(fg="red")
                self.current_index += 1
            if self.current_index == len(self.text):
                self.end_test()

    def end_test(self):
        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            self.calculate_results(elapsed_time)
        self.root.unbind("<Key>")  # Unbind the key press event to stop typing

    def calculate_results(self, elapsed_time):
        correct_chars = sum(1 for lbl in self.text_display if lbl.cget("foreground") == "green")
        total_chars = len(self.text.replace(" ", ""))  # Exclude spaces from total character count
        accuracy = correct_chars / total_chars * 100

        words_typed = len(self.text.split())
        correct_words_typed = sum(1 for word in self.text.split() if all(lbl.cget("foreground") == "green" for lbl in self.text_display[self.text.index(word):self.text.index(word) + len(word)]))
        wpm = correct_words_typed / (elapsed_time / 60)

        # Get user's email
        email = self.email  # Assuming email is obtained during login/signup

        # Store typing test results in the database
        self.store_typing_test_result(email, elapsed_time, wpm, accuracy)

        # Display results
        self.result_label.config(text=f"Time: {elapsed_time:.2f} seconds\nWPM: {wpm:.2f}\nAccuracy: {accuracy:.2f}%")

    def store_typing_test_result(self, email, elapsed_time, wpm, accuracy):
        try:
            user = users_collection.find_one({"email": email})

        # If the user exists, update the typing history
            if user:
                typing_history = user.get("typing_history", [])
                typing_history.append({"elapsed_time": elapsed_time, "wpm": wpm, "accuracy": accuracy})

            # Keep only the last 15 typings
                typing_history = typing_history[-15:]

            # Update the user document with the updated typing history
                users_collection.update_one({"email": email}, {"$set": {"typing_history": typing_history}})
            else:
            # If the user does not exist, create a new user document with the typing history
                users_collection.insert_one({"email": email, "typing_history": [{"elapsed_time": elapsed_time, "wpm": wpm, "accuracy": accuracy}]})
        except pymongo.errors.PyMongoError as e:
            print(f"Error storing typing test result: {e}")


    def show_punctuations(self):
        punctuation_sentences = [
            "Hello, world!", "Good morning! How are you?", "Python is fun; let's code.",
            "It's a beautiful day.", "Are you ready? Let's go!", "Coding: an essential skill.",
            "Wait... What just happened?", "Success is not final, failure is not fatal.",
            "Keep going, you're doing great!", "Practice makes perfect: keep typing."
        ]
        self.text = random.choice(punctuation_sentences)
        for widget in self.text_frame.winfo_children():
            widget.destroy()
        self.text_display = []

        first_line_frame = tk.Frame(self.text_frame)
        first_line_frame.pack()
        second_line_frame = tk.Frame(self.text_frame)
        second_line_frame.pack()

        mid_point = len(self.text) // 2
        first_line = self.text[:mid_point]
        second_line = self.text[mid_point:]

        for char in first_line:
            lbl = tk.Label(first_line_frame, text=char, font=("Helvetica", 18))
            lbl.pack(side=tk.LEFT)
            self.text_display.append(lbl)

        for char in second_line:
            lbl = tk.Label(second_line_frame, text=char, font=("Helvetica", 18))
            lbl.pack(side=tk.LEFT)
            self.text_display.append(lbl)

        self.result_label.config(text="")
        self.start_time = None
        self.typing_started = False
        self.current_index = 0
        self.time_remaining = self.time_limit
        self.timer_label.config(text=f"Time: {self.time_limit} s" if self.time_limit > 0 else "")
        
        self.root.unbind("<Key>")
        self.root.bind("<Key>", self.start_typing)  # Bind key press event to start typing

    
    def show_signup_window(self):
        signup_window = tk.Toplevel(self.root)
        signup_window.title("Sign Up")

        email_label = tk.Label(signup_window, text="Email:")
        email_label.grid(row=0, column=0, padx=10, pady=5)
        self.email_entry = tk.Entry(signup_window)
        self.email_entry.grid(row=0, column=1, padx=10, pady=5)

        password_label = tk.Label(signup_window, text="Password:")
        password_label.grid(row=1, column=0, padx=10, pady=5)
        password_entry = tk.Entry(signup_window, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=5)

        signup_button = tk.Button(signup_window, text="Sign Up", command=lambda: self.perform_signup(self.email_entry.get(), password_entry.get(), signup_window))
        signup_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5)



    def show_login_window(self):
        login_window = tk.Toplevel(self.root)
        login_window.title("Login")

        username_label = tk.Label(login_window, text="Name:")
        username_label.grid(row=0, column=0, padx=10, pady=5)
        self.username_entry = tk.Entry(login_window)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)

        email_label = tk.Label(login_window, text="Email:")
        email_label.grid(row=1, column=0, padx=10, pady=5)
        self.email_entry = tk.Entry(login_window)
        self.email_entry.grid(row=1, column=1, padx=10, pady=5)

        password_label = tk.Label(login_window, text="Password:")
        password_label.grid(row=2, column=0, padx=10, pady=5)
        self.password_entry = tk.Entry(login_window, show="*")
        self.password_entry.grid(row=2, column=1, padx=10, pady=5)

        login_button = tk.Button(login_window, text="Login", command=lambda: self.perform_login(self.username_entry.get(), self.email_entry.get(), self.password_entry.get(), login_window))
        login_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

    def perform_signup(self, email, password, signup_window):
        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error", "Invalid email address. Please enter a valid email.")
            return
        # Check if the user already exists in the database
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            # If the user exists, prompt them to sign up again
            if bcrypt.checkpw(password.encode('utf-8'), existing_user['password']):
                signup_window.destroy()
                self.email = email
                messagebox.showinfo("Login", "Login successful!")
                self.logout_button.pack(side="right", padx=10)
                self.history_button.pack(side="right", padx=10)
            else:
                messagebox.showerror("Login", "Incorrect password. Please try again.")
        else:
            # If the user doesn't exist, allow them to sign up
            signup_window.destroy()
            messagebox.showinfo("Signup", "Account does not exist..! u should login")

    def perform_login(self, name, email, password, login_window):
        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showerror("Error", "Invalid email address. Please enter a valid email.")
            return
        
        # Check if the user exists in the database
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            # If the user exists, inform them that they need to sign up again
            messagebox.showinfo("Login", "User already exists. Please sign up .")
        else:
            # If the user doesn't exist, allow them to log in
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            users_collection.insert_one({"name": name, "email": email, "password": hashed_password})
            login_window.destroy()
            self.email = email
            messagebox.showinfo("Login", "Account created successfully..!")
            self.logout_button.pack(side="right", padx=10)
            self.history_button.pack(side="right", padx=10)
            self.username_label.config(text=name)

    
    def logout(self):
        self.logout_button.pack_forget() # Hide the log out button
        self.history_button.pack_forget()
        self.username_label.config(text="")  # Clear the username label
        self.username_entry = None
        self.email = None
        messagebox.showinfo("Logout", "You have been logged out successfully.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TypingSpeedTest(root)
    app.generate_sentence()
    root.mainloop()