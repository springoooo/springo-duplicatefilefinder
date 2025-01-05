import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from collections import defaultdict
import time

class DuplicateFileFinder:
    def __init__(self, master):
        self.master = master
        master.title("Springo's Duplicate File Finder")
        master.geometry("600x650")
        master.minsize(600, 650)
        master.configure(bg="#f0f0f0")

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", padding=6, relief="flat", background="#FF8C00", foreground="white")
        self.style.map("TButton", background=[("active", "#E07800")])
        self.style.configure("Horizontal.TProgressbar", background="#FF8C00")

        tk.Label(master, text="Springo's Duplicate File Finder", font=("Arial", 18, "bold"), bg="#FF8C00", fg="white", pady=10).pack(fill=tk.X)

        self.dir_frame = tk.Frame(master, bg="#f0f0f0")
        self.dir_frame.pack(fill=tk.X, padx=10, pady=5)
        self.dir_entry = tk.Entry(self.dir_frame, font=("Arial", 10), state='readonly')
        self.dir_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(self.dir_frame, text="Select Folder", command=self.select_directory).pack(side=tk.RIGHT)

        self.filter_frame = tk.Frame(master, bg="#f0f0f0")
        self.filter_frame.pack(fill=tk.BOTH, padx=10, pady=5)
        tk.Label(self.filter_frame, text="Filters (files to exclude):", font=("Arial", 10, "bold"), bg="#f0f0f0").pack(anchor=tk.W)
        self.filter_list = tk.Listbox(self.filter_frame, font=("Arial", 10), selectmode=tk.SINGLE, height=5)
        self.filter_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.filter_scroll = tk.Scrollbar(self.filter_frame, orient=tk.VERTICAL, command=self.filter_list.yview)
        self.filter_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.filter_list.config(yscrollcommand=self.filter_scroll.set)

        self.filter_btn_frame = tk.Frame(self.filter_frame, bg="#f0f0f0")
        self.filter_btn_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        add_btn = ttk.Button(self.filter_btn_frame, text="+", command=self.add_filter, width=3)
        add_btn.pack(fill=tk.X, pady=2)
        remove_btn = ttk.Button(self.filter_btn_frame, text="-", command=self.remove_filter, width=3)
        remove_btn.pack(fill=tk.X, pady=2)

        self.create_tooltip(add_btn, "Add an entry")
        self.create_tooltip(remove_btn, "Remove a selected entry")

        self.find_button = ttk.Button(master, text="Find Duplicate Files", command=self.find_duplicates, style="TButton")
        self.find_button.pack(pady=10)

        self.result_label = tk.Label(master, text="", font=("Arial", 10), bg="#f0f0f0")
        self.result_label.pack()

        self.console_frame = tk.Frame(master, bg="#f0f0f0")
        self.console_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.console = tk.Text(self.console_frame, height=10, wrap=tk.WORD, font=("Consolas", 9))
        self.console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.console_scroll = tk.Scrollbar(self.console_frame, orient=tk.VERTICAL, command=self.console.yview)
        self.console_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.console.config(yscrollcommand=self.console_scroll.set)
        self.console.tag_configure("filename", foreground="#FF8C00")

        self.progress = ttk.Progressbar(master, orient=tk.HORIZONTAL, length=300, mode='determinate', style="Horizontal.TProgressbar")
        self.progress.pack(pady=10)

        self.btn_frame = tk.Frame(master, bg="#f0f0f0")
        self.btn_frame.pack(fill=tk.X, padx=10, pady=5)
        ttk.Button(self.btn_frame, text="Clear Entries", command=self.clear_entries).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.btn_frame, text="Save Results to TXT", command=self.save_results_prompt).pack(side=tk.RIGHT, padx=5)

        tk.Label(master, text="Made by Springo | Discord: springo_1", font=("Arial", 8), bg="#f0f0f0").pack(side=tk.BOTTOM, pady=5)

        self.directory = ""
        self.duplicates = None

    def create_tooltip(self, widget, text):
        def enter(event):
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = tk.Label(self.tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1)
            label.pack()

        def leave(event):
            if self.tooltip:
                self.tooltip.destroy()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def select_directory(self):
        self.directory = filedialog.askdirectory()
        self.dir_entry.config(state='normal')
        self.dir_entry.delete(0, tk.END)
        self.dir_entry.insert(0, self.directory)
        self.dir_entry.config(state='readonly')

    def add_filter(self):
        filter_name = tk.simpledialog.askstring("Add Filter", "Enter filename to exclude:")
        if filter_name:
            self.filter_list.insert(tk.END, filter_name)

    def remove_filter(self):
        selected = self.filter_list.curselection()
        if selected:
            self.filter_list.delete(selected)

    def find_duplicates(self):
        if not self.directory:
            messagebox.showerror("Error", "Please select a directory first.")
            return

        self.console.config(state=tk.NORMAL)
        self.console.delete(1.0, tk.END)
        self.console.insert(tk.END, f"Searching for duplicate files in: {self.directory}\n")
        self.console.insert(tk.END, "This may take a while for large directories...\n\n")
        self.console.update()

        self.progress['value'] = 0
        self.master.update_idletasks()

        start_time = time.time()
        self.duplicates = self.find_duplicate_files()
        elapsed_time = time.time() - start_time

        if elapsed_time < 3:
            remaining_time = 3 - elapsed_time
            steps = 100
            for i in range(steps):
                self.progress['value'] = i + 1
                self.master.update_idletasks()
                time.sleep(remaining_time / steps)

        if self.duplicates:
            self.console.insert(tk.END, "Duplicate files found:\n\n")
            for filename, paths in self.duplicates.items():
                self.console.insert(tk.END, f"File: ", "filename")
                self.console.insert(tk.END, f"{filename}\n")
                for path in paths:
                    self.console.insert(tk.END, f" - {path}\n")
                self.console.insert(tk.END, "\n")
        else:
            self.console.insert(tk.END, "No duplicate files found.\n")

        self.console.config(state=tk.DISABLED)
        
        duplicate_count = len(self.duplicates) if self.duplicates else 0
        self.result_label.config(text=f"Successfully found {duplicate_count} duplicate files.")

    def find_duplicate_files(self):
        file_map = defaultdict(list)
        filters = [item.lower() for item in self.filter_list.get(0, tk.END)]

        for root, _, files in os.walk(self.directory):
            for filename in files:
                if filename.lower() not in filters:
                    file_map[filename].append(os.path.join(root, filename))

        return {filename: paths for filename, paths in file_map.items() if len(paths) > 1}

    def save_results_prompt(self):
        if not self.duplicates:
            messagebox.showinfo("No Results", "No duplicate files have been found yet.")
            return

        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            self.save_results(self.duplicates, file_path)
            messagebox.showinfo("Save Complete", f"Results saved to {file_path}")

    def save_results(self, duplicates, output_file):
        with open(output_file, 'w') as f:
            f.write("Duplicate files found:\n\n")
            for filename, paths in duplicates.items():
                f.write(f"File: {filename}\n")
                for path in paths:
                    f.write(f" - {path}\n")
                f.write("\n")

    def clear_entries(self):
        self.directory = ""
        self.dir_entry.config(state='normal')
        self.dir_entry.delete(0, tk.END)
        self.dir_entry.config(state='readonly')
        self.filter_list.delete(0, tk.END)
        self.console.config(state=tk.NORMAL)
        self.console.delete(1.0, tk.END)
        self.console.config(state=tk.DISABLED)
        self.duplicates = None
        self.result_label.config(text="")
        self.progress['value'] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = DuplicateFileFinder(root)
    root.mainloop()
