import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
import pandas as pd
from typing import Dict, List
from anomaly import Anomaly
from PIL import Image, ImageTk
import os

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
    "Alternative Nationality 2": "French",
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
    "Alternative Nationality 2": True,
}


class RecordViewer:
    def __init__(self, root):
        self.root = root
        self.current_td_index = 0

        # Make it full screen
        self.root.attributes("-fullscreen", True)

        # Add escape key binding to exit fullscreen
        self.root.bind(
            "<Escape>", lambda e: root.attributes("-fullscreen", False)
        )

        # Create main container
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        # Left panel (Datasheet)
        self.left_panel = tk.Frame(self.main_frame)
        self.left_panel.pack(side="left", fill="both", expand=True)

        # Right panel (Image)
        self.right_panel = tk.Frame(self.main_frame)
        self.right_panel.pack(side="right", fill="both", expand=True)

        # Load data and create navigation
        self.load_data()
        self.create_navigation()

        # Image label
        self.image_label = tk.Label(self.right_panel)
        self.image_label.pack(padx=20, pady=20, fill="both", expand=True)

        self.show_current_record()

    def create_navigation(self):
        # Store navigation frame as instance variable
        self.navigation_frame = tk.Frame(self.left_panel)
        self.navigation_frame.pack(pady=20)

        # Create style for larger buttons
        style = ttk.Style()
        style.configure("Large.TButton", padding=(20, 10))

        prev_btn = ttk.Button(
            self.navigation_frame,  # Changed from nav_frame
            text="Previous",
            command=self.prev_record,
            style="Large.TButton",
        )
        prev_btn.pack(side="left", padx=10)

        next_btn = ttk.Button(
            self.navigation_frame,  # Changed from nav_frame
            text="Next",
            command=self.next_record,
            style="Large.TButton",
        )
        next_btn.pack(side="left", padx=10)

        self.counter_label = tk.Label(
            self.navigation_frame,  # Changed from nav_frame
            text=f"Record {self.current_td_index + 1} of {len(self.td_list)}",
            font=("Arial", 12),
        )
        self.counter_label.pack(side="left", padx=20)

    def load_image(self, td):
        try:
            # Get list of all images in the directory
            image_files = [
                f
                for f in os.listdir("card_images")
                if f.endswith((".jpg", ".jpeg", ".png"))
            ]

            # Use current_td_index to cycle through available images
            image_index = self.current_td_index % len(image_files)
            image_path = os.path.join("card_images", image_files[image_index])

            # Load image
            image = Image.open(image_path)

            # Get the size of the right panel
            panel_width = self.right_panel.winfo_width()
            panel_height = self.right_panel.winfo_height()

            # Calculate scaling factors for both dimensions
            width_ratio = panel_width / image.width
            height_ratio = panel_height / image.height

            # Use the smaller ratio to ensure image fits in both dimensions
            scale_factor = min(width_ratio, height_ratio)

            # Calculate new dimensions
            new_width = int(
                image.width * scale_factor * 0.9
            )  # 90% of panel width
            new_height = int(
                image.height * scale_factor * 0.9
            )  # 90% of panel height

            # Resize image
            image = image.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo  # Keep a reference
        except Exception as e:
            self.image_label.configure(image="")
            self.image_label.configure(text="No image available")

    def show_current_record(self):
        # Clear previous card
        for widget in self.left_panel.winfo_children():
            if isinstance(widget, tk.Frame) and widget != self.navigation_frame:
                widget.destroy()

        current_td = self.td_list[self.current_td_index]
        record_data = (
            self.data_df[self.data_df["TD"] == current_td].iloc[0].to_dict()
        )

        # Calculate consistency score and create card
        anomalies = self.anomalies_by_td[current_td]
        consistency_score = 100 - (len(anomalies) * 10)
        consistency_score = max(0, consistency_score)

        status = {field: "valid" for field in record_data.keys()}
        for anomaly in anomalies:
            status[anomaly.field] = "invalid"

        # Create card in left panel (Datasheet)
        card_frame = create_card(
            self.left_panel, record_data, status, consistency_score
        )

        # Update counter
        self.counter_label.config(
            text=f"Record {self.current_td_index + 1} of {len(self.td_list)}"
        )

        # Load corresponding image
        self.load_image(current_td)

    def load_data(self):
        # Load data and anomalies
        self.data_df = pd.read_excel("data.xlsx")
        self.anomaly_df = pd.read_excel("anomaly_report.xlsx")

        # Ensure TD columns are strings in both DataFrames
        self.data_df["TD"] = self.data_df["TD"].astype(str)
        self.anomaly_df["TD"] = self.anomaly_df["TD"].astype(str)

        # Group anomalies by TD
        self.anomalies_by_td = (
            self.anomaly_df.groupby(
                "TD", group_keys=False
            )  # Added group_keys=False to silence warning
            .apply(
                lambda x: [
                    Anomaly(
                        row["Field"],
                        row["Current Value"],
                        row["Issue Type"],
                        float(row["Confidence"].strip("%")) / 100,
                    )
                    for _, row in x.iterrows()
                ]
            )
            .to_dict()
        )

        # Get list of TDs with anomalies that exist in the data
        self.td_list = [
            td
            for td in self.anomalies_by_td.keys()
            if any(self.data_df["TD"] == td)
        ]

        if not self.td_list:
            raise ValueError(
                "No matching records found between anomalies and data"
            )

    def next_record(self):
        if self.current_td_index < len(self.td_list) - 1:
            self.current_td_index += 1
            self.show_current_record()

    def prev_record(self):
        if self.current_td_index > 0:
            self.current_td_index -= 1
            self.show_current_record()


def create_card(root, data, status, consistency_score):
    card_frame = tk.Frame(
        root, bd=2, relief="solid", padx=10, pady=10, bg="white"
    )
    card_frame.pack(padx=20, pady=20, fill="both", expand=True)

    # Add consistency score at the top
    score_frame = tk.Frame(card_frame, bg="white")
    score_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10))

    score_label = tk.Label(
        score_frame,
        text=f"Consistency Score: {consistency_score}%",
        font=("Arial", 12, "bold"),
        fg="black",
        bg="white",
    )
    score_label.pack()

    # TD number at the top of the card
    td_label = tk.Label(
        card_frame,
        text=f"TD: {data['TD']}",
        font=("Arial", 14, "bold"),
        fg="black",
        bg="white",
    )
    td_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))

    # Create a list of fields from the actual data
    fields = [
        ("Last_Name", data.get("Last_Name", "")),
        ("First Name", data.get("First Name", "")),
        ("Birthdate (Geb)", data.get("Birthdate (Geb)", "")),
        ("Birth Place", data.get("Birth Place", "")),
        ("Nationality", data.get("Nationality", "")),
        ("Religion", data.get("Religion", "")),
        ("Overall Confidence OCR", data.get("Overall Confidence OCR", "")),
    ]

    row = 2
    for field, value in fields:
        # Check if the field status is invalid
        field_color = "white"
        if status.get(field) == "invalid":
            field_color = "lightcoral"  # Highlight invalid fields with light red background

        # Label for each field
        field_label = tk.Label(
            card_frame,
            text=f"{field}:",
            anchor="w",
            font=("Arial", 10),
            fg="black",
            bg="white",
        )
        field_label.grid(row=row, column=0, sticky="w", pady=2, padx=5)

        # Create Entry widget for editing text fields
        if "Date" in field or "Birthdate" in field:
            entry_widget = DateEntry(
                card_frame,
                width=12,
                date_pattern="dd/mm/yyyy",
                background=field_color,
                foreground="black",  # Added black text for date entry
            )
            try:
                entry_widget.set_date(value)
            except:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, value)
        else:
            entry_widget = tk.Entry(
                card_frame,
                width=30,
                font=("Arial", 10),
                bg=field_color,
                fg="black",  # Added black text for entry
            )
            entry_widget.insert(0, str(value))

        entry_widget.grid(row=row, column=1, pady=2, padx=5)
        row += 1

    return card_frame


def main():
    root = tk.Tk()
    app = RecordViewer(root)
    root.mainloop()


if __name__ == "__main__":
    main()
