import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

# Function to load CSS based on mode
def load_css(mode):
    if mode == "Night":
        st.markdown("""
        <style>
        .stApp {
            background-color: #0e1117;
            color: white;
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
        /* Styling tables */
        .dataframe {
            color: white !important;
            background-color: #0e1117 !important;
        }
        .stDataFrame {
            background-color: #0e1117;
            color: white;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        .stApp {
            background-color: #f8f9fa;
            color: black;
        }
        div[data-baseweb="tag"] {
            background-color: #007bff !important;
        }
        div[data-baseweb="tag"] span[title="×"] {
            color: black !important;
        }
        div[data-baseweb="multiselect"] > div {
            background-color: #ffffff;
        }
        .stButton>button {
            background-color: #007bff;
            color: white;
        }
        /* Styling tables */
        .dataframe {
            color: black !important;
            background-color: #f8f9fa !important;
        }
        .stDataFrame {
            background-color: #ffffff;
            color: black;
        }
        </style>
        """, unsafe_allow_html=True)

# Function to load data
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

# Function to calculate stats
def calculate_stats(df, non_cumulative_cols):
    try:
        cumulative_df = df.drop(columns=non_cumulative_cols)
        non_cumulative_df = df[['Player'] + non_cumulative_cols]
        
        cumulative_stats = cumulative_df.groupby('Player').sum(numeric_only=True)
        non_cumulative_stats = non_cumulative_df.groupby('Player').mean()
        
        combined_stats = pd.concat([cumulative_stats, non_cumulative_stats], axis=1)
        
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

# Function to plot radar chart
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
        fig.patch.set_facecolor('black')
        ax.set_facecolor('black')
        
        ax.plot(angles, values1, 'o-', linewidth=2, label=player1, color='#00A9E0')
        ax.fill(angles, values1, alpha=0.25, color='#00A9E0')
        ax.plot(angles, values2, 'o-', linewidth=2, label=player2, color='#1CD097')
        ax.fill(angles, values2, alpha=0.25, color='#1CD097')
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(attributes)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20th', '40th', '60th', '80th', '100th'])
        
        plt.setp(ax.get_yticklabels(), color='white', fontname='Montserrat')
        plt.setp(ax.get_xticklabels(), color='white', fontname='Montserrat')
        
        legend = plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
        plt.setp(legend.get_texts(), color='white', fontname='Montserrat')
        
        plt.title(f"Percentile Comparison: {player1} vs {player2}", fontsize=16, fontweight='bold', color='white', fontname='Montserrat')
        
        ax.grid(color='gray', alpha=0.5)
        ax.spines['polar'].set_visible(False)
        
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

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        try:
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

                    # Radar Chart Section
                    st.header("Player Comparison")
                    players = combined_stats.index.tolist()
                    player1 = st.selectbox("Select first player:", players)
                    player2 = st.selectbox("Select second player:", players, index=1)

                    # Define default attributes for radar chart
                    default_attributes = [
                        "km_covered (per 90)", "Sprints Distance (per 90)", "max_speed",
                        "xT (per 90)", "xG (per 90)", "technical_load (per 90)", "passes_sx (per 90)", "passes_dx (per 90)"
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

                            fig = plot_radar_chart(player1, player2, per_90_stats, attributes)
                            if fig is not None:
                                                               st.pyplot(fig)

                    # Interactive Scatter Plot Comparison Section
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
            st.stop()  # To avoid the app from running further and encountering additional errors

if __name__ == "__main__":
    main()

