import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def load_data(file):
    try:
        df = pd.read_csv(file)
        required_columns = ['Player', 'Minutes']
        if not all(col in df.columns for col in required_columns):
            st.error(f"CSV file must contain at least these columns: {', '.join(required_columns)}")
            return None
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def calculate_stats(df, non_cumulative_cols):
    try:
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
    except Exception as e:
        st.error(f"Error calculating stats: {str(e)}")
        return None, None

def calculate_percentiles(stats):
    return stats.rank(pct=True) * 100

def get_stat_type(col_name, non_cumulative_cols):
    if col_name in non_cumulative_cols:
        return col_name
    else:
        return f"{col_name} (per 90)"

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

def main():
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
                
                selected_attributes = st.multiselect(
                    "Select attributes to compare:",
                    options=attribute_options,
                    default=attribute_options[:5]  # Select first 5 attributes by default
                )

                if st.button("Compare Players"):
                    if len(selected_attributes) < 3:
                        st.warning("Please select at least 3 attributes for comparison.")
                    else:
                        # Strip the type indicator for actual data access
                        attributes = [attr.split(" (per 90)")[0] for attr in selected_attributes]
                        
                        # Display table comparison
                        comparison = pd.DataFrame({
                            player1: per_90_stats.loc[player1, attributes],
                            player2: per_90_stats.loc[player2, attributes]
                        })
                        st.write(comparison)
                        
                        # Display radar chart
                        fig = plot_radar_chart(player1, player2, per_90_stats, attributes)
                        if fig is not None:
                            st.pyplot(fig)

if __name__ == "__main__":
    main()
