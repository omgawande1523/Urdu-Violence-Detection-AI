import pandas as pd
import pyarrow as pa
from typing import Dict, Any, Tuple

# Categories definitions
LEVEL1_CATEGORIES = {"Violence", "Non-Violence"}
LEVEL2_CATEGORIES = {"Gender", "Economic", "Ethnic", "Political", "Religious", "General", "None"}

def validate_dataframe_schema(df: pd.DataFrame) -> Tuple[bool, str]:
    """Validates dataframe schema using PyArrow to ensure type correctness."""
    expected_schema = pa.schema([
        ("text", pa.string()),
        ("level1", pa.string()),
        ("level2", pa.string()),
    ])
    
    # Check if necessary columns exist
    missing_cols = [col for col in ["text", "level1"] if col not in df.columns]
    if missing_cols:
        return False, f"Missing required columns: {', '.join(missing_cols)}"
    
    # If level2 is missing, fill with "None"
    if "level2" not in df.columns:
        df["level2"] = "None"
    else:
        df["level2"] = df["level2"].fillna("None")

    # Cast to ensure proper typing
    try:
        table = pa.Table.from_pandas(df[["text", "level1", "level2"]])
        # Just verifying structure
        return True, "Schema is valid"
    except Exception as e:
        return False, f"Schema validation error: {str(e)}"

def run_quality_checks(df: pd.DataFrame) -> Dict[str, Any]:
    """Runs data quality rules (emulating Great Expectations rules) on pandas DataFrame."""
    report = {
        "success": True,
        "total_records": len(df),
        "empty_text_count": 0,
        "invalid_level1_count": 0,
        "invalid_level2_count": 0,
        "duplicate_count": 0,
        "errors": []
    }
    
    if df.empty:
        report["success"] = False
        report["errors"].append("Dataset is empty.")
        return report

    # 1. Check for empty/null text
    empty_mask = df["text"].isna() | (df["text"].str.strip() == "")
    report["empty_text_count"] = int(empty_mask.sum())
    if report["empty_text_count"] > 0:
        report["success"] = False
        report["errors"].append(f"Found {report['empty_text_count']} rows with empty text content.")

    # 2. Validate Level 1 labels
    invalid_l1 = ~df["level1"].isin(LEVEL1_CATEGORIES)
    report["invalid_level1_count"] = int(invalid_l1.sum())
    if report["invalid_level1_count"] > 0:
        report["success"] = False
        report["errors"].append(f"Found {report['invalid_level1_count']} rows with invalid Level 1 labels.")

    # 3. Validate Level 2 labels conditional rules
    # If level 1 is 'Non-Violence', level 2 must be 'None' or equivalent empty placeholder
    # If level 1 is 'Violence', level 2 must be one of the six categories
    invalid_l2_rows = 0
    for idx, row in df.iterrows():
        l1 = row["level1"]
        l2 = row["level2"]
        if l1 == "Non-Violence" and l2 not in ("None", "", None):
            invalid_l2_rows += 1
        elif l1 == "Violence" and l2 not in LEVEL2_CATEGORIES - {"None"}:
            invalid_l2_rows += 1
            
    report["invalid_level2_count"] = invalid_l2_rows
    if invalid_l2_rows > 0:
        report["success"] = False
        report["errors"].append(f"Found {invalid_l2_rows} rows with invalid Level 2 labels based on Level 1 predictions.")

    # 4. Check for duplicates
    duplicates = df.duplicated(subset=["text"])
    report["duplicate_count"] = int(duplicates.sum())
    
    return report

def clean_and_normalize_dataframe(df: pd.DataFrame):
    """Cleans data by removing duplicates, trimming spaces, and dropping empty rows."""
    from ai_service.app.pipelines.urdu_preprocessing import preprocess_text
    
    df = df.copy()
    if "text" in df.columns:
        df["text"] = df["text"].astype(str)
        df["normalized_text"] = df["text"].apply(preprocess_text)
        df = df[df["normalized_text"] != ""]
        df = df.drop_duplicates(subset=["normalized_text"])
    
    return df
