import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry

# Sample data and status
sample_data = {
    "ID": "123456",
    "First Name": "John",
    "Last Name": "Doe",
    "Father": "Richard Doe",
    "Mother": "Jane Doe",
    "Spouse": "Mary Doe",
    "Birth Date": "01/01/1900",
    "Alternative Birthdate": "02/01/1900",
    "Birthplace": "Berlin",
    "Tracing Document Number": "78910",
    "Nationality": "German",
    "Alternative Nationality 1": "Polish",
    "Alternative Nationality 2": "French"
}

# Field validation status (valid/invalid)
field_status = {
    "ID": True,
    "First Name": True,
    "Last Name": False,
    "Father": True,
    "Mother": True,
    "Spouse": True,
    "Birth Date": True,
    "Alternative Birthdate": False,
    "Birthplace": False,
    "Tracing Document Number": True,
    "Nationality": False,
    "Alternative Nationality 1": False,
    "Alternative Nationality 2": True
}

def create_card(root, data, status):
    card_frame = tk.Frame(root, bd=2, relief="solid", padx=10, pady=10)
    card_frame.pack(padx=20, pady=20, fill="both", expand=True)
    
    # ID number at the top of the card
    id_label = tk.Label(card_frame, text=f"ID: {data['ID']}", font=("Arial", 14, "bold"))
    id_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

    # Create a list of fields - name, etc.
    fields = [
        ("First Name", data["First Name"]),
        ("Last Name", data["Last Name"]),
        ("Father", data["Father"]),
        ("Mother", data["Mother"]),
        ("Spouse", data["Spouse"]),
        ("Birth Date", data["Birth Date"]),
        ("Alternative Birthdate", data["Alternative Birthdate"]),
        ("Birthplace", data["Birthplace"]),
        ("Tracing Document Number", data["Tracing Document Number"]),
        ("Nationality", data["Nationality"]),
        ("Alternative Nationality 1", data["Alternative Nationality 1"]),
        ("Alternative Nationality 2", data["Alternative Nationality 2"]),
    ]
    
    row = 1
    for field, value in fields:
        # Check if the field status is invalid
        field_color = "white"
        if status.get(field) == "invalid":
            field_color = "lightcoral"  # Highlight invalid fields with light red background
        
        # Label for each field
        field_label = tk.Label(card_frame, text=f"{field}:", anchor="w", font=("Arial", 10))
        field_label.grid(row=row, column=0, sticky="w", pady=2, padx=5)
        
        # Create Entry widget for editing text fields
        if "Date" in field:  # Allow volunteers/researchers to select a date to avoid human error?
            entry_widget = DateEntry(card_frame, width=12, date_pattern="dd/mm/yyyy", background=field_color)
            entry_widget.set_date(value)
        else:
            entry_widget = tk.Entry(card_frame, width=30, font=("Arial", 10), bg=field_color)
            entry_widget.insert(0, value)
        
        # Add the CONSISTENCY field here:
        # calculated based on: number of rows highlighted as invalid in field_status
        # AND potentially the number of matches between our parsing of upper and middle columns and their row info?
        
        entry_widget.grid(row=row, column=1, pady=2, padx=5)
        row += 1

def main():
    # Create the main window
    root = tk.Tk()
    root.title("Arolsen Archives Data Viewer")
    create_card(root, sample_data, field_status)
    
    root.mainloop() # GOOOOOOOOOO

if __name__ == "__main__":
    main()
