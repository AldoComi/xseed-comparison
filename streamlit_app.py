import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# ... (keep all previous functions as they were)

def main():
    # Set page config and custom theme
    st.set_page_config(page_title="XSEED Analytics App", layout="wide")
    
    # Custom CSS to change multiselect box color and other styling
    st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    div[data-baseweb="tag"] {
        background-color: #00A9E0 !important;
    }
    div[data-baseweb="tag"] span[title="×"] {
        color: white !important;
    }
    div[data-baseweb="multiselect"] > div {
        background-color: #2b3035;
    }
    .stButton>button {
        background-color: #00A9E0;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("XSEED Analytics App")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        data = load_data(uploaded_file)
        if data is not None:
            non_cumulative_cols = [
                'max_speed', 'Max Shot Power (km/h)', 'technical_load',
                'technical_load_left', 'technical_load_right', 'distance_per_minute (m)',
                'EDI (%)', 'Anaerobic Index (%)', 'Aerobic Index (%)'
            ]
            
            combined_stats, per_90_stats = calculate_stats(data, non_cumulative_cols)
            
            if combined_stats is not None and per_90_stats is not None:
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

                attribute_options = [get_stat_type(col, non_cumulative_cols) for col in per_90_stats.columns]
                
                # Define the default attributes
                default_attributes = [
                    "km_covered (per 90)", 
                    "Sprints Distance (m) (per 90)", 
                    "Sprints (> 21 km/h & > 0.5s) (per 90)", 
                    "max_speed", 
                    "touches_sx (per 90)", 
                    "touches_dx (per 90)", 
                    "xT (per 90)", 
                    "xG (per 90)"
                ]
                
                # Ensure all default attributes are in the options
                default_attributes = [attr for attr in default_attributes if attr in attribute_options]
                
                selected_attributes = st.multiselect(
                    "Select attributes to compare:",
                    options=attribute_options,
                    default=default_attributes
                )

                if st.button("Compare Players"):
                    if len(selected_attributes) < 3:
                        st.warning("Please select at least 3 attributes for comparison.")
                    else:
                        attributes = [attr.split(" (per 90)")[0] for attr in selected_attributes]
                        
                        comparison = pd.DataFrame({
                            player1: per_90_stats.loc[player1, attributes],
                            player2: per_90_stats.loc[player2, attributes]
                        })
                        st.write(comparison)
                        
                        fig = plot_radar_chart(player1, player2, per_90_stats, attributes)
                        if fig is not None:
                            st.pyplot(fig)

                st.header("Interactive Scatter Plot Comparison")
                x_var_options = attribute_options
                y_var_options = attribute_options
                
                x_var_index = x_var_options.index("xG (per 90)") if "xG (per 90)" in x_var_options else 0
                y_var_index = y_var_options.index("xT (per 90)") if "xT (per 90)" in y_var_options else 0
                
                x_var_full = st.selectbox("Select X-axis variable:", x_var_options, index=x_var_index)
                y_var_full = st.selectbox("Select Y-axis variable:", y_var_options, index=y_var_index)
                
                x_var = x_var_full.split(" (per 90)")[0]
                y_var = y_var_full.split(" (per 90)")[0]
                
                highlight = st.multiselect("Highlight players (optional):", players, default=[player1, player2])
                
                if st.button("Generate Interactive Scatter Plot"):
                    fig = plot_interactive_scatter(per_90_stats, x_var, y_var, highlight)
                    if fig is not None:
                        st.plotly_chart(fig)

if __name__ == "__main__":
    main()
