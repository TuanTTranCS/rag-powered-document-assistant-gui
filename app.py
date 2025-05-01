import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from deployment.agent import rag_agent as agent_engine
import json
import os
import re
import ctypes

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Reminder")
        root.iconbitmap("./images/app_icon_32.ico")
        # Initialize threads and current thread
        self.threads = {}
        self.current_thread = None

        # Define thread directory
        self.thread_dir = "thread_history"
        if not os.path.exists(self.thread_dir):
            os.makedirs(self.thread_dir)

        # Adjust layout to move threads to the left
        thread_label = tk.Label(root, text="Threads", font=("Arial", 12, "bold"))
        thread_label.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        thread_frame = tk.Frame(root)
        thread_frame.grid(row=1, column=0, rowspan=5, padx=10, pady=5, sticky="ns")

        thread_scrollbar = ttk.Scrollbar(thread_frame, orient="vertical")
        thread_scrollbar_horizontal = ttk.Scrollbar(thread_frame, orient="horizontal")

        self.thread_list = tk.Listbox(thread_frame, height=20, width=30, 
                                      yscrollcommand=thread_scrollbar.set, 
                                      xscrollcommand=thread_scrollbar_horizontal.set)

        thread_scrollbar.config(command=self.thread_list.yview)
        thread_scrollbar_horizontal.config(command=self.thread_list.xview)

        self.thread_list.grid(row=0, column=0, sticky="nsew")
        thread_scrollbar.grid(row=0, column=1, sticky="ns")
        thread_scrollbar_horizontal.grid(row=1, column=0, sticky="ew")

        self.thread_list.bind("<Button-1>", self.select_thread)

        thread_frame.grid_rowconfigure(0, weight=1)
        thread_frame.grid_columnconfigure(0, weight=1)

        button_frame = tk.Frame(root)
        button_frame.grid(row=6, column=0, padx=10, pady=10, sticky="w")
        self.delete_button = tk.Button(button_frame, text="Delete Thread", command=self.delete_thread)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        self.new_thread_button = tk.Button(button_frame, text="New Thread", command=self.create_new_thread)
        self.new_thread_button.pack(side=tk.LEFT, padx=5)

        chat_label = tk.Label(root, text="Chat History", font=("Arial", 12, "bold"))
        chat_label.grid(row=0, column=1, columnspan=2, padx=10, pady=(10, 0), sticky="w")

        chat_frame = tk.Frame(root)
        chat_frame.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="nsew")
        self.chat_display = tk.Text(chat_frame, state="disabled", wrap="word", height=20, width=50)
        chat_scrollbar = ttk.Scrollbar(chat_frame, command=self.chat_display.yview)
        self.chat_display.configure(yscrollcommand=chat_scrollbar.set)
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        input_label = tk.Label(root, text="Message Input", font=("Arial", 12, "bold"))
        input_label.grid(row=2, column=1, columnspan=2, padx=10, pady=(10, 0), sticky="w")

        self.user_input = tk.Text(root, height=2, width=50, wrap="word")
        self.user_input.grid(row=3, column=1, padx=10, pady=5, sticky="we")
        user_input_scrollbar = ttk.Scrollbar(root, command=self.user_input.yview)
        self.user_input.configure(yscrollcommand=user_input_scrollbar.set)
        user_input_scrollbar.grid(row=3, column=2, sticky="ns")
        self.user_input.bind("<Return>", self.send_message)

        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.grid(row=3, column=3, padx=10, pady=5, sticky="w")

        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(1, weight=1)

        # Load threads from local JSON files
        self.load_threads()
        self.update_thread_list()

    def load_threads(self):
        for file_name in os.listdir(self.thread_dir):
            if file_name.endswith(".json"):
                with open(os.path.join(self.thread_dir, file_name), "r") as file:
                    thread_data = json.load(file)
                    self.threads[file_name[:-5]] = thread_data

    def sanitize_filename(self, title):
        return re.sub(r'[\\/:*?"<>|]', '_', title)

    def save_thread(self, thread_title):
        sanitized_title = self.sanitize_filename(thread_title)
        with open(os.path.join(self.thread_dir, f"{sanitized_title}.json"), "w") as file:
            json.dump(self.threads[thread_title], file, indent=4)

    def send_message(self, event=None):
        user_message = self.user_input.get("1.0", tk.END).strip()
        if not user_message:
            messagebox.showerror("Error", "Message cannot be empty.")
            return

        self.user_input.delete("1.0", tk.END)
        self.display_message("user", user_message)

        try:
            session = {"id": "default_session"}  # Define or fetch the session object
            response = self.query_agent(user_message, session)
            self.display_message("agent", response)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get response: {e}")

    def query_agent(self, message, session):
        # Simulate querying the agent engine
        for event in agent_engine.stream_query(
            message=message,
        ):
            agent_engine.pretty_print_event(event)
            return agent_engine.get_agent_text_from_event(event)

    def display_message(self, author, message):
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, f"[{author}]: {message}\n")
        self.chat_display.config(state="disabled")

        # Save message to current thread
        if not self.current_thread:
            self.current_thread = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.threads[self.current_thread] = []
        self.threads[self.current_thread].append({"author": author, "message": message})

        # Update thread list
        self.update_thread_list()

        # Save the current thread to a JSON file
        self.save_thread(self.current_thread)

    def update_thread_list(self):
        self.thread_list.delete(0, tk.END)
        for thread, messages in sorted(self.threads.items()):
            first_message = messages[0]['message'][:50] if messages else "No messages"
            display_name = f"{thread} - {first_message}"
            self.thread_list.insert(tk.END, display_name)

    def select_thread(self, event):
        selected = self.thread_list.curselection()
        if not selected:
            return

        # Save the current thread before switching
        if self.current_thread:
            self.save_thread(self.current_thread)

        thread_display_name = self.thread_list.get(selected[0])
        thread_title = thread_display_name.split(' - ')[0]

        # Ensure the thread exists in memory before switching
        if thread_title not in self.threads:
            messagebox.showerror("Error", f"Thread '{thread_title}' not found.")
            return

        self.current_thread = thread_title
        self.chat_display.config(state="normal")
        self.chat_display.delete(1.0, tk.END)
        for message in self.threads[thread_title]:
            self.chat_display.insert(tk.END, f"[{message['author']}]: {message['message']}\n")
        self.chat_display.config(state="disabled")

    def create_new_thread(self):
        # Save the current thread before creating a new one
        if self.current_thread:
            self.save_thread(self.current_thread)

        new_thread_title = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_thread = new_thread_title
        self.threads[new_thread_title] = []
        self.chat_display.config(state="normal")
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state="disabled")
        self.update_thread_list()

    def delete_thread(self):
        selected = self.thread_list.curselection()
        if not selected:
            messagebox.showerror("Error", "No thread selected.")
            return

        thread_title = self.thread_list.get(selected[0])
        del self.threads[thread_title]
        self.current_thread = None
        self.chat_display.config(state="normal")
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state="disabled")
        self.update_thread_list()

        # Delete the corresponding JSON file
        sanitized_title = self.sanitize_filename(thread_title)
        os.remove(os.path.join(self.thread_dir, f"{sanitized_title}.json"))

if __name__ == "__main__":
    # Set the AppUserModelID to change the taskbar icon
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.example.chatapp")
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()