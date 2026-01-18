import numpy as np
import pandas as pd
from pathlib import Path


SLA_HOURS = 72
UNKNOWN = "desconocido"


def load_silver(base: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    solicitudes = pd.read_parquet(base / "data" / "silver" / "solicitudes_ciudadanas.parquet")
    oficinas = pd.read_parquet(base / "data" / "silver" / "oficinas.parquet")
    return solicitudes, oficinas


def normalize_gold(df: pd.DataFrame) -> pd.DataFrame:
    # normalize categoricals and fill unknowns
    for col in [
        "category",
        "subcategory",
        "request_type",
        "channel",
        "status",
        "priority",
        "department",
        "province",
        "district",
    ]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
            df.loc[df[col].isin(["", "nan", "none"]), col] = np.nan
            df[col] = df[col].fillna(UNKNOWN)

    if "status" in df.columns:
        df["status"] = df["status"].replace({"cerrrado": "cerrado", "": "otros"}).fillna("otros")

    if "priority" in df.columns:
        df["priority"] = df["priority"].replace({"": UNKNOWN}).fillna(UNKNOWN)

    # numeric consistency
    for col in ["resolution_hours", "cost_soles", "satisfaction_rating"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "resolution_hours" in df.columns:
        df.loc[df["resolution_hours"] < 0, "resolution_hours"] = np.nan
    if "cost_soles" in df.columns:
        df["cost_soles"] = df["cost_soles"].abs()

    if "satisfaction_rating" in df.columns:
        df.loc[~df["satisfaction_rating"].between(1, 5), "satisfaction_rating"] = np.nan

    return df


def add_calendar(df: pd.DataFrame) -> pd.DataFrame:
    created = pd.to_datetime(df.get("created_at"), errors="coerce")
    df["year"] = created.dt.year
    df["month"] = created.dt.month
    df["month_start"] = created.dt.to_period("M").dt.to_timestamp()
    return df


def aggregate_metrics(df: pd.DataFrame, group_cols: list[str], is_lifetime: int) -> pd.DataFrame:
    df = df.copy()
    df["is_closed"] = (df["status"] == "cerrado").astype(int)
    df["is_open"] = (df["status"].isin(["abierto", "en_proceso"])).astype(int)
    df["sla_breach"] = (df["resolution_hours"] > SLA_HOURS).astype(int)
    df["high_satisfaction"] = (df["satisfaction_rating"] >= 4).astype(int)
    df["high_priority"] = df["priority"].isin(["alta", "critica"]).astype(int)

    agg = df.groupby(group_cols, dropna=False).agg(
        total_requests=("request_id", "count"),
        closed_requests=("is_closed", "sum"),
        open_requests=("is_open", "sum"),
        sla_breach_count=("sla_breach", "sum"),
        avg_resolution_hours=("resolution_hours", "mean"),
        median_resolution_hours=("resolution_hours", "median"),
        p90_resolution_hours=("resolution_hours", lambda s: s.quantile(0.9) if s.notna().any() else np.nan),
        avg_satisfaction=("satisfaction_rating", "mean"),
        high_satisfaction_count=("high_satisfaction", "sum"),
        total_cost_soles=("cost_soles", "sum"),
        avg_cost_soles=("cost_soles", "mean"),
        high_priority_count=("high_priority", "sum"),
    ).reset_index()

    agg["closure_rate"] = np.where(agg["total_requests"] > 0, agg["closed_requests"] / agg["total_requests"], np.nan)
    agg["sla_breach_rate"] = np.where(agg["total_requests"] > 0, agg["sla_breach_count"] / agg["total_requests"], np.nan)
    agg["high_satisfaction_rate"] = np.where(agg["total_requests"] > 0, agg["high_satisfaction_count"] / agg["total_requests"], np.nan)
    agg["high_priority_rate"] = np.where(agg["total_requests"] > 0, agg["high_priority_count"] / agg["total_requests"], np.nan)

    agg["is_lifetime"] = is_lifetime
    if is_lifetime:
        agg["year"] = 0
        agg["month"] = 0
        agg["month_start"] = pd.NaT

    return agg


def main() -> None:
    base = Path(__file__).resolve().parents[2]

    solicitudes, oficinas = load_silver(base)

    # join and normalize
    df = solicitudes.merge(oficinas, on="office_id", how="left", suffixes=("", "_office"))
    df = normalize_gold(df)

    # calendar for monthly grain
    df = add_calendar(df)

    # drop records without created_at for monthly aggregation
    monthly = df[df["year"].notna()].copy()

    group_cols = [
        "year",
        "month",
        "month_start",
        "category",
        "request_type",
        "channel",
        "status",
        "priority",
        "department",
        "province",
        "district",
        "office_id",
        "office_name",
        "categoria_principal",
    ]

    monthly_agg = aggregate_metrics(monthly, group_cols, is_lifetime=0)

    lifetime_group_cols = [
        "category",
        "request_type",
        "channel",
        "status",
        "priority",
        "department",
        "province",
        "district",
        "office_id",
        "office_name",
        "categoria_principal",
    ]

    lifetime_agg = aggregate_metrics(df, lifetime_group_cols, is_lifetime=1)

    gold = pd.concat([monthly_agg, lifetime_agg], ignore_index=True)

    out_path = base / "data" / "gold" / "dashboard_reclamos.parquet"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    gold.to_parquet(out_path, index=False)

    print("Gold generado:")
    print("-", out_path)


if __name__ == "__main__":
    main()
