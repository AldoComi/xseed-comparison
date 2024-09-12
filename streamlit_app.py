import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# ... (previous functions remain unchanged)

def plot_radar_chart(player1, player2, stats, attributes):
    try:
        percentile_stats = calculate_percentiles(stats)
        
        # Check if players exist in the data
        if player1 not in percentile_stats.index or player2 not in percentile_stats.index:
            missing_players = [p for p in [player1, player2] if p not in percentile_stats.index]
            raise KeyError(f"Player(s) not found in data: {', '.join(missing_players)}")
        
        # Check if all attributes exist in the data
        missing_attributes = [attr for attr in attributes if attr not in percentile_stats.columns]
        if missing_attributes:
            raise KeyError(f"Attribute(s) not found in data: {', '.join(missing_attributes)}")
        
        values1 = percentile_stats.loc[player1, attributes].values.flatten().tolist()
        values2 = percentile_stats.loc[player2, attributes].values.flatten().tolist()
        
        values1 += values1[:1]
        values2 += values2[:1]
        
        angles = [n / float(len(attributes)) * 2 * np.pi for n in range(len(attributes))]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        fig.patch.set_facecolor('#2c2c2c')  # Dark background for the entire figure
        ax.set_facecolor('#2c2c2c')  # Dark background for the plot area
        
        ax.plot(angles, values1, 'o-', linewidth=2, label=player1, color='#3498db')  # Light blue
        ax.fill(angles, values1, alpha=0.25, color='#3498db')
        ax.plot(angles, values2, 'o-', linewidth=2, label=player2, color='#e74c3c')  # Light red
        ax.fill(angles, values2, alpha=0.25, color='#e74c3c')
        
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

# ... (rest of the code remains unchanged)

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

    # ... (rest of the main function remains unchanged)

if __name__ == "__main__":
    main()
