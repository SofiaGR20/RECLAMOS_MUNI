import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

NULL_LIKE = {"", "NULL", "null", "NaN", "nan", "None", "none"}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )
    return df


def clean_string_series(s: pd.Series) -> pd.Series:
    s = s.astype(str).str.strip()
    return s.replace(list(NULL_LIKE), np.nan)


def digits_only(value: str) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    return re.sub(r"\D", "", str(value))


def is_valid_email(value: str) -> bool:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return False
    value = str(value).strip()
    if not value:
        return False
    return EMAIL_RE.match(value) is not None


def read_csv_bronze(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype=str, keep_default_na=False).replace(list(NULL_LIKE), np.nan)


def count_nulls(df: pd.DataFrame) -> dict:
    total = len(df)
    return {
        col: {
            "nulls": int(df[col].isna().sum()),
            "null_pct": float(df[col].isna().mean()) if total else 0.0,
        }
        for col in df.columns
    }


def iqr_outliers(series: pd.Series) -> int:
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return 0
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return int(((s < lower) | (s > upper)).sum())


def build_quality_report(
    solicitudes_raw: pd.DataFrame,
    oficinas_raw: pd.DataFrame,
    solicitudes_clean: pd.DataFrame,
    oficinas_clean: pd.DataFrame,
) -> dict:
    report = {
        "solicitudes": {
            "rows_raw": int(len(solicitudes_raw)),
            "rows_clean": int(len(solicitudes_clean)),
            "nulls_clean": count_nulls(solicitudes_clean),
            "duplicate_request_id_raw": int(solicitudes_raw["request_id"].duplicated().sum())
            if "request_id" in solicitudes_raw.columns
            else 0,
            "duplicate_request_id_clean": int(solicitudes_clean["request_id"].duplicated().sum())
            if "request_id" in solicitudes_clean.columns
            else 0,
        },
        "oficinas": {
            "rows_raw": int(len(oficinas_raw)),
            "rows_clean": int(len(oficinas_clean)),
            "nulls_clean": count_nulls(oficinas_clean),
            "duplicate_office_id_raw": int(oficinas_raw["office_id"].duplicated().sum())
            if "office_id" in oficinas_raw.columns
            else 0,
            "duplicate_office_id_clean": int(oficinas_clean["office_id"].duplicated().sum())
            if "office_id" in oficinas_clean.columns
            else 0,
        },
    }

    if "created_at" in solicitudes_raw.columns and "closed_at" in solicitudes_raw.columns:
        created = pd.to_datetime(solicitudes_raw["created_at"], errors="coerce")
        closed = pd.to_datetime(solicitudes_raw["closed_at"], errors="coerce")
        mask = created.notna() & closed.notna() & (closed < created)
        report["solicitudes"]["invalid_date_order_raw"] = int(mask.sum())

    if "satisfaction_rating" in solicitudes_raw.columns:
        rating = pd.to_numeric(solicitudes_raw["satisfaction_rating"], errors="coerce")
        report["solicitudes"]["rating_out_of_range_raw"] = int((~rating.between(1, 5)).sum())

    if "latitude" in solicitudes_raw.columns:
        lat = pd.to_numeric(solicitudes_raw["latitude"], errors="coerce")
        report["solicitudes"]["latitude_out_of_range_raw"] = int((~lat.between(-19.5, -0.5)).sum())

    if "longitude" in solicitudes_raw.columns:
        lon = pd.to_numeric(solicitudes_raw["longitude"], errors="coerce")
        report["solicitudes"]["longitude_out_of_range_raw"] = int((~lon.between(-82.5, -68.0)).sum())

    if "contact_phone" in solicitudes_raw.columns:
        phones = solicitudes_raw["contact_phone"].apply(digits_only)
        report["solicitudes"]["invalid_phone_raw"] = int((phones.str.len() != 9).sum())

    if "contact_email" in solicitudes_raw.columns:
        report["solicitudes"]["invalid_email_raw"] = int((~solicitudes_raw["contact_email"].apply(is_valid_email)).sum())

    outlier_fields = ["resolution_hours", "cost_soles", "satisfaction_rating"]
    report["solicitudes"]["outliers_clean"] = {
        col: iqr_outliers(solicitudes_clean[col]) for col in outlier_fields if col in solicitudes_clean.columns
    }

    return report


def write_quality_report(report: dict, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "quality_report.json"
    md_path = out_dir / "quality_report.md"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = ["# Data Quality Report", ""]
    for section in ["solicitudes", "oficinas"]:
        data = report.get(section, {})
        lines.append(f"## {section}")
        lines.append(f"- rows_raw: {data.get('rows_raw')}")
        lines.append(f"- rows_clean: {data.get('rows_clean')}")
        for key in [
            "duplicate_request_id_raw",
            "duplicate_request_id_clean",
            "duplicate_office_id_raw",
            "duplicate_office_id_clean",
            "invalid_date_order_raw",
            "rating_out_of_range_raw",
            "latitude_out_of_range_raw",
            "longitude_out_of_range_raw",
            "invalid_phone_raw",
            "invalid_email_raw",
        ]:
            if key in data:
                lines.append(f"- {key}: {data[key]}")
        if "outliers_clean" in data:
            lines.append("- outliers_clean:")
            for col, count in data["outliers_clean"].items():
                lines.append(f"  - {col}: {count}")
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")


def clean_oficinas(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)

    for col in df.select_dtypes(include="object").columns:
        df[col] = clean_string_series(df[col])

    if "categoria_principal" in df.columns:
        df["categoria_principal"] = df["categoria_principal"].str.lower().replace({"desconocida": "otra"})

    if "telefono_contacto" in df.columns:
        df["telefono_contacto"] = df["telefono_contacto"].apply(digits_only)
        df.loc[df["telefono_contacto"].str.len() < 7, "telefono_contacto"] = np.nan

    if "email_contacto" in df.columns:
        df.loc[~df["email_contacto"].apply(is_valid_email), "email_contacto"] = np.nan

    df = df.drop_duplicates(subset=["office_id"], keep="first")
    return df


def clean_solicitudes(df: pd.DataFrame, oficinas_ids: set[str]) -> pd.DataFrame:
    df = normalize_columns(df)

    for col in df.select_dtypes(include="object").columns:
        df[col] = clean_string_series(df[col])

    for col in ["channel", "request_type", "category", "subcategory", "priority", "department", "province", "district", "status"]:
        if col in df.columns:
            df[col] = df[col].str.lower()

    if "status" in df.columns:
        df["status"] = df["status"].replace({"cerrrado": "cerrado"})

    created_at_dt = pd.to_datetime(df.get("created_at"), errors="coerce")
    closed_at_dt = pd.to_datetime(df.get("closed_at"), errors="coerce")

    invalid_close = closed_at_dt < created_at_dt
    df.loc[invalid_close, "closed_at"] = np.nan
    df.loc[invalid_close, "resolution_hours"] = np.nan

    # preserve date-only format in output
    df["created_at"] = created_at_dt.dt.strftime("%Y-%m-%d")
    df.loc[created_at_dt.isna(), "created_at"] = np.nan
    df["closed_at"] = closed_at_dt.dt.strftime("%Y-%m-%d")
    df.loc[closed_at_dt.isna(), "closed_at"] = np.nan

    for col in ["resolution_hours", "cost_soles", "satisfaction_rating", "latitude", "longitude"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "satisfaction_rating" in df.columns:
        df.loc[~df["satisfaction_rating"].between(1, 5), "satisfaction_rating"] = np.nan

    if "latitude" in df.columns:
        df.loc[~df["latitude"].between(-19.5, -0.5), "latitude"] = np.nan
    if "longitude" in df.columns:
        df.loc[~df["longitude"].between(-82.5, -68.0), "longitude"] = np.nan

    if "contact_email" in df.columns:
        df.loc[~df["contact_email"].apply(is_valid_email), "contact_email"] = np.nan

    if "contact_phone" in df.columns:
        df["contact_phone"] = df["contact_phone"].apply(digits_only)
        df.loc[df["contact_phone"].str.len() != 9, "contact_phone"] = np.nan

    if "resolution_hours" in df.columns:
        calc = (closed_at_dt - created_at_dt).dt.total_seconds() / 3600
        df.loc[df["resolution_hours"].isna(), "resolution_hours"] = calc
        df.loc[df["resolution_hours"] < 0, "resolution_hours"] = np.nan

    if "office_id" in df.columns:
        df.loc[~df["office_id"].isin(oficinas_ids), "office_id"] = np.nan

    if "request_id" in df.columns:
        sort_key = df["created_at"].fillna(pd.Timestamp.min)
        completeness = df.notna().sum(axis=1)
        df = df.assign(_sort_key=sort_key, _completeness=completeness)
        df = df.sort_values(["_sort_key", "_completeness"]).drop_duplicates(subset=["request_id"], keep="last")
        df = df.drop(columns=["_sort_key", "_completeness"])

    return df


def main() -> None:
    base = Path(__file__).resolve().parents[2]
    bronze = base / "data" / "bronze"
    silver = base / "data" / "silver"
    silver.mkdir(parents=True, exist_ok=True)

    solicitudes_raw = read_csv_bronze(bronze / "solicitudes_ciudadanas.csv")
    oficinas_raw = read_csv_bronze(bronze / "oficinas.csv")

    oficinas = clean_oficinas(oficinas_raw.copy())
    solicitudes = clean_solicitudes(solicitudes_raw.copy(), set(oficinas["office_id"].dropna()))

    solicitudes.to_parquet(silver / "solicitudes_ciudadanas.parquet", index=False)
    oficinas.to_parquet(silver / "oficinas.parquet", index=False)

    report = build_quality_report(solicitudes_raw, oficinas_raw, solicitudes, oficinas)
    write_quality_report(report, silver)

    print("Silver generado:")
    print("-", silver / "solicitudes_ciudadanas.parquet")
    print("-", silver / "oficinas.parquet")
    print("-", silver / "quality_report.json")
    print("-", silver / "quality_report.md")


if __name__ == "__main__":
    main()
