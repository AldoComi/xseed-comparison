import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# ... (keep all previous functions as they were, except for plot_distance_breakdown)

def plot_distance_breakdown(data):
    intensity_columns = [
        'Standing (m) (0-0.3 km/h)',
        'Walking (m) (0.3-3 km/h)',
        'Jogging (m) (3-8 km/h)',
        'Low Intensity Running (m) (8-13 km/h)',
        'Mid Intensity Running (m) (13-18 km/h)',
        'High Intensity Running (m) (> 18 km/h)'
    ]
    
    if not all(col in data.columns for col in intensity_columns):
        st.error("Required distance breakdown columns are missing from the data.")
        return None
    
    plot_data = data[['Player'] + intensity_columns].sort_values(by='Player')
    plot_data_melted = plot_data.melt(id_vars=['Player'], var_name='Intensity', value_name='Distance')
    
    label_mapping = {
        'Standing (m) (0-0.3 km/h)': 'Standing',
        'Walking (m) (0.3-3 km/h)': 'Walking',
        'Jogging (m) (3-8 km/h)': 'Jogging',
        'Low Intensity Running (m) (8-13 km/h)': 'Low Intensity',
        'Mid Intensity Running (m) (13-18 km/h)': 'Mid Intensity',
        'High Intensity Running (m) (> 18 km/h)': 'High Intensity'
    }
    
    plot_data_melted['Intensity'] = plot_data_melted['Intensity'].map(label_mapping)
    
    # Updated color scheme to match the example chart
    color_scheme = {
        'Standing': '#1a2f38',
        'Walking': '#164a5b',
        'Jogging': '#11698e',
        'Low Intensity': '#119da4',
        'Mid Intensity': '#13505b',
        'High Intensity': '#0c7b93'
    }
    
    fig = px.bar(plot_data_melted, x='Distance', y='Player', color='Intensity', orientation='h',
                 title='Distance Covered by Intensity Level',
                 labels={'Distance': 'Distance covered (m)', 'Player': ''},
                 color_discrete_map=color_scheme)
    
    fig.update_layout(
        barmode='stack',
        height=600,
        font_family="Montserrat",
        font_color='white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend_title_text='Intensity Level',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_xaxes(title_font=dict(size=14), tickfont=dict(size=12))
    fig.update_yaxes(title_font=dict(size=14), tickfont=dict(size=12))
    
    return fig

def main():
    st.set_page_config(page_title="XSEED Analytics App", layout="wide")
    
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

                # Distance Covered Breakdown chart moved here
                st.header("Distance Covered Breakdown")
                distance_fig = plot_distance_breakdown(data)
                if distance_fig is not None:
                    st.plotly_chart(distance_fig, use_container_width=True)

                st.header("Player Comparison")
                players = combined_stats.index.tolist()
                player1 = st.selectbox("Select first player:", players)
                player2 = st.selectbox("Select second player:", players, index=1)

                attribute_options = [get_stat_type(col, non_cumulative_cols) for col in per_90_stats.columns]
                
                selected_attributes = st.multiselect(
                    "Select attributes to compare:",
                    options=attribute_options,
                    default=attribute_options[:5]  # Select first 5 attributes by default
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
