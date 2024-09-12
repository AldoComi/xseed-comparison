import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

def load_data(file):
    df = pd.read_csv(file)
    return df

def calculate_stats(df):
    cumulative_stats = df.groupby('Player').sum(numeric_only=True)
    minutes_played = cumulative_stats['Minutes']
    
    # List of columns that should not be transformed to per-90
    non_per_90_cols = [
        'max_speed', 'Max Shot Power (km/h)', 'technical_load',
        'technical_load_left', 'technical_load_right', 'distance_per_minute (m)',
        'EDI (%)', 'Anaerobic Index (%)', 'Aerobic Index (%)'
    ]
    
    # Create a mask for columns that should be transformed to per-90
    per_90_mask = ~cumulative_stats.columns.isin(non_per_90_cols)
    
    # Apply per-90 transformation only to relevant columns
    per_90_stats = cumulative_stats.copy()
    per_90_stats.loc[:, per_90_mask] = per_90_stats.loc[:, per_90_mask].div(minutes_played, axis=0) * 90
    
    return cumulative_stats, per_90_stats

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

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
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
    plt.title(f"Percentile Comparison: {player1} vs {player2}")
    return fig

def plot_interactive_scatter(stats, x_var, y_var, highlight_players=None):
    fig = px.scatter(stats, x=x_var, y=y_var, hover_name=stats.index,
                     hover_data={x_var: ':.2f', y_var: ':.2f'},
                     title=f"{y_var} vs {x_var}")
    
    if highlight_players:
        highlights = stats.loc[highlight_pl
