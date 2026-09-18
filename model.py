import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans

## Function to create segments based on customers total orders
def orders_segment(x):
    if x == 1:
        return 1
    elif x <= 3:
        return 2
    elif x <= 5:
        return 3
    else:
        return 4

def orders_segment_name(x):
    if x == 1:
        return "1 Order"
    elif x <= 3:
        return "2-3 Orders"
    elif x <= 5:
        return "4-5 Orders"
    else:
        return "6+ Orders"

## Function to create customer segments based on all metrics
def assign_segment(row):
    if row["value_score"] >= 5 and row["engagement_score"] >= 5:
        return "High Value"
    elif row["recency_quantile"] == 3:
        return "At Risk"
    elif row["value_score"] <= 2:
        return "Low Value"
    else:
        return "Mid Value"


def RFM_method(df):
    df = df.copy()
    df["orders_segment"] = df["totalorders"].apply(orders_segment)
    df['orders_segment_name'] = df['totalorders'].apply(orders_segment_name)
    df["payment_quantile"] = pd.qcut(df["totalpayments"], 4, labels=False)
    df["recency_quantile"] = pd.qcut(df["dayssincelastorder"], 4, labels=False)

    df["value_score"] = df["orders_segment"] + df["payment_quantile"]
    df["engagement_score"] = df["ordersperyear"] + (3 - df["recency_quantile"])

    df["segment"] = df.apply(assign_segment, axis=1)
    return df


def KMeans_method(df):
    df = df.copy()
    numeric_features = [
    "totalorders", "totalpayments", "avgorderpayment",
    "totalitems", "avgitemsperorder",
    "totalreviews", "avgreviewscore",
    "dayssincelastorder", "customerlifespan",
    "ordersperyear"
    ]

    categorical_features = ["customer_city", "topproductcategory"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
        ]
    )

    pipeline = Pipeline(steps=[
        ("preprocess", preprocessor),
        ("cluster", KMeans(n_clusters=4, random_state=42))
    ])

    pipeline.fit(df)
    df["cluster"] = pipeline["cluster"].labels_

    return df