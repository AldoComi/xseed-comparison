# Importing libraries
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
                required_columns = ['Player', 'Minutes', 'km_covered']
                if not all(col in df.columns for col in required_columns):
                    st.error(f"CSV file '{file.name}' must contain at least these columns: {', '.join(required_columns)}")
                    return None
                df['Match'] = f'M{files.index(file) + 1}'  # Add match label
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

# Function to plot distance breakdown chart
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

# Function to plot interactive scatter
def plot_interactive_scatter(stats, x_var, y_var, highlight_players=None):
    try:
        fig = px.scatter(stats, x=x_var, y=y_var, hover_name=stats.index,
                         hover_data={x_var: ':.2f', y_var: ':.2f'},
                         title=f"{y_var} vs {x_var}")
        
        fig.update_traces(marker=dict(color='#00A9E0', size=10))
        
        if highlight_players:
            highlights = stats.loc[highlight_players]
            highlight_trace = px.scatter(highlights, x=x_var, y=y_var, hover_name=highlights.index,
                                         hover_data={x_var: ':.2f', y_var: ':.2f'}).data[0]
            
            highlight_trace.marker.color = '#1CD097'
            highlight_trace.marker.size = 15
            fig.add_trace(highlight_trace)
            
            for player in highlight_players:
                fig.add_annotation(x=stats.loc[player, x_var],
                                   y=stats.loc[player, y_var],
                                   text=player,
                                   showarrow=True,
                                   arrowhead=2)
        
        fig.update_layout(
            height=600,
            font_family="Montserrat",
            title_font_family="Montserrat",
            title_font_size=20,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='Gray')
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='Gray')
        
        return fig
    except Exception as e:
        st.error(f"Error plotting interactive scatter: {str(e)}")
        return None

# Function to plot team stat trend with the ability to select the stat
def plot_team_stat_trend(data, selected_stat, mode):
    if mode == 'Total Stats':
        # Group by match and calculate total selected statistic for each match
        match_stats = data.groupby('Match')[selected_stat].sum().reset_index()
        title = f"Total {selected_stat.replace('_', ' ').capitalize()} Covered by Team Across Matches"
    else:
        # Calculate average stat per player for each match
        match_stats = data.groupby('Match')[selected_stat].mean().reset_index()
        title = f"Average {selected_stat.replace('_', ' ').capitalize()} per Player Across Matches"

    fig = px.bar(match_stats, x='Match', y=selected_stat, 
                 title=title,
                 labels={selected_stat: f'{selected_stat.replace("_", " ").capitalize()}', 'Match': 'Matches'})
    
    fig.update_layout(
        height=400,
        font_family="Montserrat",
        font_color='white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title='Match',
        yaxis_title=f'{selected_stat.replace("_", " ").capitalize()}'
    )
    return fig

# Function to plot player stat trend
def plot_player_stat_trend(data, selected_stat, player, mode, per_90_stats):
    if mode == 'Match Stats':
        # Extract stats for selected player per match
        player_data = data[data['Player'] == player].set_index('Match')[selected_stat].reset_index()
        title = f"{selected_stat.replace('_', ' ').capitalize()} Trend for {player} Across Matches"
    else:
        # Extract per 90 stats for selected player per match
        player_data = per_90_stats[per_90_stats.index == player][selected_stat].reset_index()
        title = f"{selected_stat.replace('_', ' ').capitalize()} (Per 90) Trend for {player} Across Matches"

    fig = px.bar(player_data, x='Match', y=selected_stat, 
                  title=title, 
                  labels={selected_stat: f'{selected_stat.replace("_", " ").capitalize()}', 'Match': 'Matches'})
    
    fig.update_layout(
        height=400,
        font_family="Montserrat",
        font_color='white',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title='Match',
        yaxis_title=f'{selected_stat.replace("_", " ").capitalize()}'
    )
    return fig

# Main app logic
def main():
    # Add a toggle for Day/Night mode
    if 'mode' not in st.session_state:
        st.session_state['mode'] = "Night"
    
    st.session_state['mode'] = "Night" if st.sidebar.checkbox("Night Mode", value=True) else "Day"
    
    load_css(st.session_state['mode'])

    st.title("XSEED Analytics App")

    # Initialize session state to keep track of match uploads
    if 'num_matches' not in st.session_state:
        st.session_state['num_matches'] = 1

    uploaded_files = []
    for match in range(1, st.session_state['num_matches'] + 1):
        uploaded_files.append(st.file_uploader(f"Upload CSV for Match {match}", type="csv", key=f"match_{match}"))

    # Button to add new match uploaders
    if st.button("Add another match"):
        if st.session_state['num_matches'] < 40:
            st.session_state['num_matches'] += 1
        else:
            st.warning("Maximum number of 40 matches reached.")

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

                    # Team Stat Trend with Stat Selector
                    st.header("Team Stat Trend Across Matches")
                    available_stats = ['km_covered', 'Sprints Distance (m)', 'High Intensity Running (m) (> 18 km/h)', 'xG', 'xT', 'shots_sx', 'shots_dx','passes_sx','passes_dx']  # Add more stats as needed
                    selected_stat = st.selectbox("Select the statistic to view:", available_stats)
                    mode = st.radio("Select Mode:", ['Total Stats', 'Per Player'])

                    team_stat_fig = plot_team_stat_trend(data, selected_stat, mode)
                    if team_stat_fig is not None:
                        st.plotly_chart(team_stat_fig, use_container_width=True)

                    # Player Stat Trend with Stat Selector
                    st.header("Player Stat Trend Across Matches")
                    player = st.selectbox("Select player:", combined_stats.index.tolist())
                    player_stat = st.selectbox("Select the statistic for the player:", available_stats)
                    player_mode = st.radio("Select Player Mode:", ['Match Stats', 'Per 90 Stats'])

                    player_stat_fig = plot_player_stat_trend(data, player_stat, player, player_mode, per_90_stats)
                    if player_stat_fig is not None:
                        st.plotly_chart(player_stat_fig, use_container_width=True)

                    # Distance Covered Breakdown chart
                    st.header("Distance Covered Breakdown")
                    distance_fig = plot_distance_breakdown(data)
                    if distance_fig is not None:
                        st.plotly_chart(distance_fig, use_container_width=True)

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

                    # Interactive Scatter Plot
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

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.stop()

if __name__ == "__main__":
    main()
