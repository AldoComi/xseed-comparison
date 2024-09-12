import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# ... [previous functions remain unchanged] ...

def get_stat_type(col_name, non_cumulative_cols):
    if col_name in non_cumulative_cols:
        return f"{col_name} (raw)"
    else:
        return f"{col_name} (per 90)"

def main():
    # Set page config
    st.set_page_config(page_title="XSEED Analytics App", layout="wide")

    # Custom CSS to use Montserrat font
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Montserrat', sans-serif;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("XSEED Analytics App")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        data = load_data(uploaded_file)
        
        # List of columns that should not be cumulated or transformed to per-90
        non_cumulative_cols = [
            'max_speed', 'Max Shot Power (km/h)', 'technical_load',
            'technical_load_left', 'technical_load_right', 'distance_per_minute (m)',
            'EDI (%)', 'Anaerobic Index (%)', 'Aerobic Index (%)'
        ]
        
        combined_stats, per_90_stats = calculate_stats(data)

        st.header("Player Statistics")
        stat_type = st.radio("Select statistic type:", ("Combined", "Per 90 minutes"))
        
        if stat_type == "Combined":
            st.dataframe(combined_stats)
        else:
            st.dataframe(per_90_stats)

        st.header("Player Comparison")
        players = combined_stats.index.tolist()
        player1 = st.selectbox("Select first player:", players)
        player2 = st.selectbox("Select second player:", players, index=1)

        # Create a list of attributes with their types indicated
        attribute_options = [get_stat_type(col, non_cumulative_cols) for col in per_90_stats.columns]
        
        # Select default attributes, ensuring they exist in the data
        default_attributes = ["km_covered (per 90)", "xG (per 90)", "xT (per 90)", "Sprints Distance (m) (per 90)"]
        default_attributes = [attr for attr in default_attributes if attr in attribute_options]

        selected_attributes = st.multiselect(
            "Select attributes to compare:",
            options=attribute_options,
            default=default_attributes
        )

        # Strip the type indicator for actual data access
        attributes = [attr.split(" (")[0] for attr in selected_attributes]

        if st.button("Compare Players"):
            fig = plot_radar_chart(player1, player2, per_90_stats, attributes)
            st.pyplot(fig)

        st.header("Detailed Percentile Comparison")
        if st.button("Show Detailed Percentiles"):
            percentile_stats = calculate_percentiles(per_90_stats)
            comparison = pd.DataFrame({
                player1: percentile_stats.loc[player1, attributes],
                player2: percentile_stats.loc[player2, attributes]
            }).round(2)
            st.dataframe(comparison)

        st.header("Interactive Scatter Plot Comparison")
        x_var_options = [get_stat_type(col, non_cumulative_cols) for col in per_90_stats.columns]
        y_var_options = x_var_options.copy()
        
        x_var_index = x_var_options.index("xG (per 90)") if "xG (per 90)" in x_var_options else 0
        y_var_index = y_var_options.index("xT (per 90)") if "xT (per 90)" in y_var_options else 0
        
        x_var_full = st.selectbox("Select X-axis variable:", x_var_options, index=x_var_index)
        y_var_full = st.selectbox("Select Y-axis variable:", y_var_options, index=y_var_index)
        
        # Strip the type indicator for actual data access
        x_var = x_var_full.split(" (")[0]
        y_var = y_var_full.split(" (")[0]
        
        highlight = st.multiselect("Highlight players (optional):", players, default=[player1, player2])
        
        if st.button("Generate Interactive Scatter Plot"):
            fig = plot_interactive_scatter(per_90_stats, x_var, y_var, highlight)
            st.plotly_chart(fig)

if __name__ == "__main__":
    main()
