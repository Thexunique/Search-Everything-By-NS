import os
import fnmatch
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Menu
from tkinter.constants import END
import threading  # Add this line to import the threading module
import json
import sys
import ctypes
import platform
from datetime import datetime


class FileSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Search made by NS")
        self.root.geometry("800x600")  # Default size, but will adapt to screen resolution
        try:
            self.root.iconbitmap("icon.ico")  # Ensure you have an icon file named 'icon.ico' in the same directory
        except:
            print("Icon file not found. Running without icon.")

        # Check if the application is running as admin
        if not self.is_admin():
            self.request_admin_privileges()

        # Default font settings
        self.font_size = 12
        self.font_family = "Segoe UI"

        # Default search directory (root of the local drive)
        self.default_directory = os.path.abspath(os.sep)  # Root directory of the system

        # Create a modern theme using ttk
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Index file path
        self.index_file = "drive_index.json"
        self.index_data = {}

        # Current sort order
        self.sort_by = None  # None, "type", or "date"
        self.sort_order = "asc"  # "asc" or "desc"

        # Create and place widgets
        self.create_widgets()

        # Add a menu for font customization
        self.create_menu()

        # Make the UI adaptable to screen resolution
        self.adapt_to_screen()

        # Load index if it exists
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, "r") as f:
                    self.index_data = json.load(f)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load index: {e}")

    def is_admin(self):
        """Check if the application is running with administrator privileges."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def request_admin_privileges(self):
        """Prompt the user to run the application as an administrator."""
        if platform.system() == "Windows":
            script = os.path.abspath(sys.argv[0])
            params = " ".join([script] + sys.argv[1:])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            sys.exit(0)

    def adapt_to_screen(self):
        """Adjust window size and widget proportions based on screen resolution."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{int(screen_width * 0.8)}x{int(screen_height * 0.7)}")

    def create_menu(self):
        """Create a menu bar with font customization options."""
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        settings_menu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)

        # Font size menu
        font_menu = Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Font Size", menu=font_menu)
        font_menu.add_command(label="Small (10)", command=lambda: self.set_font_size(10))
        font_menu.add_command(label="Medium (12)", command=lambda: self.set_font_size(12))
        font_menu.add_command(label="Large (14)", command=lambda: self.set_font_size(14))
        font_menu.add_command(label="Extra Large (16)", command=lambda: self.set_font_size(16))

        # Index menu
        index_menu = Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Index", menu=index_menu)
        index_menu.add_command(label="Index Drive", command=self.index_drive)

        # Sort menu
        sort_menu = Menu(settings_menu, tearoff=0)
        settings_menu.add_cascade(label="Sort By", menu=sort_menu)
        sort_menu.add_command(label="Type (A-Z)", command=lambda: self.set_sort("type", "asc"))
        sort_menu.add_command(label="Type (Z-A)", command=lambda: self.set_sort("type", "desc"))
        sort_menu.add_command(label="Date (Newest First)", command=lambda: self.set_sort("date", "desc"))
        sort_menu.add_command(label="Date (Oldest First)", command=lambda: self.set_sort("date", "asc"))

    def set_font_size(self, size):
        """Update the font size for all widgets and adjust row height."""
        self.font_size = size
        self.update_font()
        self.adjust_treeview_columns()  # Adjust columns after font change
        self.adjust_treeview_row_height()  # Adjust row height after font change

    def update_font(self):
        """Apply the current font settings to all widgets."""
        font = (self.font_family, self.font_size)
        self.style.configure(".", font=font)
        self.search_entry.config(font=font)
        self.results_tree.config(font=font)
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, (ttk.Label, ttk.Button, ttk.Entry)):
                        child.config(font=font)

    def adjust_treeview_columns(self):
        """Adjust the Treeview column widths to fit the content."""
        font = (self.font_family, self.font_size)
        font_metrics = tk.font.Font(font=font)
        for col in self.results_tree["columns"]:
            max_width = max(
                self.results_tree.column(col, "width"),  # Current width
                [font_metrics.measure(value) for value in self.get_column_values(col)],  # Content width
                font_metrics.measure(col) * 1.5  # Header width (with padding)
            )
            self.results_tree.column(col, width=int(max_width + 20))  # Add padding

    def adjust_treeview_row_height(self):
        """Adjust the row height of the Treeview based on the font size."""
        font = (self.font_family, self.font_size)
        font_metrics = tk.font.Font(font=font)
        row_height = font_metrics.metrics("linespace") + 4  # Add some padding
        self.results_tree.configure(style="Treeview", rowheight=row_height)

    def get_column_values(self, column):
        """Retrieve all values from a specific column in the Treeview."""
        return [self.results_tree.set(item, column) for item in self.results_tree.get_children()]

    def create_widgets(self):
        """Create and place all widgets in the window."""
        # Frame for the search bar
        search_frame = ttk.Frame(self.root)
        search_frame.pack(pady=10, padx=10, fill=tk.X)

        # Label
        ttk.Label(search_frame, text="Search for:").pack(side=tk.LEFT, padx=5)

        # Entry for search term
        self.search_entry = ttk.Entry(search_frame, width=50)
        self.search_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        self.search_entry.bind("<Return>", lambda event: self.start_search())  # Start search on Enter

        # Browse button to select directory
        ttk.Button(search_frame, text="Browse", command=self.browse_directory).pack(side=tk.LEFT, padx=5)

        # Search button
        self.search_button = ttk.Button(search_frame, text="Search", command=self.start_search)
        self.search_button.pack(side=tk.LEFT, padx=5)

        # Frame for the results
        results_frame = ttk.Frame(self.root)
        results_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        # Treeview to display search results
        self.results_tree = ttk.Treeview(results_frame, columns=("Path", "Type", "Date"), show="headings")
        self.results_tree.heading("Path", text="Path")
        self.results_tree.heading("Type", text="Type")
        self.results_tree.heading("Date", text="Date")
        self.results_tree.pack(fill=tk.BOTH, expand=True)

        # Bind double-click event to open file/folder
        self.results_tree.bind("<Double-1>", self.open_item)

        # Bind right-click event to show context menu
        self.results_tree.bind("<Button-3>", self.show_context_menu)

        # Scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        self.results_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def browse_directory(self):
        """Open a dialog to select the directory to search in."""
        self.directory = filedialog.askdirectory()
        if self.directory:
            self.search_entry.delete(0, END)
            self.search_entry.insert(0, self.directory)

    def start_search(self):
        """Start the search process in a separate thread to avoid freezing the UI."""
        search_term = self.search_entry.get().strip()
        if not search_term:
            messagebox.showwarning("Input Error", "Please enter a search term.")
            return
        if not hasattr(self, 'directory') or not self.directory:
            self.directory = self.default_directory
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.search_button.config(state=tk.DISABLED)
        search_thread = threading.Thread(target=lambda: self.thread_safe_search(search_term))
        search_thread.start()

    def thread_safe_search(self, search_term):
        """Perform the search in a separate thread and update the UI safely."""
        results = []
        if self.index_data:
            # Search within the indexed data
            for path, item_type in self.index_data.items():
                if fnmatch.fnmatch(os.path.basename(path), f"*{search_term}*"):
                    date_modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M:%S')
                    results.append((path, item_type, date_modified))
        else:
            # Perform a live search if no index exists
            for root, dirs, files in os.walk(self.directory):
                for name in dirs + files:
                    if fnmatch.fnmatch(name, f"*{search_term}*"):
                        item_path = os.path.join(root, name)
                        if os.path.isdir(item_path):
                            item_type = "Folder"
                        else:
                            item_type = os.path.splitext(name)[1].upper() or "File"
                        date_modified = datetime.fromtimestamp(os.path.getmtime(item_path)).strftime('%Y-%m-%d %H:%M:%S')
                        results.append((item_path, item_type, date_modified))

        # Apply sorting
        results = self.apply_sorting(results)
        self.root.after(0, lambda: self.update_results(results))
        self.root.after(0, lambda: self.search_button.config(state=tk.NORMAL))

    def apply_sorting(self, results):
        """Sort the results based on the selected sort criteria."""
        if self.sort_by == "type":
            return sorted(results, key=lambda x: x[1], reverse=self.sort_order == "desc")
        elif self.sort_by == "date":
            return sorted(results, key=lambda x: x[2], reverse=self.sort_order == "desc")
        return results

    def set_sort(self, sort_by, sort_order):
        """Set the current sort criteria and reapply sorting."""
        self.sort_by = sort_by
        self.sort_order = sort_order
        self.reapply_sorting()

    def reapply_sorting(self):
        """Reapply sorting to the current results."""
        items = [(self.results_tree.set(item, "Path"), self.results_tree.set(item, "Type"), self.results_tree.set(item, "Date"))
                 for item in self.results_tree.get_children()]
        sorted_items = self.apply_sorting(items)
        # Clear and reinsert sorted items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        for path, item_type, date_modified in sorted_items:
            self.results_tree.insert("", tk.END, values=(path, item_type, date_modified))

    def update_results(self, results):
        """Insert search results into the Treeview and adjust column widths."""
        for path, item_type, date_modified in results:
            self.results_tree.insert("", tk.END, values=(path, item_type, date_modified))
        self.adjust_treeview_columns()  # Adjust columns after inserting new data

    def open_item(self, event):
        """Open the selected file or folder."""
        selected_item = self.results_tree.selection()
        if selected_item:
            path, _, _ = self.results_tree.item(selected_item, "values")
            try:
                os.startfile(path)
            except Exception as e:
                messagebox.showerror("Error", f"Unable to open: {e}")

    def show_context_menu(self, event):
        """Show a context menu when right-clicking on an item."""
        selected_item = self.results_tree.identify_row(event.y)
        if selected_item:
            self.results_tree.selection_set(selected_item)
            path, _, _ = self.results_tree.item(selected_item, "values")
            context_menu = Menu(self.root, tearoff=0)
            context_menu.add_command(label="Open Containing Folder", command=lambda: self.open_containing_folder(path))
            context_menu.add_command(label="Copy Path", command=lambda: self.copy_path_to_clipboard(path))
            context_menu.post(event.x_root, event.y_root)

    def copy_path_to_clipboard(self, path):
        """Copy the selected file/folder path to the clipboard."""
        self.root.clipboard_clear()
        self.root.clipboard_append(path)
        messagebox.showinfo("Copied", f"Copied path to clipboard: {path}")

    def open_containing_folder(self, path):
        """Open the containing folder of the selected file or folder."""
        try:
            if os.path.isfile(path):
                folder_path = os.path.dirname(path)
            else:
                folder_path = path
            os.startfile(folder_path)
        except Exception as e:
            messagebox.showerror("Error", f"Unable to open containing folder: {e}")

    def index_drive(self):
        """Index the selected local drive and save the index to a file."""
        drive = filedialog.askdirectory(title="Select Drive to Index", mustexist=True)
        if not drive:
            return
        messagebox.showinfo("Indexing", f"Indexing drive: {drive}. This may take some time...")
        self.index_data = {}
        for root, dirs, files in os.walk(drive):
            for name in dirs + files:
                item_path = os.path.join(root, name)
                if os.path.isdir(item_path):
                    item_type = "Folder"
                else:
                    item_type = os.path.splitext(name)[1].upper() or "File"
                self.index_data[item_path] = item_type
        # Save the index to a file
        with open(self.index_file, "w") as f:
            json.dump(self.index_data, f)
        messagebox.showinfo("Indexing Complete", "Drive indexing completed successfully.")


if __name__ == "__main__":
    root = tk.Tk()
    app = FileSearchApp(root)
    root.mainloop()
