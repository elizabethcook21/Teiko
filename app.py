import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import altair as alt

from TechInterview import import_cell_count_data, generate_cell_frequency_summary, analyze_response_effects, melanoma_baseline_summary

# Filenames
DB_NAME = "cell-count.db"
CSV_FILE = "cell-count.csv"

# Configuring the App
st.title("Immune Cell Analysis Dashboard")
st.set_page_config(
    page_title="Immune Cell Analysis Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded")
alt.themes.enable("dark")

with st.sidebar:
    st.title('Initialize & Load Database')
if st.sidebar.button("Initialize & Load Database"):
    import_cell_count_data(DB_NAME, CSV_FILE)
    st.sidebar.success("Database initialized and data loaded.")

# Summary Table
st.header("Summary Table")
st.caption("The frequency of each cell type in each sample.")
df_summary = generate_cell_frequency_summary(DB_NAME)
df_summary['percentage_str'] = df_summary['percentage'].map(lambda x: f"{x:.2f}%") # format percentage with %
display_cols = ['sample', 'population', 'count', 'total_count', 'percentage_str']
st.dataframe(df_summary[display_cols])

# Part 3: Statistical Analysis
st.header("Response Effect Analysis")
st.caption("Comparison of cell frequencies in miraclib-treated melanoma responders vs non-responders.")

if st.button("Analyze Responders vs Non-Responders"):
    fig, sig_results = analyze_response_effects(df_summary, DB_NAME)
    st.pyplot(fig)

    st.subheader("Significant Differences (p < 0.05) from a Mann-Whitney U Test (two-sided)")
    if sig_results:
        st.write("Significant differences found:")
        for pop, p in sig_results:
            st.write(f"- **{pop}**: p = {p:.4f}")
    else:
        st.write("No significant differences found.")

# Part 4: Baseline Subset Analysis
st.header("Melanoma Baseline PBMC Sample Summary")
st.caption("This section shows statistics for all melanoma PBMC samples at baseline who have been treated with miraclib")

if st.button("Show Baseline PBMC Stats for Miraclib"):
    summary = melanoma_baseline_summary(DB_NAME)
    st.write("Samples per project:", summary['samples_per_project'])
    st.write("Responders:", summary['responders'])
    st.write("Non-responders:", summary['non_responders'])
    st.write("Sex Distribution:", summary['sex_distribution'])
