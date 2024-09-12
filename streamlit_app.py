import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

def load_data(file):
    df = pd.read_csv(file)
    return df

def calculate_stats(df):
    # List of columns that should not be cumulated or transformed to per-90
    non_cumulative_cols = [
        'max_speed', 'Max Shot Power (km/h)', 'technical_load',
        'technical_load_left', 'technical_load_right', 'distance_per_minute (m)',
        'EDI (%)', 'Anaerobic Index (%)', 'Aerobic Index (%)'
    ]
    
    # Separate cumulative and non-cumulative stats
    cumulative_df = df.drop(columns=non_cumulative_cols)
    non_cumulative_df = df[['Player'] + non_cumulative_cols]
    
    # Calculate cumulative stats
    cumulative_stats = cumulative_df.groupby('Player').sum(numeric_only=True)
    
    # Calculate average for non-cumulative stats
    non_cumulative_stats = non_cumulative_df.groupby('Player').mean()
    
    # Combine cumulative and non-cumulative stats
    combined_stats = pd.concat([cumulative_stats, non_cumulative_stats], axis=1)
    
    # Calculate per-90 stats for cumulative columns only
    minutes_played = combined_stats['Minutes']
    per_90_stats = combined_stats.copy()
    per_90_cols = [col for col in cumulative_stats.columns if col not in non_cumulative_cols]
    per_90_stats[per_90_cols] = per_90_stats[per_90_cols].div(minutes_played, axis=0) * 90
    
    return combined_stats, per_90_stats

def calculate_percentiles(stats):
    return stats.rank(pct=True) * 100

def plot_radar_chart(player1, player2, stats, attributes):
    percentile_stats = calculate_percentiles(stats)
    
    values1 = percentile_stats.loc[player1, attributes].values.flatten().tolist()
    values2 = percentile_stats.loc[player2, attributes].values.flatten().tolist()
    
    values1 += values1[:1]
    values2 += values2[:1]
    
    angles = [n / float(len(attributes)) * 2 * np.pi for n in range(len(attributes))]
    angles += angles[:1]

    plt.style.use('seaborn')
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    ax.plot(angles, values1, 'o-', linewidth=2, label=player1)
    ax.fill(angles, values1, alpha=0.25)
    ax.plot(angles, values2, 'o-', linewidth=2, label=player2)
    ax.fill(angles, values2, alpha=0.25)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(attributes)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20th', '40th', '60th', '80th', '100th'])
    
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.title(f"Percentile Comparison: {player1} vs {player2}", fontsize=16, fontweight='bold')
    
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontname('Montserrat')
    
    return fig

def plot_interactive_scatter(stats, x_var, y_var, highlight_players=None):
    fig = px.scatter(stats, x=x_var, y=y_var, hover_name=stats.index,
                     hover_data={x_var: ':.2f', y_var: ':.2f'},
                     title=f"{y_var} vs {x_var}")
    
    if highlight_players:
        highlights = stats.loc[highlight_players]
        fig.add_trace(px.scatter(highlights, x=x_var, y=y_var, hover_name=highlights.index,
                                 hover_data={x_var: ':.2f', y_var: ':.2f'}).data[0])
        
        for player in highlight_players:
            fig.add_annotation(x=stats.loc[player, x_var],
                               y=stats.loc[player, y_var],
                               text=player,
                               showarrow=True,
                               arrowhead=2)
    
    fig.update_traces(marker=dict(size=10))
    fig.update_layout(
        height=600,
        font_family="Montserrat",
        title_font_family="Montserrat",
        title_font_size=20
    )
    return fig

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
