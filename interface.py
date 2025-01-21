import customtkinter as ctk
import tkinter as tk
from tkcalendar import DateEntry
import pandas as pd
from typing import Dict, List
from anomaly import Anomaly
from PIL import Image, ImageTk
import os

# Set theme and color scheme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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


class RecordViewer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.current_td_index = 0

        # Configure window
        self.title("Record Viewer")
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        # Set unified background color
        bg_color = "#1a1a1a"  # Single background color for everything
        self.configure(fg_color=bg_color)

        # Create main container with grid
        self.grid_columnconfigure(0, weight=2)  # Left panel takes 2/3
        self.grid_columnconfigure(1, weight=1)  # Right panel takes 1/3
        self.grid_rowconfigure(0, weight=1)

        # Left panel (Datasheet)
        self.left_panel = ctk.CTkFrame(
            self, fg_color=bg_color, corner_radius=0, border_width=0
        )
        self.left_panel.grid(row=0, column=0, sticky="nsew")

        # Configure left panel grid
        self.left_panel.grid_rowconfigure(0, weight=1)  # Content area
        self.left_panel.grid_rowconfigure(1, weight=0)  # Navigation buttons
        self.left_panel.grid_columnconfigure(0, weight=1)

        # Right panel (Image)
        self.right_panel = ctk.CTkFrame(
            self, fg_color=bg_color, corner_radius=0, border_width=0
        )
        self.right_panel.grid(
            row=0, column=1, sticky="nsew"
        )  # Changed to "nsew" to fill entire area
        self.right_panel.grid_rowconfigure(0, weight=1)
        self.right_panel.grid_columnconfigure(0, weight=1)

        # Load data and create navigation
        self.load_data()

        # Content area frame
        self.content_frame = ctk.CTkFrame(self.left_panel, fg_color=bg_color)
        self.content_frame.grid(
            row=0, column=0, sticky="nsew", padx=20, pady=20
        )

        # Create navigation at bottom
        self.create_navigation()

        # Image label taking 1/3 of screen width and full height
        self.image_label = ctk.CTkLabel(self.right_panel, text="")
        self.image_label.grid(row=0, column=0, sticky="nsew")

        self.show_current_record()

    def create_navigation(self):
        # Navigation frame at bottom
        self.navigation_frame = ctk.CTkFrame(
            self.left_panel, fg_color="#1a1a1a", height=60
        )
        self.navigation_frame.grid(row=1, column=0, sticky="ew")

        # Prevent frame from shrinking
        self.navigation_frame.grid_propagate(False)

        # Center the buttons container
        button_container = ctk.CTkFrame(
            self.navigation_frame, fg_color="transparent"
        )
        button_container.place(relx=0.5, rely=0.5, anchor="center")

        # Previous button with modern styling
        self.prev_btn = ctk.CTkButton(
            button_container,
            text="← Previous",
            command=self.prev_record,
            width=120,
            height=32,
            corner_radius=6,
            fg_color="#2d5a88",
            hover_color="#1e3d5c",
            font=("Inter", 13),
        )
        self.prev_btn.pack(side="left", padx=10)

        # Counter label with modern font
        self.counter_label = ctk.CTkLabel(
            button_container,
            text=f"Record {self.current_td_index + 1} of {len(self.td_list)}",
            font=("Inter", 13),
            text_color="#8b8b8b",
        )
        self.counter_label.pack(side="left", padx=20)

        # Next button with modern styling
        self.next_btn = ctk.CTkButton(
            button_container,
            text="Next →",
            command=self.next_record,
            width=120,
            height=32,
            corner_radius=6,
            fg_color="#2d5a88",
            hover_color="#1e3d5c",
            font=("Inter", 13),
        )
        self.next_btn.pack(side="left", padx=10)

    def load_image(self, td):
        try:
            image_files = [
                f
                for f in os.listdir("card_images")
                if f.endswith((".jpg", ".jpeg", ".png"))
            ]
            image_index = self.current_td_index % len(image_files)
            image_path = os.path.join("card_images", image_files[image_index])

            # Calculate the screen dimensions
            screen_width = self.winfo_width()
            screen_height = self.winfo_height()

            # Calculate target size (1/3 of screen width, full height)
            target_width = screen_width // 3
            target_height = screen_height

            # Load and resize image
            image = Image.open(image_path)

            # Calculate aspect ratio
            aspect_ratio = image.width / image.height

            # Adjust dimensions to maintain aspect ratio
            if aspect_ratio > (target_width / target_height):
                # Image is wider than the target area
                new_width = target_width
                new_height = int(target_width / aspect_ratio)
            else:
                # Image is taller than the target area
                new_height = target_height
                new_width = int(target_height * aspect_ratio)

            image = image.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
        except Exception as e:
            self.image_label.configure(image="")
            self.image_label.configure(text="No image available")

    def show_current_record(self):
        # Clear previous card
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        current_td = self.td_list[self.current_td_index]
        record_data = (
            self.data_df[self.data_df["TD"] == current_td].iloc[0].to_dict()
        )

        # Calculate consistency score
        anomalies = self.anomalies_by_td[current_td]
        consistency_score = 100 - (len(anomalies) * 10)
        consistency_score = max(0, consistency_score)

        status = {field: "valid" for field in record_data.keys()}
        for anomaly in anomalies:
            status[anomaly.field] = "invalid"

        # Create card in content frame
        card_frame = create_card(
            self.content_frame, record_data, status, consistency_score
        )

        # Update counter
        self.counter_label.configure(
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

        # Group anomalies by TD with include_groups=False to fix deprecation warning
        self.anomalies_by_td = (
            self.anomaly_df.groupby("TD", group_keys=False)
            .apply(
                lambda x: [
                    Anomaly(
                        row["Field"],
                        row["Current Value"],
                        row["Issue Type"],
                        float(row["Confidence"].strip("%")) / 100,
                    )
                    for _, row in x.iterrows()
                ],
                include_groups=False,  # Added to fix deprecation warning
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
    card_frame = ctk.CTkFrame(root, fg_color="#252525", corner_radius=12)
    card_frame.pack(padx=20, pady=(0, 20), fill="both", expand=True)

    # Header section with consistency score
    header_frame = ctk.CTkFrame(
        card_frame, fg_color="#2d2d2d", corner_radius=12
    )
    header_frame.pack(fill="x", padx=15, pady=15)

    # TD number with modern styling
    td_label = ctk.CTkLabel(
        header_frame,
        text=f"TD: {data['TD']}",
        font=("Inter", 20, "bold"),
        text_color="#ffffff",
    )
    td_label.pack(side="left", padx=15)

    # Score with pill-style background
    score_frame = ctk.CTkFrame(
        header_frame, fg_color="#2d5a88", corner_radius=15
    )
    score_frame.pack(side="right", padx=15)

    score_label = ctk.CTkLabel(
        score_frame,
        text=f"Consistency: {consistency_score}%",
        font=("Inter", 13),
        text_color="#ffffff",
    )
    score_label.pack(padx=12, pady=6)

    # Fields section with modern styling
    fields_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
    fields_frame.pack(fill="both", expand=True, padx=15, pady=15)

    fields = [
        ("Last_Name", data.get("Last_Name", "")),
        ("First Name", data.get("First Name", "")),
        ("Birthdate (Geb)", data.get("Birthdate (Geb)", "")),
        ("Birth Place", data.get("Birth Place", "")),
        ("Nationality", data.get("Nationality", "")),
        ("Religion", data.get("Religion", "")),
        ("Overall Confidence OCR", data.get("Overall Confidence OCR", "")),
    ]

    for i, (field, value) in enumerate(fields):
        # Field label with modern font
        field_label = ctk.CTkLabel(
            fields_frame,
            text=f"{field}",  # Removed colon for modern look
            anchor="w",
            font=("Inter", 13),
            text_color="#8b8b8b",  # Subtle gray
        )
        field_label.grid(row=i, column=0, sticky="w", pady=8, padx=5)

        # Entry widget with modern styling
        if "Date" in field or "Birthdate" in field:
            entry_widget = DateEntry(
                fields_frame,
                width=20,
                date_pattern="dd/mm/yyyy",
                background=(
                    "#2b2b2b" if status.get(field) != "invalid" else "#662222"
                ),
                foreground="#ffffff",
                borderwidth=0,
            )
            try:
                entry_widget.set_date(value)
            except:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, value)
        else:
            entry_widget = ctk.CTkEntry(
                fields_frame,
                width=200,
                height=32,
                font=("Inter", 13),
                fg_color="#2b2b2b",
                text_color="#ffffff",
                border_color="#404040",
                corner_radius=6,
            )
            entry_widget.insert(0, str(value))
            if status.get(field) == "invalid":
                entry_widget.configure(fg_color="#662222")

        entry_widget.grid(row=i, column=1, pady=8, padx=5, sticky="ew")

    fields_frame.grid_columnconfigure(1, weight=1)
    return card_frame


def main():
    app = RecordViewer()
    app.mainloop()


if __name__ == "__main__":
    main()
