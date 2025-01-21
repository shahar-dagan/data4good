import pandas as pd
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Anomaly:
    field: str
    value: str
    issue_type: str
    confidence: float
    suggestions: List[str] = None


class HolocaustRecordValidator:
    def __init__(self):
        # OCR thresholds
        self.MIN_OCR_CONFIDENCE = 75.0
        self.MIN_NAME_OCR_CONFIDENCE = 90.0

        # Define suspicious characters
        self.suspicious_chars = set('!@#$%^&*()_+=[]{}|\\;:"<>?/0123456789')

        # Known valid values
        self.valid_nationalities = {
            "albanian",
            "argentinian",
            "australian",
            "austrian",
            "belgian",
            "brazilian",
            "canadian",
            "costa",
            "croatian",
            "czechoslovakian",
            "estonian",
            "french",
            "german",
            "greek",
            "hungarian",
            "israeli",
            "italian",
            "latvian",
            "lithuanian",
            "luxembourg",
            "dutch",
            "norwegian",
            "polish",
            "romanian",
            "russian",
            "slovakian",
            "slovenian",
            "south african",
            "spanish",
            "swedish",
            "swiss",
            "turkish",
            "ukrainian",
            "american",
            "uruguayan",
            "venezuelan",
            "yugoslavian",
            "stateless",
        }

        self.valid_religions = {
            "Christian",
            "Jewish",
            "Roman Catholic",
            "Orthodox Christian",
            "Muslim",
            "Buddhist",
            "Other",
        }

    def validate_record(self, record: pd.Series) -> List[Anomaly]:
        anomalies = []

        # Check OCR confidence
        if record["Automatic Validation"] == "To be validated":
            anomalies.extend(self._check_ocr_confidence(record))

        # Validate fields
        anomalies.extend(self._validate_names(record))
        anomalies.extend(self._validate_nationality(record))
        anomalies.extend(self._validate_dates(record))
        anomalies.extend(self._validate_religion(record))
        anomalies.extend(self._validate_location(record))

        return anomalies

    def _check_ocr_confidence(self, record) -> List[Anomaly]:
        anomalies = []
        ocr_confidence = float(record["Overall Confidence OCR"])

        if ocr_confidence < self.MIN_OCR_CONFIDENCE:
            anomalies.append(
                Anomaly(
                    field="OCR_Confidence",
                    value=str(ocr_confidence),
                    issue_type="low_confidence",
                    confidence=ocr_confidence,
                )
            )
        return anomalies

    def _validate_names(self, record) -> List[Anomaly]:
        """
        Validates names considering Holocaust record specifics:
        - Last names are usually in capital letters
        - Check for common OCR errors
        - Handle special cases like 'geb' (geboren - maiden name)
        - Check for suspicious characters or numbers
        """
        anomalies = []

        # Validate Last Name
        if pd.notna(record["Last_Name"]):
            last_name = str(record["Last_Name"]).strip()

            # Check if empty after stripping
            if not last_name:
                anomalies.append(
                    Anomaly(
                        field="Last_Name",
                        value="",
                        issue_type="empty_required_field",
                        confidence=1.0,
                    )
                )
            else:
                # Check if name is in capitals (as expected in original documents)
                if not last_name.isupper():
                    anomalies.append(
                        Anomaly(
                            field="Last_Name",
                            value=last_name,
                            issue_type="not_capitalized",
                            confidence=0.8,
                        )
                    )

                # Check for numbers (likely OCR errors)
                if any(char.isdigit() for char in last_name):
                    anomalies.append(
                        Anomaly(
                            field="Last_Name",
                            value=last_name,
                            issue_type="contains_numbers",
                            confidence=0.9,
                        )
                    )

                # Check for suspicious characters
                if any(char in self.suspicious_chars for char in last_name):
                    anomalies.append(
                        Anomaly(
                            field="Last_Name",
                            value=last_name,
                            issue_type="suspicious_characters",
                            confidence=0.9,
                        )
                    )

                # Check for very short names (likely incomplete)
                if len(last_name) < 2:
                    anomalies.append(
                        Anomaly(
                            field="Last_Name",
                            value=last_name,
                            issue_type="too_short",
                            confidence=0.9,
                        )
                    )

                # Check for maiden name indicators
                maiden_name_indicators = [
                    "geb",
                    "geb.",
                    "geboren",
                    "nee",
                    "née",
                ]
                if any(
                    indicator in last_name.lower()
                    for indicator in maiden_name_indicators
                ):
                    # This is not an error, but should be noted for processing
                    anomalies.append(
                        Anomaly(
                            field="Last_Name",
                            value=last_name,
                            issue_type="contains_maiden_name_indicator",
                            confidence=0.7,
                        )
                    )
        else:
            # Missing Last Name
            anomalies.append(
                Anomaly(
                    field="Last_Name",
                    value="",
                    issue_type="missing_required_field",
                    confidence=1.0,
                )
            )

        # Validate First Name (less strict rules)
        if pd.notna(record["First Name"]):
            first_name = str(record["First Name"]).strip()

            # Check if empty after stripping
            if not first_name:
                anomalies.append(
                    Anomaly(
                        field="First Name",
                        value="",
                        issue_type="empty_required_field",
                        confidence=1.0,
                    )
                )
            else:
                # Check for numbers (likely OCR errors)
                if any(char.isdigit() for char in first_name):
                    anomalies.append(
                        Anomaly(
                            field="First Name",
                            value=first_name,
                            issue_type="contains_numbers",
                            confidence=0.9,
                        )
                    )

                # Check for suspicious characters
                if any(char in self.suspicious_chars for char in first_name):
                    anomalies.append(
                        Anomaly(
                            field="First Name",
                            value=first_name,
                            issue_type="suspicious_characters",
                            confidence=0.9,
                        )
                    )
        else:
            # Missing First Name
            anomalies.append(
                Anomaly(
                    field="First Name",
                    value="",
                    issue_type="missing_required_field",
                    confidence=1.0,
                )
            )

        return anomalies

    def _validate_nationality(self, record) -> List[Anomaly]:
        anomalies = []
        if pd.notna(record["Nationality"]):
            nat = str(record["Nationality"]).strip().lower()
            if nat not in self.valid_nationalities:
                anomalies.append(
                    Anomaly(
                        field="Nationality",
                        value=nat,
                        issue_type="unknown_nationality",
                        confidence=0.7,
                    )
                )
        return anomalies

    def _validate_dates(self, record) -> List[Anomaly]:
        """
        Simplified date validation that only checks for basic format issues
        and obviously invalid dates.
        """
        anomalies = []
        if pd.isna(record["Birthdate (Geb)"]):
            return anomalies

        birth_date = str(record["Birthdate (Geb)"]).strip()

        # Handle special case: no date indicator
        if birth_date == "//" or not birth_date:
            return anomalies

        # Handle partial dates like "//1885"
        if birth_date.startswith("//"):
            return anomalies

        # Only validate dates that are in the expected format
        if "/" in birth_date:
            try:
                date = pd.to_datetime(
                    birth_date, format="%d/%m/%Y", dayfirst=True
                )
                # Only flag dates that are obviously wrong
                if date.year < 1800 or date.year > 1950:
                    anomalies.append(
                        Anomaly(
                            field="Birthdate",
                            value=birth_date,
                            issue_type="invalid_format",
                            confidence=0.95,
                        )
                    )
            except:
                # Only flag completely unparseable dates
                if not birth_date.count("/") == 2:
                    anomalies.append(
                        Anomaly(
                            field="Birthdate",
                            value=birth_date,
                            issue_type="invalid_format",
                            confidence=0.95,
                        )
                    )

        return anomalies

    def _validate_religion(self, record) -> List[Anomaly]:
        anomalies = []
        if pd.notna(record["Religion"]):
            religion = str(record["Religion"]).strip()
            # Convert both the input and valid religions to lowercase for comparison
            if religion.lower() not in {
                r.lower() for r in self.valid_religions
            }:
                anomalies.append(
                    Anomaly(
                        field="Religion",
                        value=str(record["Religion"]),
                        issue_type="unknown_religion",
                        confidence=0.8,
                    )
                )
        return anomalies

    def _validate_location(self, record) -> List[Anomaly]:
        anomalies = []
        if pd.isna(record["Birth Place"]):
            anomalies.append(
                Anomaly(
                    field="Birth Place",
                    value="",
                    issue_type="missing_required_field",
                    confidence=1.0,
                )
            )
        return anomalies


def process_database(file_path: str) -> Dict[str, List[Anomaly]]:
    """
    Process entire database and return anomalies by TD number
    """
    validator = HolocaustRecordValidator()
    df = pd.read_excel(file_path)

    anomalies_by_td = {}
    for _, record in df.iterrows():
        anomalies = validator.validate_record(record)
        if anomalies:
            anomalies_by_td[str(record["TD"])] = anomalies

    return anomalies_by_td


def create_anomaly_report(
    anomalies_by_td: Dict[str, List[Anomaly]], output_file: str
):
    """
    Create detailed Excel report of all anomalies
    """
    # Prepare data for DataFrame
    report_data = []

    for td, anomalies in anomalies_by_td.items():
        for field, field_anomalies in anomalies.items():
            for anomaly in field_anomalies:
                report_data.append(
                    {
                        "TD": td,
                        "Field": field,
                        "Current Value": anomaly.value,
                        "Issue Type": anomaly.issue_type,
                        "Confidence": f"{anomaly.confidence * 100:.1f}%",
                    }
                )

    # Create DataFrame and save to Excel
    report_df = pd.DataFrame(report_data)
    report_df.to_excel(output_file, index=False)


def print_summary_stats(anomalies_by_td: Dict[str, List[Anomaly]]):
    """
    Print summary statistics of the anomaly detection
    """
    total_records = len(anomalies_by_td)
    total_anomalies = sum(
        len(anomalies) for anomalies in anomalies_by_td.values()
    )

    # Count issues by type
    issue_counts = {}
    field_counts = {}

    for anomalies in anomalies_by_td.values():
        for anomaly in anomalies:
            issue_counts[anomaly.issue_type] = (
                issue_counts.get(anomaly.issue_type, 0) + 1
            )
            field_counts[anomaly.field] = field_counts.get(anomaly.field, 0) + 1

    print("\nANOMALY DETECTION SUMMARY")
    print("========================")
    print(f"Total records with issues: {total_records}")
    print(f"Total anomalies found: {total_anomalies}")
    print(f"Average issues per record: {total_anomalies/total_records:.1f}")

    print("\nIssues by Field:")
    print("--------------")
    for field, count in sorted(
        field_counts.items(), key=lambda x: x[1], reverse=True
    ):
        print(f"{field}: {count}")

    print("\nIssues by Type:")
    print("-------------")
    for issue_type, count in sorted(
        issue_counts.items(), key=lambda x: x[1], reverse=True
    ):
        print(f"{issue_type}: {count}")


def main():
    try:
        print("Processing database...")
        anomalies = process_database("data.xlsx")

        # Create detailed Excel report
        output_file = "anomaly_report.xlsx"
        create_anomaly_report(anomalies, output_file)
        print(f"\nDetailed report saved to '{output_file}'")

        # Print summary statistics
        print_summary_stats(anomalies)

    except FileNotFoundError:
        print("Error: data.xlsx file not found!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
