import pandas as pd
import streamlit as st
from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "bigdata_db"


@st.cache_data
def load_collection(name: str) -> pd.DataFrame:
    client = MongoClient(MONGO_URI)
    coll = client[DB_NAME][name]
    docs = list(coll.find({}))
    for d in docs:
        d["_id"] = str(d["_id"])
    if not docs:
        return pd.DataFrame()
    return pd.DataFrame(docs)


def main():
    st.set_page_config(
        page_title="Yelp Big Data Dashboard",
        page_icon="⭐",
        layout="wide",
    )

    st.title("📊 Yelp Big Data Dashboard")

    st.markdown(
        "This dashboard is built on **MongoDB aggregated collections** "
        "(`agg_city`, `agg_state`) from **1,000,000+ rows** of Yelp-like data."
    )

    # Load data
    df_city = load_collection("agg_city")
    df_state = load_collection("agg_state")

    if df_city.empty or df_state.empty:
        st.warning(
            "No aggregated data found. Please run the ingestion, cleaning, and aggregation "
            "scripts, then refresh this page."
        )
        return

    # --- KPIs ---
    total_businesses = int(df_city["count"].sum())
    unique_cities = int(df_city["_id"].nunique())
    unique_states = int(df_state["_id"].nunique())
    overall_rating = float(df_state["avg_rating"].mean())

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Businesses", f"{total_businesses:,}")
    kpi2.metric("Cities Covered", f"{unique_cities}")
    kpi3.metric("States Covered", f"{unique_states}")
    kpi4.metric("Avg Rating (overall)", f"{overall_rating:.2f}")

    st.markdown("---")

    # Sidebar filters
    st.sidebar.header("Filters")

    min_reviews = int(df_city["count"].min())
    max_reviews = int(df_city["count"].max())
    selected_min_reviews = st.sidebar.slider(
        "Minimum business count per city",
        min_value=min_reviews,
        max_value=max_reviews,
        value=min(50, max_reviews),
        step=10 if max_reviews > 100 else 1,
    )

    df_city_filt = df_city[df_city["count"] >= selected_min_reviews]

    # --- Layout: 2 columns for main charts ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏙️ Top Cities by Business Count")
        top_n = st.slider("Top N cities", 5, 30, 20, key="top_cities_slider")
        df_city_top = df_city_filt.sort_values("count", ascending=False).head(top_n)
        st.bar_chart(df_city_top.set_index("_id")["count"])

    with col2:
        st.subheader("⭐ Average Rating by City")
        df_city_top_rating = df_city_filt.sort_values("avg_rating", ascending=False).head(top_n)
        st.bar_chart(df_city_top_rating.set_index("_id")["avg_rating"])

    st.markdown("---")

    # --- State level view ---
    st.subheader("🗺️ Average Rating by State")

    df_state_sorted = df_state.sort_values("avg_rating", ascending=False)
    st.bar_chart(df_state_sorted.set_index("_id")["avg_rating"])

    with st.expander("View underlying aggregated data (preview)"):
        st.write("City-level aggregates")
        st.dataframe(df_city.head(50))
        st.write("State-level aggregates")
        st.dataframe(df_state.head(50))


if __name__ == "__main__":
    main()
