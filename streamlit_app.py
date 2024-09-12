import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# ... [other functions remain unchanged] ...

def plot_radar_chart(player1, player2, stats, attributes):
    # Filter attributes to only include those present in the stats DataFrame
    valid_attributes = [attr for attr in attributes if attr in stats.columns]
    
    if not valid_attributes:
        st.error("No valid attributes selected for the radar chart. Please select different attributes.")
        return None

    percentile_stats = calculate_percentiles(stats)
    
    values1 = percentile_stats.loc[player1, valid_attributes].values.flatten().tolist()
    values2 = percentile_stats.loc[player2, valid_attributes].values.flatten().tolist()
    
    values1 += values1[:1]
    values2 += values2[:1]
    
    angles = [n / float(len(valid_attributes)) * 2 * np.pi for n in range(len(valid_attributes))]
    angles += angles[:1]

    plt.style.use('seaborn')
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    ax.plot(angles, values1, 'o-', linewidth=2, label=player1)
    ax.fill(angles, values1, alpha=0.25)
    ax.plot(angles, values2, 'o-', linewidth=2, label=player2)
    ax.fill(angles, values2, alpha=0.25)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(valid_attributes)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_yticklabels(['20th', '40th', '60th', '80th', '100th'])
    
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    plt.title(f"Percentile Comparison: {player1} vs {player2}", fontsize=16, fontweight='bold')
    
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontname('Montserrat')
    
    return fig

def main():
    # ... [previous parts of main function remain unchanged] ...

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
        if fig is not None:
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
