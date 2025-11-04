import pandas as pd
import json
import re

def js_to_dataframe(js_filepath):
    with open(js_filepath, "r", encoding='utf-8') as f:
        js_contents = f.read()

    # Find the array assignment
    match = re.search(r'var\s+\w+\s*=\s*(\[.*\]);?', js_contents, flags=re.DOTALL)
    if not match:
        raise ValueError("Cannot find device data array in the file.")

    data_array_str = match.group(1)

    # Clean up for JSON: double quotes, true->true, false->false (keep as JSON)
    cleaned = (
        data_array_str
        .replace("True", "true")   # Just to avoid Python True if present
        .replace("False", "false")
        .replace("true", "true")
        .replace("false", "false")
    )
    # Remove trailing commas before closing braces/brackets
    cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
    # Sometimes JS allows keys without quotes, but JSON needs double quotes
    # This uses a regex to put quotes around keys, but it's not fool-proof for every JS syntax case.
    cleaned = re.sub(r'(\{|,)\s*([a-zA-Z0-9_]+)\s*:', r'\1 "\2":', cleaned)

    # Now parse as JSON
    data = json.loads(cleaned)
    df = pd.DataFrame(data)
    return df

devices_data = js_to_dataframe("devices.js")


def rename_device_columns(d):
    """
    Renames columns in the device DataFrame to be more descriptive.
    """
    with open("column_map.json") as f:
        column_map = json.load(f)
    
    return d.rename(columns=column_map)


df_raw = rename_device_columns(devices_data)
def eligible_manufacturers_by_sample_size(data, min_total_sample_size):
    # Group by manufacturer, sum sample_size per manufacturer
    sums = data.groupby("manufacturer")["sample_size"].sum()
    # Filter manufacturers with sum >= min_total_sample_size
    eligible = sums[sums >= min_total_sample_size].index.tolist()
    return eligible

def dedupe_models_keep_max_sample_size(df, model_col="model", sample_col="sample_size"):
    # For each model, keep only the row with the maximum sample_size
    return df.sort_values(sample_col, ascending=False).drop_duplicates(subset=model_col, keep="first")
df_raw = dedupe_models_keep_max_sample_size(df_raw)


# Example usage:
MIN_SAMPLE_SIZE = 10
manufacturers = eligible_manufacturers_by_sample_size(df_raw, MIN_SAMPLE_SIZE)
devices_data = df_raw[df_raw["manufacturer"].isin(manufacturers)]

manufacturers = devices_data['manufacturer'].dropna().unique().tolist()
manufacturers = sorted(manufacturers, key=lambda s: s.lower())

numeric_cols = sorted(devices_data.select_dtypes(include='number').columns.tolist())
