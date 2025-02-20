import customtkinter as ctk
import tkinter as tk
from tkcalendar import DateEntry
import pandas as pd
from typing import Dict, List
from anomaly import Anomaly
from PIL import Image, ImageTk
import os
import folium
from folium import plugins
import webbrowser
import json
import io
import requests

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

        # Right panel (Image) with minimal padding
        self.right_panel = ctk.CTkFrame(
            self,
            fg_color="#252525",
            corner_radius=12,
            border_width=0,
            width=800,  # Fixed width
            height=700,  # Fixed height
        )
        self.right_panel.grid(
            row=0, column=1, sticky="n", padx=(2, 4), pady=2
        )  # Minimal padding

        # Prevent the panel from shrinking
        self.right_panel.grid_propagate(False)

        # Image label with minimal padding
        self.image_label = ctk.CTkLabel(
            self.right_panel, text="", fg_color="transparent"
        )
        self.image_label.pack(
            padx=2, pady=2, expand=True
        )  # Minimal internal padding

        # Load data and create navigation
        self.load_data()

        # Content area frame
        self.content_frame = ctk.CTkFrame(self.left_panel, fg_color=bg_color)
        self.content_frame.grid(
            row=0, column=0, sticky="nsew", padx=20, pady=20
        )

        # Create navigation at bottom
        self.create_navigation()

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

            # Get panel dimensions (accounting for minimal padding)
            panel_width = 796  # 800 - 4 (padding)
            panel_height = 696  # 700 - 4 (padding)

            # Load image
            image = Image.open(image_path)

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
            self.image_label.configure(image="")
            self.image_label.configure(text="No image available")

    def show_current_record(self):
        try:
            print("\nSHOWING RECORD:")
            # Clear previous content
            for widget in self.content_frame.winfo_children():
                widget.destroy()

            # Get current record
            current_td = self.td_list[self.current_td_index]
            print("Current TD:", current_td)

            record_mask = self.data_df["TD"] == current_td
            print("Records matching TD:", sum(record_mask))

            record_data = self.data_df[record_mask].iloc[0].to_dict()
            print("Record data:", record_data)

            # Calculate consistency score
            anomalies = self.anomalies_by_td[current_td]
            consistency_score = 100 - (len(anomalies) * 10)
            consistency_score = max(0, consistency_score)

            status = {field: "valid" for field in record_data.keys()}
            for anomaly in anomalies:
                status[anomaly.field] = "invalid"

            print("Status:", status)

            # Create navigation frame
            nav_frame = ctk.CTkFrame(
                self.content_frame, fg_color="#252525", corner_radius=12
            )
            nav_frame.pack(padx=20, pady=20, fill="x")

            # Add Consistency Score, TD, and OCR Confidence labels in navbar
            consistency_label = ctk.CTkLabel(
                nav_frame,
                text=f"Consistency Score: {consistency_score}",
                font=("Inter", 12, "bold"),
                text_color="#8b8b8b",
            )
            consistency_label.pack(side="left", padx=15, pady=15)

            td_label = ctk.CTkLabel(
                nav_frame,
                text=f"TD: {current_td}",
                font=("Inter", 12, "bold"),
                text_color="#8b8b8b",
            )
            td_label.pack(side="left", padx=15, pady=15)

            ocr_label = ctk.CTkLabel(
                nav_frame,
                text=f"OCR Confidence: {record_data.get('Overall Confidence OCR', 'N/A')}",
                font=("Inter", 12, "bold"),
                text_color="#8b8b8b",
            )
            ocr_label.pack(side="left", padx=15, pady=15)

            # Add map button if geo data exists
            if "Geo Location" in record_data and record_data["Geo Location"]:
                try:
                    # Clean and parse the JSON string
                    geo_string = str(record_data["Geo Location"])
                    geo_string = geo_string.replace('""', '"')
                    if geo_string.startswith('"') and geo_string.endswith('"'):
                        geo_string = geo_string[1:-1]

                    geo_data = json.loads(geo_string)

                    # Create interactive map
                    map_path = self.create_map(geo_data)

                    # Create a button to open the map
                    map_button = ctk.CTkButton(
                        nav_frame,
                        text="Open Journey Map",
                        command=lambda: webbrowser.open(
                            f"file://{os.path.abspath(map_path)}"
                        ),
                        fg_color="#1a1a1a",
                        hover_color="#2a2a2a",
                        height=32,
                    )
                    map_button.pack(side="right", padx=30, pady=15)

                except Exception as e:
                    print(f"Error creating map: {str(e)}")

            # Create data frame and continue with rest of the data display...
            self.create_card(record_data, status, consistency_score)

            # Load corresponding image
            self.load_image(current_td)

        except Exception as e:
            print(f"Error in show_current_record: {str(e)}")
            import traceback

            traceback.print_exc()

    def create_card(self, data, status, consistency_score, suggestions=None):
        card_frame = ctk.CTkFrame(
            self.content_frame, fg_color="#252525", corner_radius=12
        )
        card_frame.pack(padx=20, pady=(0, 20), fill="both", expand=True)

        # Header with consistency score
        header_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 5))

        score_label = ctk.CTkLabel(
            header_frame,
            text=f"Consistency Score: {consistency_score}%",
            font=("Inter", 16, "bold"),
            text_color="#ffffff",
        )
        score_label.pack(side="left")

        # Fields section
        fields_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Use exact column names from your data
        fields = [
            "TD",
            "Last Name",
            "First Name",
            "Birthdate",
            "Birth Place",
            "Nationality",
            "Religion",
            "Automatic Validation",
        ]

        for i, field in enumerate(fields):
            # Field label
            field_label = ctk.CTkLabel(
                fields_frame,
                text=field,
                anchor="w",
                font=("Inter", 13),
                text_color="#8b8b8b",
            )
            field_label.grid(row=i, column=0, sticky="w", pady=8, padx=5)

            value = data.get(field, "")

            # Entry widget
            if "Date" in field or "Birthdate" in field:
                entry_widget = DateEntry(
                    fields_frame,
                    width=20,
                    date_pattern="dd/mm/yyyy",
                    background=(
                        "#2b2b2b"
                        if status.get(field) != "invalid"
                        else "#662222"
                    ),
                    foreground="#ffffff",
                    borderwidth=0,
                )
                try:
                    entry_widget.set_date(value)
                except:
                    entry_widget.delete(0, tk.END)
                    entry_widget.insert(0, str(value))
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

            entry_widget.configure(state="readonly")
            entry_widget.grid(row=i, column=1, pady=8, padx=5, sticky="ew")

        fields_frame.grid_columnconfigure(1, weight=1)
        return card_frame

    def load_data(self):
        try:
            print("\nLOADING DATA:")
            # Load existing data
            self.data_df = pd.read_excel("data.xlsx")
            print("Data columns:", self.data_df.columns.tolist())
            print("First row of data:", self.data_df.iloc[0].to_dict())

            self.anomaly_df = pd.read_excel("anomaly_report.xlsx")
            print("\nAnomaly columns:", self.anomaly_df.columns.tolist())

            self.suggestions_df = pd.read_excel("suggestions.xlsx")
            print(
                "\nSuggestions columns:", self.suggestions_df.columns.tolist()
            )

            # Clean column names by stripping whitespace
            self.data_df.columns = self.data_df.columns.str.strip()

            # Ensure TD column is string in data and anomaly DataFrames
            self.data_df["TD"] = self.data_df["TD"].astype(str)
            self.anomaly_df["TD"] = self.anomaly_df["TD"].astype(str)

            # Group anomalies by TD
            self.anomalies_by_td = (
                self.anomaly_df.groupby("TD")
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

            print("\nFound TDs with anomalies:", self.td_list)

            if not self.td_list:
                raise ValueError(
                    "No matching records found between anomalies and data"
                )

        except Exception as e:
            print(f"Error in load_data: {str(e)}")
            import traceback

            traceback.print_exc()

    def next_record(self):
        if self.current_td_index < len(self.td_list) - 1:
            self.current_td_index += 1
            self.show_current_record()

    def prev_record(self):
        if self.current_td_index > 0:
            self.current_td_index -= 1
            self.show_current_record()

    def create_map(self, geo_data):
        """Create an interactive map showing the journey path"""
        try:
            # Create a map centered on Europe
            m = folium.Map(location=[50.0, 10.0], zoom_start=4)

            # Extract markers and paths from geo_data
            markers = geo_data.get("markers", [])
            paths = geo_data.get("paths", [])

            coordinates = []
            if markers and paths:
                # Create a dictionary of locations for quick lookup
                locations = {}
                for marker in markers:
                    location = marker.get("location", {})
                    lat = location.get("lat")
                    lon = location.get("lon")
                    label = marker.get("label", "")
                    marker_type = marker.get("type", "Location")
                    if lat is not None and lon is not None:
                        locations[label] = {
                            "coords": [float(lat), float(lon)],
                            "type": marker_type,
                        }

                # Add markers and collect coordinates in path order
                location_number = 1
                added_locations = set()  # Keep track of added locations

                # Add first location
                first_path = paths[0]
                first_label = first_path.get("fromLabel", "")
                if first_label in locations:
                    loc_data = locations[first_label]
                    coords = loc_data["coords"]
                    if tuple(coords) not in added_locations:
                        coordinates.append(coords)
                        added_locations.add(tuple(coords))
                        # Create custom icon with number
                        icon = folium.DivIcon(
                            html=f'<div style="font-size: 12pt; color: white; background-color: red; border-radius: 50%; width: 25px; height: 25px; display: flex; align-items: center; justify-content: center; border: 2px solid white;"><b>{location_number}</b></div>'
                        )
                        folium.Marker(
                            coords,
                            popup=f"{location_number}. {first_label} ({loc_data['type']})",
                            icon=icon,
                        ).add_to(m)
                        location_number += 1

                # Add subsequent locations
                for path in paths:
                    to_label = path.get("toLabel", "")
                    if to_label in locations:
                        loc_data = locations[to_label]
                        coords = loc_data["coords"]
                        if tuple(coords) not in added_locations:
                            coordinates.append(coords)
                            added_locations.add(tuple(coords))
                            # Create custom icon with number
                            icon = folium.DivIcon(
                                html=f'<div style="font-size: 12pt; color: white; background-color: red; border-radius: 50%; width: 25px; height: 25px; display: flex; align-items: center; justify-content: center; border: 2px solid white;"><b>{location_number}</b></div>'
                            )
                            folium.Marker(
                                coords,
                                popup=f"{location_number}. {to_label} ({loc_data['type']})",
                                icon=icon,
                            ).add_to(m)
                            location_number += 1

            # Add path lines if we have coordinates
            if len(coordinates) > 1:
                # Add a line connecting the points
                folium.PolyLine(
                    coordinates, weight=2, color="red", opacity=0.8
                ).add_to(m)

                # Add animated path
                plugins.AntPath(coordinates).add_to(m)

            # Save the map
            map_path = os.path.join(
                os.path.dirname(__file__), "journey_map.html"
            )
            m.save(map_path)
            return map_path

        except Exception as e:
            print(f"Error in create_map: {str(e)}")
            print("Geo data structure:", geo_data)
            raise


def create_card(root, data, status, consistency_score):
    card_frame = ctk.CTkFrame(root, fg_color="#252525", corner_radius=12)
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
    td_frame = ctk.CTkFrame(spacing_frame, fg_color="#2d5a88", corner_radius=15)
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
        text=f"OCR: {data.get('Overall OCR Confidence', '')}%",
        font=("Inter", 13),
        text_color="#ffffff",
    )
    ocr_label.pack(padx=12, pady=6)

    # Fields section
    fields_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
    fields_frame.pack(fill="both", expand=True, padx=15, pady=15)

    fields = [
        ("First Name", data.get("First Name", "")),
        ("Last Name", data.get("Last_Name", "")),
        ("Birthdate", data.get("Birthdate (Geb)", "")),
        ("Birth Place", data.get("Birth Place", "")),
        ("Nationality", data.get("Nationality", "")),
        ("Religion", data.get("Religion", "")),
    ]  # Removed OCR confidence from fields list

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
