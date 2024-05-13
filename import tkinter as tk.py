import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3

class SmartDictionaryGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Dictionary")
        self.root.geometry("800x600")  # Larger desktop size
        
        # Set background color for the GUI
        self.root.configure(bg="#add8e6")  # Light blue background
        
        self.conn = sqlite3.connect("dictionary.db")
        self.cur = self.conn.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS words
                            (word TEXT PRIMARY KEY, definition TEXT)''')
        self.conn.commit()
        
        self.dictionary = self.load_dictionary()
        
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 12), background='black', foreground='black')  # Change button text color to black
        
        self.title_label = ttk.Label(self.root, text="SMART DICTIONARY", font=('Nexa Black', 24), background="#add8e6")
        self.title_label.grid(row=0, columnspan=3, padx=20, pady=20)
        
        self.word_label = ttk.Label(self.root, text="Word:", font=('Arial', 12), background="#add8e6")
        self.word_label.grid(row=1, column=0, padx=20, pady=20, sticky="w")
        
        self.word_entry = ttk.Entry(self.root, width=50, font=('Arial', 12))
        self.word_entry.grid(row=1, column=1, padx=20, pady=20)
        
        self.definition_label = ttk.Label(self.root, text="Definition:", font=('Arial', 12), background="#add8e6")
        self.definition_label.grid(row=2, column=0, padx=20, pady=20, sticky="w")
        
        self.definition_entry = ttk.Entry(self.root, width=50, font=('Arial', 12))
        self.definition_entry.grid(row=2, column=1, padx=20, pady=20)
        
        self.add_button = ttk.Button(self.root, text="Add", command=self.add_word)
        self.add_button.grid(row=1, column=2, padx=20, pady=20, sticky="wens")
        
        self.search_button = ttk.Button(self.root, text="Search", command=self.search_word)
        self.search_button.grid(row=2, column=2, padx=20, pady=20, sticky="wens")
        
        self.update_button = ttk.Button(self.root, text="Update", command=self.update_word)
        self.update_button.grid(row=3, column=0, padx=20, pady=20, sticky="wens")
        
        self.delete_button = ttk.Button(self.root, text="Delete", command=self.delete_word)
        self.delete_button.grid(row=3, column=1, padx=20, pady=20, sticky="wens")
        
        self.output_text = tk.Text(self.root, height=20, width=80, font=('Arial', 12))
        self.output_text.grid(row=4, columnspan=3, padx=20, pady=20)
        
        self.output_text.tag_config("error", foreground="red")
        
        # Database Button
        self.database_button = ttk.Button(self.root, text="Database", command=self.show_database_window)
        self.database_button.grid(row=5, column=0, columnspan=3, padx=20, pady=20, sticky="wens")
        
    def load_dictionary(self):
        dictionary = {}
        self.cur.execute("SELECT * FROM words")
        rows = self.cur.fetchall()
        for row in rows:
            dictionary[row[0]] = row[1]
        return dictionary
    
    def add_word(self):
        word = self.word_entry.get()
        definition = self.definition_entry.get()
        if word and definition:
            if word in self.dictionary:
                messagebox.showerror("Error", "Word already exists in the dictionary.")
            else:
                self.dictionary[word] = definition
                self.cur.execute("INSERT INTO words VALUES (?, ?)", (word, definition))
                self.conn.commit()
                self.output_text.insert(tk.END, f"Word '{word}' added successfully.\n")
                self.clear_entries()
        else:
            self.output_text.insert(tk.END, "Please enter both word and definition.\n", "error")

    def update_word(self):
        word = self.word_entry.get()
        new_definition = self.definition_entry.get()
        if word in self.dictionary:
            self.dictionary[word] = new_definition
            self.cur.execute("UPDATE words SET definition=? WHERE word=?", (new_definition, word))
            self.conn.commit()
            self.output_text.insert(tk.END, f"Definition of '{word}' updated successfully.\n")
            self.clear_entries()
        else:
            self.output_text.insert(tk.END, "Word does not exist in the dictionary.\n", "error")
        
    def delete_word(self):
        word = self.word_entry.get()
        if word in self.dictionary:
            del self.dictionary[word]
            self.cur.execute("DELETE FROM words WHERE word=?", (word,))
            self.conn.commit()
            self.output_text.insert(tk.END, f"Word '{word}' deleted successfully.\n")
            self.clear_entries()
        else:
            self.output_text.insert(tk.END, "Word not found in the dictionary.\n", "error")
        
    def search_word(self):
        word = self.word_entry.get()
        if word in self.dictionary:
            definition = self.dictionary[word]
            self.output_text.insert(tk.END, f"Definition of '{word}': {definition}\n")
            self.clear_entries()
        else:
            self.output_text.insert(tk.END, "Word not found in the dictionary.\n", "error")
    
    def clear_entries(self):
        self.word_entry.delete(0, tk.END)
        self.definition_entry.delete(0, tk.END)
    
    def show_database_window(self):
        self.database_window = tk.Toplevel(self.root)
        self.database_window.title("Database")
        
        # Add buttons for each alphabet
        alphabet_frame = ttk.Frame(self.database_window)
        alphabet_frame.grid(row=0, column=0, sticky="ns")
        
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            ttk.Button(alphabet_frame, text=letter, command=lambda l=letter: self.show_words_starting_with(l)).pack(side="top", padx=2, pady=2)
        
        self.database_tree = ttk.Treeview(self.database_window, columns=("Word", "Definition"), show="headings", height=20)
        self.database_tree.heading("Word", text="Word")
        self.database_tree.heading("Definition", text="Definition")
        self.database_tree.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Populate the database tree initially with all words
        self.populate_database_tree()
    
    def show_words_starting_with(self, letter):
        # Clear the database tree before populating it with new words
        self.populate_database_tree(letter)
    
    def populate_database_tree(self, starting_letter=None):
        # Clear existing items
        self.database_tree.delete(*self.database_tree.get_children())
        # Populate with dictionary items
        for word, definition in self.dictionary.items():
            if starting_letter is None or word.startswith(starting_letter):
                self.database_tree.insert("", "end", values=(word, definition))
    
    def run(self):
        self.root.mainloop()

# Example usage:
gui = SmartDictionaryGUI()
gui.run()
