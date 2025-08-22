import streamlit as st
import pandas as pd
import altair as alt


# Streamlit App Configuration
st.set_page_config(page_title="ehrQL Dashboard", layout="wide")
st.markdown("<h1 style='text-align: center;'>ehrQL Analysis Dashboard</h1>", unsafe_allow_html=True)

repos_df = pd.read_csv("Data/opensafely_ehrql_code_files.csv")
features_df = pd.read_csv("Data/ehrQL_feature_counts.csv")
feature_repo_df = pd.read_csv("Data/feature-repo_map.csv")
code_files_df = pd.read_csv("Data/opensafely_ehrql_code_files.csv")

if "Created_on" in repos_df.columns:
    repos_df["Created_on"] = pd.to_datetime(repos_df["Created_on"], errors="coerce") # Ensure datetime conversion

if "feature_selected" not in st.session_state:  #initialising session state
    st.session_state.feature_selected = None

if "sort_order" not in st.session_state:
    st.session_state.sort_order = "Oldest First"



page = st.sidebar.radio("Content:", ["Overview", "All Repositories", "Feature Counts", "Feature Details"]) #sidebar


# PAGE 0: Overview
if page == "Overview":
    st.header("Project Overview")
    st.write (
"""
        The aim of this project is to understand how researchers are using ehrQL. I looked at which features are most popular, which ones are rarely used.
        This matters because it will help the tech team decide which features to improve or simplify, nudges researchers towards newer tools, and shows where extra training or clearer documentation might be needed.""" 
    )
        
#     st.write (
# """    
#         How?"""
#     )
#     st.markdown("![Alt text](C:/Users/USER/Downloads/Streamlit.png)")

    st.write (
        """ This dashboard provides insights into:
        - Research repositories that have used ehrQL
        - Usage counts of ehrQL features (classes and methods)
        - Mapping between repositories and the ehrQL features they use  """ 
    )
    
    total_unique_repos = repos_df["Repository"].nunique()
    st.metric("Total Repositories", total_unique_repos)
    st.metric("Total Unique Features", features_df["Feature"].nunique())

# PAGE 1: All Repositories
elif page == "All Repositories":
    st.subheader("All Repositories")
    st.write(
        """
        This page provides an overview of repositories that make use of **ehrQL**. Each entry shows the date the repository was first created along with the number of ehrQL code files it contains.
        The table can be sorted to display either the oldest or the most recent repositories first.
        """
    )

    # Unique repositories with first creation date
    unique_repos_df = repos_df.groupby("Repository")["Created_on"].min().reset_index()
    repo_codefile_counts = repos_df.groupby("Repository").size().reset_index(name="CodeFile Count")
    unique_repos_df = unique_repos_df.merge(repo_codefile_counts, on="Repository", how="left")
    unique_repos_df["Year"] = unique_repos_df["Created_on"].dt.year

    # Repos per year chart
    repos_by_year = unique_repos_df.groupby("Year").size().reset_index(name='Count')
    line_chart = alt.Chart(repos_by_year).mark_line(point=True).encode(
        x='Year:O',
        y='Count:Q',
        tooltip=['Year:O', 'Count:Q']
    ).properties(width=700, title="Unique Repositories per Year").interactive()
    st.altair_chart(line_chart, use_container_width=True)
    st.caption("Line Graph of ehrQL adoption over the years")

    # Session state for sort order
    st.session_state.sort_order = st.radio(
        "Sort repositories by date:", 
        ["Oldest First", "Newest First"], 
        index=0 if st.session_state.sort_order == "Oldest First" else 1
    )

    repos_sorted = unique_repos_df.sort_values(
        "Created_on", ascending=(st.session_state.sort_order == "Oldest First")
    ).reset_index(drop=True)

    st.subheader("Data Frame")
    st.dataframe(repos_sorted, use_container_width=True)


# PAGE 2: Feature Counts
def new_func(feature_data):
    feature_data = feature_data.rename(columns={"URL": "Raw URL"})
    return feature_data

if page == "Feature Counts":
    st.header("ehrQL Feature Counts")
    st.write(
        """
        This section shows the occurrence of different **ehrQL features** across all 65 repositories. The bar charts show which classes and methods are most common, excluding features that returned zero counts.  
        The full table below retains all features, including those with zero usage, to give a complete overview of the features used in this project. The INTERVAL function was excluded because it serves no real function in research code
        """
    )

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
            st.caption("Frequency of ehrQL **class features** used across repositories (features with zero counts excluded).")
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
            st.caption("Frequency of ehrQL **Method features** used across repositories (features with zero counts excluded).")
        else:
            st.info("No method features with nonzero counts.")

    # Full table: all features, sorted by Count (descending)
    st.subheader("All Features (including zero counts)")
    sorted_features = features_df.sort_values("Count", ascending=False).reset_index(drop=True)
    st.dataframe(sorted_features, use_container_width=True)

    st.write (
        """Overall, the data suggests that while some features (such as `where`, `end_date`, and `start_date`) are widely adopted, many remain rarely or never used."""
    )

# PAGE 3: Feature Details
elif page == "Feature Details":
    st.title("Feature Details")
    st.write(
        "This page provides a detailed view into how individual ehrQL features are used across research repositories."
    )

    # Session state for feature selection
    st.session_state.feature_selected = st.selectbox(
        "Select a feature:",
        feature_repo_df["Feature"].unique(),
        index=0 if st.session_state.feature_selected is None else list(feature_repo_df["Feature"].unique()).index(st.session_state.feature_selected)
    )
    feature_selected = st.session_state.feature_selected

    feature_data = feature_repo_df[feature_repo_df["Feature"] == feature_selected].copy()
    unique_repos_count = feature_data["Repository"].nunique()
    st.write(f"**Total unique repositories using this feature:** {unique_repos_count}")

    display_columns = ["Repository"]
    if "URL" in feature_data.columns:
        display_columns.append("URL")
        feature_data = feature_data.rename(columns={"URL": "Raw URL"})
    elif "File" in feature_data.columns:
        display_columns.append("File")

    display_df = feature_data[display_columns].drop_duplicates().reset_index(drop=True)
    st.subheader("Repositories using this Feature")
    st.dataframe(display_df, use_container_width=True)