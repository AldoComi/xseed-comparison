import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# ... [previous functions remain unchanged] ...

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

        attributes = st.multiselect("Select attributes to compare:", 
                                    combined_stats.columns.tolist(),
                                    default=["km_covered", "xG", "xT", "Sprints Distance (m)"])

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
        x_var = st.selectbox("Select X-axis variable:", per_90_stats.columns.tolist(), index=per_90_stats.columns.get_loc("xG"))
        y_var = st.selectbox("Select Y-axis variable:", per_90_stats.columns.tolist(), index=per_90_stats.columns.get_loc("xT"))
        
        highlight = st.multiselect("Highlight players (optional):", players, default=[player1, player2])
        
        if st.button("Generate Interactive Scatter Plot"):
            fig = plot_interactive_scatter(per_90_stats, x_var, y_var, highlight)
            st.plotly_chart(fig)

if __name__ == "__main__":
    main()
