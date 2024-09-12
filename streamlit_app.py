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
        
        # Rest of the function remains the same
        # ...

    except KeyError as e:
        st.error(f"Error: {str(e)}")
        return None

def main():
    # ... (previous code remains the same)

    if st.button("Compare Players"):
        if len(selected_attributes) < 3:
            st.warning("Please select at least 3 attributes for comparison.")
        else:
            # Strip the type indicator for actual data access
            attributes = [attr.split(" (")[0] for attr in selected_attributes]
            fig = plot_radar_chart(player1, player2, per_90_stats, attributes)
            if fig is not None:
                st.pyplot(fig)

    # ... (rest of the main function remains the same)

if __name__ == "__main__":
    main()
