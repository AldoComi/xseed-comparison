import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Function to load CSS based on mode
def load_css(mode):
    if mode == "Night":
        st.markdown(f"""
        <style>
        .stApp {{
            background-color: #0e1117;
            color: white;
        }}
        .stMultiSelect [role="listbox"] > div[data-baseweb="tag"] {{
            background-color: #00a9e0 !important;
            color: white !important;
        }}
        .stMultiSelect [role="listbox"] > div[data-baseweb="tag"] > div {{
            color: white !important;
        }}
        .stButton>button {{
            background-color: #00A9E0;
            color: white;
        }}
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <style>
        .stApp {{
            background-color: #f8f9fa;
            color: black;
        }}
        .stMultiSelect [role="listbox"] > div[data-baseweb="tag"] {{
            background-color: #00a9e0 !important;
            color: white !important;
        }}
        .stMultiSelect [role="listbox"] > div[data-baseweb="tag"] > div {{
            color: white !important;
        }}
        .stButton>button {{
            background-color: #007bff;
            color: white;
        }}
        </style>
        """, unsafe_allow_html=True)

# Function to load data from multiple CSVs and merge them into one DataFrame
def load_data(files):
    cumulative_df = pd.DataFrame()
    
    for file in files:
        if file is not None:
            try:
                df = pd.read_csv(file)
                required_columns = ['Player', 'Minutes']
                if not all(col in df.columns for col in required_columns):
                    st.error(f"CSV file '{file.name}' must contain at least these columns: {', '.join(required_columns)}")
                    return None
                cumulative_df = pd.concat([cumulative_df, df])
            except Exception as e:
                st.error(f"Error loading data from '{file.name}': {str(e)}")
                return None
    
    return cumulative_df

# Function to calculate cumulative and P90 stats across all matches
def calculate_stats(df, non_cumulative_cols):
    try:
        cumulative_df = df.drop(columns=non_cumulative_cols)
        non_cumulative_df = df[['Player'] + non_cumulative_cols]
        
        # Cumulative Stats: Summing values across all matches
        cumulative_stats = cumulative_df.groupby('Player').sum(numeric_only=True)
        
        # Non-Cumulative Stats: Averaging the non-cumulative columns
        non_cumulative_stats = non_cumulative_df.groupby('Player').mean()
        
        # Merging cumulative and non-cumulative stats
        combined_stats = pd.concat([cumulative_stats, non_cumulative_stats], axis=1)
        
        # Calculating per-90 stats based on total cumulative minutes
        minutes_played = combined_stats['Minutes']
        per_90_stats = combined_stats.copy()
        per_90_cols = [col for col in cumulative_stats.columns if col not in non_cumulative_cols]
        per_90_stats[per_90_cols] = per_90_stats[per_90_cols].div(minutes_played, axis=0) * 90
        
        return combined_stats, per_90_stats
    except Exception as e:
        st.error(f"Error calculating stats: {str(e)}")
        return None, None

# Function to calculate percentiles
def calculate_percentiles(stats):
    return stats.rank(pct=True) * 100

# Function to get stat type
def get_stat_type(col_name, non_cumulative_cols):
    if col_name in non_cumulative_cols:
        return col_name
    else:
        return f"{col_name} (per 90)"

# Function to plot radar chart using Plotly
def plot_radar_chart_plotly(player1, player2, stats, attributes, per_90_stats):
    try:
        percentile_stats = calculate_percentiles(stats)
        
        categories = attributes + [attributes[0]]  # Closing the radar chart
        player1_values = percentile_stats.loc[player1, attributes].values.tolist() + [percentile_stats.loc[player1, attributes].values[0]]
        player2_values = percentile_stats.loc[player2, attributes].values.tolist() + [percentile_stats.loc[player2, attributes].values[0]]
        
        # Custom hover data for radar chart
        player1_hover = [
            f"Original: {stats.loc[player1, attr]:.2f}<br>Per 90: {per_90_stats.loc[player1, attr]:.2f}<br>Percentile: {percentile_stats.loc[player1, attr]:.2f}"
            for attr in attributes
        ]
        player2_hover = [
            f"Original: {stats.loc[player2, attr]:.2f}<br>Per 90: {per_90_stats.loc[player2, attr]:.2f}<br>Percentile: {percentile_stats.loc[player2, attr]:.2f}"
            for attr in attributes
        ]

        player1_hover += [player1_hover[0]]  # Closing hover data for radar chart
        player2_hover += [player2_hover[0]]

        fig = go.Figure()

        # Add radar traces for both players
        fig.add_trace(go.Scatterpolar(
            r=player1_values,
            theta=categories,
            fill='toself',
            name=player1,
            hovertext=player1_hover,
            hoverinfo="text",
            line_color="#00A9E0",
        ))
        fig.add_trace(go.Scatterpolar(
            r=player2_values,
            theta=categories,
            fill='toself',
            name=player2,
            hovertext=player2_hover,
            hoverinfo="text",
            line_color="#1CD097",
        ))

        # Layout for radar chart with transparent background
        fig.update_layout(
            polar=dict(
                bgcolor='rgba(0,0,0,0)',
                radialaxis=dict(visible=True, range=[0, 100], showline=True, showgrid=True),
                angularaxis=dict(tickfont=dict(size=12, color='white')),
            ),
            showlegend=True,
            legend=dict(font=dict(color='white')),
            font=dict(color='white'),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
        )

        return fig
    except Exception as e:
        st.error(f"Error plotting radar chart: {str(e)}")
        return None

# Main app logic
def main():
    # Add a toggle for Day/Night mode
    if 'mode' not in st.session_state:
        st.session_state['mode'] = "Night"
    
    st.session_state['mode'] = "Night" if st.sidebar.checkbox("Night Mode", value=True) else "Day"
    
    load_css(st.session_state['mode'])

    st.title("XSEED Analytics App")

    # Create 40 file upload buttons for each match
    uploaded_files = []
    for match in range(1, 41):
        uploaded_files.append(st.file_uploader(f"Upload CSV for Match {match}", type="csv", key=f"match_{match}"))

    # Process the uploaded files
    if any(uploaded_files):
        try:
            data = load_data(uploaded_files)
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

                    # Radar Chart Section
                    st.header("Player Comparison")
                    players = combined_stats.index.tolist()
                    player1 = st.selectbox("Select first player:", players)
                    player2 = st.selectbox("Select second player:", players, index=1)

                    # Define default attributes for radar chart
                    default_attributes = [
                        "km_covered", "Sprints Distance (m)", "max_speed",
                        "xT", "xG", "technical_load", "passes_sx", "passes_dx"
                    ]
                    
                    attribute_options = [get_stat_type(col, non_cumulative_cols) for col in per_90_stats.columns]

                    selected_attributes = st.multiselect(
                        "Select attributes to compare:",
                        options=attribute_options,
                        default=[get_stat_type(attr, non_cumulative_cols) for attr in default_attributes]
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

                            fig = plot_radar_chart_plotly(player1, player2, combined_stats, attributes, per_90_stats)
                            if fig is not None:
                                st.plotly_chart(fig)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.stop()

if __name__ == "__main__":
    main()
