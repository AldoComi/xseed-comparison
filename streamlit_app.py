import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def load_data(file):
    return pd.read_csv(file)

def plot_simple_chart(data):
    fig, ax = plt.subplots()
    ax.plot(data['x'], data['y'])
    return fig

def main():
    st.title("Simplified XSEED Analytics App")

    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        data = load_data(uploaded_file)
        st.write(data.head())

        if st.button("Generate Simple Plot"):
            fig = plot_simple_chart(data)
            st.pyplot(fig)

if __name__ == "__main__":
    main()
