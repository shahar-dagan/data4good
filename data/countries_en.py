import pandas as pd

### get_countries func. returns 2 outputs:
# df - a df containing country code - abbreviation - name - formation date - end date
# years_df - a df mapping years 1900-1950 to a comma-separated list of countries that existed
# Note: the end date is 2020-12-31 for currently existing countries because we were all meant to die during Covid

def get_countries(url="http://ksgleditsch.com/data/ksgmdw.txt"):
    df = pd.read_csv(
        url,  # File URL
        sep="\t",  # Tab-separated values
        skiprows=1,  # Skip the first row (header)
        header=None,
        names=["Code", "Abbreviation", "Country", "StartDate", "EndDate"],  # Assign column names
        encoding="latin1",  # encoding
    )

    df["StartDate"] = pd.to_datetime(df["StartDate"], errors='coerce')
    df["EndDate"] = pd.to_datetime(df["EndDate"], errors='coerce')

    year_country_mapping = []

    for year in range(1900, 1951):
        # Filter countries that existed in the current year
        countries_in_year = df[
            (df["StartDate"] <= pd.Timestamp(year=year, month=12, day=31)) &
            (df["EndDate"] >= pd.Timestamp(year=year, month=1, day=1))
        ]["Country"].tolist()
        
        country_list_str = ",".join(countries_in_year)
        year_country_mapping.append({"Year": year, "Countries": country_list_str})
    years_df = pd.DataFrame(year_country_mapping)

    return df, years_df

# # Let's cccccall the function
# df, years_df = get_country_data_and_mapping()

# # Display the resulting DataFrames
# print("Original DataFrame:")
# print(df.head())

# print("\nYear-to-Country Mapping DataFrame:")
# print(years_df.head())
