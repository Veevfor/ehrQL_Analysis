import streamlit as st
import pandas as pd
import altair as alt

# Streamlit App Configuration
st.set_page_config(page_title="ehrQL Dashboard", layout="wide")
st.markdown("<h1 style='text-align: center;'>ehrQL Project Dashboard</h1>", unsafe_allow_html=True)

repos_df = pd.read_csv("Data/opensafely_ehrql_code_files.csv")
features_df = pd.read_csv("Data/ehrQL_feature_counts.csv")
feature_repo_df = pd.read_csv("Data/feature-repo_map.csv")

if "Created_on" in repos_df.columns:
    repos_df["Created_on"] = pd.to_datetime(repos_df["Created_on"], errors="coerce") # Ensure datetime conversion


page = st.sidebar.radio("Select Page:", ["Overview", "All Repositories", "Feature Counts", "Feature Details"]) #sidebar


# PAGE 0: Overview
if page == "Overview":
    st.header("Project Overview")
    st.write(
        """
        Welcome to the **ehrQL Dashboard**.  
        
        This dashboard provides insights into:
        - Research repositories that have used ehrQL
        - Usage counts of ehrQL features (classes and methods)
        - Mapping between repositories and the ehrQL features they use  

        Use the sidebar to navigate between pages.
        """
    )
    st.metric("Total Repositories", len(repos_df))
    st.metric("Total Unique Features", features_df["Feature"].nunique())


# PAGE 1: All Repositories
elif page == "All Repositories":
    st.header("All Research Repositories")

    total_repos = len(repos_df)
    st.metric("Total Repositories", total_repos)

    repos_df["date"] = repos_df["Created_on"].dt.date
    daily_counts = repos_df.groupby("date").size().reset_index(name="Count")


    # Line chart by year
    repos_by_year = (
        repos_df.groupby(repos_df['Created_on'].dt.year)
        .size()
        .reset_index(name='Count')
        .rename(columns={'Created_on': 'Year'})
    )
    line_chart = alt.Chart(repos_by_year).mark_line(point=True).encode(
        x='Year:O',
        y='Count:Q',
        tooltip=['Year:O', 'Count:Q']
    ).properties(
        width=700,
        title="Repositories per Year"
    ).interactive()

    st.altair_chart(line_chart, use_container_width=True)

    # Repository table
    st.subheader("All Repositories")

    sort_order = st.radio("Sort repositories by date:", ["Oldest First", "Newest First"])
    repos_sorted = repos_df.sort_values(
        "Created_on", ascending=(sort_order == "Oldest First")
    ).reset_index(drop=True)

    repos_sorted["Year"] = repos_sorted["Created_on"].dt.year
    st.dataframe(repos_sorted, use_container_width=True)


# PAGE 2: Feature Counts
elif page == "Feature Counts":
    st.header("ehrQL Feature Counts")

    classes_df = features_df.iloc[:16].copy()
    methods_df = features_df.iloc[16:].copy()

    classes_nonzero = classes_df[classes_df["Count"] > 0].sort_values("Count", ascending=False) #drop features with zero counts for the chart
    methods_nonzero = methods_df[methods_df["Count"] > 0].sort_values("Count", ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Class")
        if not classes_nonzero.empty:
            class_chart = alt.Chart(classes_nonzero).mark_bar().encode(
                x=alt.X("Count:Q"),
                y=alt.Y("Feature:N", sort="-x"),
                tooltip=["Feature", "Count"]
            )
            st.altair_chart(class_chart, use_container_width=True)
        else:
            st.info("No class features with nonzero counts.")

    with col2:
        st.subheader("Methods")
        if not methods_nonzero.empty:
            method_chart = alt.Chart(methods_nonzero).mark_bar().encode(
                x=alt.X("Count:Q"),
                y=alt.Y("Feature:N", sort="-x"),
                tooltip=["Feature", "Count"]
            )
            st.altair_chart(method_chart, use_container_width=True)
        else:
            st.info("No method features with nonzero counts.")

    # Full table: all features, sorted by Count (descending)
    st.subheader("All Features (including zero counts)")
    sorted_features = features_df.sort_values("Count", ascending=False).reset_index(drop=True)
    st.dataframe(sorted_features, use_container_width=True)


# PAGE 3: Feature Detail View
elif page == "Feature Details":
    st.title("Feature Details")

    feature_selected = st.selectbox("Select a feature:", feature_repo_df["Feature"].unique())

    # Filter repositories using the selected feature
    repos_using_feature = feature_repo_df[feature_repo_df["Feature"] == feature_selected]

    st.subheader("Repositories using")
    st.dataframe(repos_using_feature)

    