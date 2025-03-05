import streamlit as st
import pandas as pd

# Sample Data: Version & Deployment Status
data = {
    "Version": [1, 2, 3, 4],
    "MAE": [1.9354, 2.9011, 1.9354, 2.8661],
    "Status": ["Not Deployed", "Not Deployed", "Not Deployed", "Deployed"],
}

df = pd.DataFrame(data)

# Streamlit UI
st.title("Streamlit Deployment Status")

st.subheader("All Versions")
st.dataframe(df)

st.subheader("Deployed Version")
deployed_df = df[df["Status"] == "Deployed"]
st.dataframe(deployed_df)

# Show Min & Max MAE Values
st.subheader("Min & Max MAE Values")
st.write(f"🔹 **Min MAE:** {df['MAE'].min()}")
st.write(f"🔹 **Max MAE:** {df['MAE'].max()}")
