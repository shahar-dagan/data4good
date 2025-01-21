import customtkinter as ctk
import tkinter as tk
from tkcalendar import DateEntry
import pandas as pd
from typing import Dict, List
from anomaly import Anomaly
from PIL import Image, ImageTk
import os
from tkinter import Menu

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
        self.td_list = []  # Initialize empty list

        # Configure window
        self.title("Record Viewer")
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        # Set unified background color
        bg_color = "#1a1a1a"
        self.configure(fg_color=bg_color)

        # Create main container with grid
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left panel (Datasheet)
        self.left_panel = ctk.CTkFrame(
            self, fg_color=bg_color, corner_radius=0, border_width=0
        )
        self.left_panel.grid(row=0, column=0, sticky="nsew")

        # Configure left panel grid
        self.left_panel.grid_rowconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(1, weight=0)
        self.left_panel.grid_columnconfigure(0, weight=1)

        # Right panel (Image)
        self.right_panel = ctk.CTkFrame(
            self,
            fg_color="#252525",
            corner_radius=12,
            border_width=0,
            width=800,
            height=700,
        )
        self.right_panel.grid(row=0, column=1, sticky="n", padx=(2, 4), pady=2)
        self.right_panel.grid_propagate(False)

        # Image label
        self.image_label = ctk.CTkLabel(
            self.right_panel, text="", fg_color="transparent"
        )
        self.image_label.pack(padx=2, pady=2, expand=True)

        # Content area frame
        self.content_frame = ctk.CTkFrame(self.left_panel, fg_color=bg_color)
        self.content_frame.grid(
            row=0, column=0, sticky="nsew", padx=20, pady=20
        )

        # Load data first
        print("Initializing data...")
        self.load_data()

        # Then create navigation with the loaded data
        self.create_navigation()

        # Create right-click menu
        self.context_menu = Menu(self, tearoff=0)

        print("Data loaded, showing first record...")
        self.show_current_record()
        print("First record should be shown")

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
            print("Loading image for TD:", td)
            image_files = [
                f
                for f in os.listdir("card_images")
                if f.endswith((".jpg", ".jpeg", ".png"))
            ]
            print("Available images:", image_files)

            image_index = self.current_td_index % len(image_files)
            image_path = os.path.join("card_images", image_files[image_index])
            print("Selected image path:", image_path)

            # Get panel dimensions (accounting for minimal padding)
            panel_width = 796  # 800 - 4 (padding)
            panel_height = 696  # 700 - 4 (padding)

            # Load image
            image = Image.open(image_path)
            print("Image loaded successfully")

            # Calculate aspect ratios
            image_ratio = image.width / image.height
            panel_ratio = panel_width / panel_height

            # Determine new size while maintaining aspect ratio
            if image_ratio > panel_ratio:
                # Image is wider than panel
                new_width = panel_width
                new_height = int(panel_width / image_ratio)
            else:
                # Image is taller than panel
                new_height = panel_height
                new_width = int(panel_height * image_ratio)

            # Resize image
            image = image.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )
            photo = ImageTk.PhotoImage(image)
            self.image_label.configure(image=photo)
            self.image_label.image = photo
        except Exception as e:
            print("Error loading image:", str(e))
            self.image_label.configure(image="")
            self.image_label.configure(text="No image available")

    def show_current_record(self):
        print("Starting show_current_record")
        # Clear previous card
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        try:
            current_td = self.td_list[self.current_td_index]
            print(f"Current TD: {current_td}")

            record_data = (
                self.data_df[self.data_df["TD"] == current_td].iloc[0].to_dict()
            )
            print(f"Record data: {record_data}")

            # Get the ID for the current TD
            current_id = record_data.get("ID")
            print(f"Current ID: {current_id}")

            # Get suggestions using ID
            suggestions = {}
            if current_id:
                suggestion_row = self.suggestions_df[
                    self.suggestions_df["ID"] == current_id
                ]
                if not suggestion_row.empty:
                    suggestions = suggestion_row.iloc[0].to_dict()
            print(f"Suggestions: {suggestions}")

            # Calculate consistency score
            anomalies = self.anomalies_by_td[current_td]
            consistency_score = 100 - (len(anomalies) * 10)
            consistency_score = max(0, consistency_score)

            status = {field: "valid" for field in record_data.keys()}
            for anomaly in anomalies:
                status[anomaly.field] = "invalid"

            print("Creating card...")
            # Create card with suggestions
            self.create_card(
                record_data, status, consistency_score, suggestions
            )
            print("Card created")

            # Update counter
            self.counter_label.configure(
                text=f"Record {self.current_td_index + 1} of {len(self.td_list)}"
            )

            # Load corresponding image
            self.load_image(current_td)

        except Exception as e:
            print(f"Error in show_current_record: {str(e)}")
            import traceback

            traceback.print_exc()

    def load_data(self):
        # Load existing data
        print("Loading data files...")
        self.data_df = pd.read_excel("data.xlsx")
        self.anomaly_df = pd.read_excel("anomaly_report.xlsx")
        self.suggestions_df = pd.read_excel("suggestions.xlsx")

        # Clean column names by stripping whitespace
        self.data_df.columns = self.data_df.columns.str.strip()

        print("Data shape:", self.data_df.shape)
        print("Anomaly shape:", self.anomaly_df.shape)
        print("Suggestions shape:", self.suggestions_df.shape)
        print("Data columns:", self.data_df.columns)
        print("Anomaly columns:", self.anomaly_df.columns)
        print("Suggestions columns:", self.suggestions_df.columns)

        # Ensure TD column is string in data and anomaly DataFrames
        self.data_df["TD"] = self.data_df["TD"].astype(str)
        self.anomaly_df["TD"] = self.anomaly_df["TD"].astype(str)

        # Add ID column if it doesn't exist (using TD as ID)
        if "ID" not in self.data_df.columns:
            self.data_df["ID"] = self.data_df["TD"]
        self.data_df["ID"] = self.data_df["ID"].astype(str)

        # Ensure ID column is string in suggestions DataFrame
        if "ID" in self.suggestions_df.columns:
            self.suggestions_df["ID"] = self.suggestions_df["ID"].astype(str)

        # Group anomalies by TD
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
                ]
            )
            .to_dict()
        )

        print("Anomalies by TD:", list(self.anomalies_by_td.keys()))

        # Get list of TDs with anomalies that exist in the data
        self.td_list = [
            td
            for td in self.anomalies_by_td.keys()
            if any(self.data_df["TD"] == td)
        ]

        print("TD list:", self.td_list)

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

    def create_field_entry(
        self, fields_frame, field, value, status, row, suggestions_value=None
    ):
        field_label = ctk.CTkLabel(
            fields_frame,
            text=f"{field}",
            anchor="w",
            font=("Inter", 13),
            text_color="#8b8b8b",
        )
        field_label.grid(row=row, column=0, sticky="w", pady=8, padx=5)

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
                state="readonly",
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
                state="readonly",
            )
            entry_widget.insert(0, str(value))

            # Only show suggestion if it exists and is not "-"
            if (
                suggestions_value is not None
                and str(suggestions_value) != "-"
                and str(suggestions_value) != str(value)
            ):

                entry_widget.configure(fg_color="#662222")  # Highlight in red
                entry_widget.bind(
                    "<Button-3>",
                    lambda e, f=field, v=value, s=suggestions_value: self.show_suggestion_menu(
                        e, f, v, s
                    ),
                )

            elif status.get(field) == "invalid":
                entry_widget.configure(fg_color="#662222")

        entry_widget.grid(row=row, column=1, pady=8, padx=5, sticky="ew")
        return entry_widget

    def show_anomaly_menu(self, event, field, tooltip_text):
        self.context_menu.delete(0, "end")
        self.context_menu.add_command(
            label=f"Issues with {field}:", state="disabled"
        )
        for line in tooltip_text.split("\n"):
            self.context_menu.add_command(label=line, state="disabled")
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def create_card(self, data, status, consistency_score, suggestions=None):
        card_frame = ctk.CTkFrame(
            self.content_frame, fg_color="#252525", corner_radius=12
        )
        card_frame.pack(padx=20, pady=(0, 20), fill="both", expand=True)

        # Header section with evenly spaced indicators
        header_frame = ctk.CTkFrame(
            card_frame, fg_color="#2d2d2d", corner_radius=12
        )
        header_frame.pack(fill="x", padx=15, pady=15)

        # Create a container for even spacing
        spacing_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        spacing_frame.pack(expand=True, fill="x", padx=20)

        # Configure grid columns for even spacing
        spacing_frame.grid_columnconfigure(0, weight=1)
        spacing_frame.grid_columnconfigure(1, weight=1)
        spacing_frame.grid_columnconfigure(2, weight=1)

        # TD number with pill style
        td_frame = ctk.CTkFrame(
            spacing_frame, fg_color="#2d5a88", corner_radius=15
        )
        td_frame.grid(row=0, column=0, padx=10)

        td_label = ctk.CTkLabel(
            td_frame,
            text=f"TD: {data['TD']}",
            font=("Inter", 13),
            text_color="#ffffff",
        )
        td_label.pack(padx=12, pady=6)

        # Consistency score with pill style
        score_frame = ctk.CTkFrame(
            spacing_frame, fg_color="#2d5a88", corner_radius=15
        )
        score_frame.grid(row=0, column=1, padx=10)

        score_label = ctk.CTkLabel(
            score_frame,
            text=f"Consistency: {consistency_score}%",
            font=("Inter", 13),
            text_color="#ffffff",
        )
        score_label.pack(padx=12, pady=6)

        # OCR Confidence score with pill style
        ocr_frame = ctk.CTkFrame(
            spacing_frame, fg_color="#2d5a88", corner_radius=15
        )
        ocr_frame.grid(row=0, column=2, padx=10)

        ocr_label = ctk.CTkLabel(
            ocr_frame,
            text=f"OCR: {data.get('Overall Confidence OCR', '')}%",
            font=("Inter", 13),
            text_color="#ffffff",
        )
        ocr_label.pack(padx=12, pady=6)

        # Fields section
        fields_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True, padx=15, pady=15)

        fields = [
            ("Last_Name", data.get("Last_Name", "")),
            ("First Name", data.get("First Name", "")),
            ("Birthdate (Geb)", data.get("Birthdate (Geb)", "")),
            ("Birth Place", data.get("Birth Place", "")),
            ("Nationality", data.get("Nationality", "")),
            ("Religion", data.get("Religion", "")),
        ]

        for i, (field, value) in enumerate(fields):
            suggestion_value = suggestions.get(field) if suggestions else None
            self.create_field_entry(
                fields_frame, field, value, status, i, suggestion_value
            )

        fields_frame.grid_columnconfigure(1, weight=1)
        return card_frame


def main():
    app = RecordViewer()
    app.mainloop()


if __name__ == "__main__":
    main()
