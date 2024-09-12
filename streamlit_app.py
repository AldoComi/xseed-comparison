import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_data(file):
    df = pd.read_csv(file)
    return df

def calculate_stats(df):
    # Group by player and sum up all numeric columns
    cumulative_stats = df.groupby('Player').sum(numeric_only=True)
    
    # Calculate minutes played for each player
    minutes_played = cumulative_stats['Minutes']
    
    # Calculate per 90 minutes stats
    per_90_stats = cumulative_stats.div(minutes_played, axis=0) * 90
    
    return cumulative_stats, per_90_stats

def plot_radar_chart(player1, player2, stats, attributes):
    values1 = stats.loc[player1, attributes].values.flatten().tolist()
    values2 = stats.loc[player2, attributes].values.flatten().tolist()
    
    values1 += values1[:1]
    values2 += values2[:1]
    
    angles = [n / float(len(attributes)) * 2 * 3.141593 for n in range(len(attributes))]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
    ax.plot(angles, values1, 'o-', linewidth=2, label=player1)
    ax.fill(angles, values1, alpha=0.25)
    ax.plot(angles, values2, 'o-', linewidth=2, label=player2)
    ax.fill(angles, values2, alpha=0.25)
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(attributes)
    ax.set_ylim(0, max(max(values1), max(values2)))
    
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    return fig

def main():
    st.title("Football Player Statistics App")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        data = load_data(uploaded_file)
        cumulative_stats, per_90_stats = calculate_stats(data)

        st.header("Player Statistics")
        stat_type = st.radio("Select statistic type:", ("Cumulative", "Per 90 minutes"))
        
        if stat_type == "Cumulative":
            st.dataframe(cumulative_stats)
        else:
            st.dataframe(per_90_stats)

        st.header("Player Comparison")
        players = per_90_stats.index.tolist()
        player1 = st.selectbox("Select first player:", players)
        player2 = st.selectbox("Select second player:", players, index=1)

        attributes = st.multiselect("Select attributes to compare:", 
                                    per_90_stats.columns.tolist(),
                                    default=["Goals", "Assists", "Passes", "Tackles"])

        if st.button("Compare Players"):
            fig = plot_radar_chart(player1, player2, per_90_stats, attributes)
            st.pyplot(fig)

if __name__ == "__main__":
    main()
