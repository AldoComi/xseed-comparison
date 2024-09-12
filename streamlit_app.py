import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# ... (keep all other functions as they were)

def plot_radar_chart(player1, player2, stats, attributes):
    try:
        percentile_stats = calculate_percentiles(stats)
        
        values1 = percentile_stats.loc[player1, attributes].values.flatten().tolist()
        values2 = percentile_stats.loc[player2, attributes].values.flatten().tolist()
        
        values1 += values1[:1]
        values2 += values2[:1]
        
        angles = [n / float(len(attributes)) * 2 * np.pi for n in range(len(attributes))]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        fig.patch.set_facecolor('black')  # Black background for the entire figure
        ax.set_facecolor('black')  # Black background for the plot area
        
        ax.plot(angles, values1, 'o-', linewidth=2, label=player1, color='#00A9E0')  # Light blue
        ax.fill(angles, values1, alpha=0.25, color='#00A9E0')
        ax.plot(angles, values2, 'o-', linewidth=2, label=player2, color='#1CD097')  # Light green
        ax.fill(angles, values2, alpha=0.25, color='#1CD097')
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(attributes)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20th', '40th', '60th', '80th', '100th'])
        
        # Customize text color and font
        plt.setp(ax.get_yticklabels(), color='white', fontname='Montserrat')
        plt.setp(ax.get_xticklabels(), color='white', fontname='Montserrat')
        
        # Customize legend
        legend = plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.setp(legend.get_texts(), color='white', fontname='Montserrat')
        
        plt.title(f"Percentile Comparison: {player1} vs {player2}", fontsize=16, fontweight='bold', color='white', fontname='Montserrat')
        
        # Customize grid
        ax.grid(color='gray', alpha=0.5)
        ax.spines['polar'].set_visible(False)
        
        return fig
    except Exception as e:
        st.error(f"Error plotting radar chart: {str(e)}")
        return None

def plot_interactive_scatter(stats, x_var, y_var, highlight_players=None):
    try:
        fig = px.scatter(stats, x=x_var, y=y_var, hover_name=stats.index,
                         hover_data={x_var: ':.2f', y_var: ':.2f'},
                         title=f"{y_var} vs {x_var}")
        
        # Set all points to light blue
        fig.update_traces(marker=dict(color='#00A9E0', size=10))
        
        if highlight_players:
            highlights = stats.loc[highlight_players]
            highlight_trace = px.scatter(highlights, x=x_var, y=y_var, hover_name=highlights.index,
                                         hover_data={x_var: ':.2f', y_var: ':.2f'}).data[0]
            
            # Set highlighted points to light green
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
            title_font_size=20
        )
        return fig
    except Exception as e:
        st.error(f"Error plotting interactive scatter: {str(e)}")
        return None

# ... (keep the main function and the rest of the code as it was)

if __name__ == "__main__":
    main()
