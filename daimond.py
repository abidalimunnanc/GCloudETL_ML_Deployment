import streamlit as st
from google.cloud import aiplatform

aiplatform.init(project="gcloud-flow-123", location="us-central1")
ENDPOINT_ID = "xxxxxxxxxxxxxxxxx"
endpoint = aiplatform.Endpoint(endpoint_name=f"projects/xxxxxxxxxxxxxxxx/locations/us-central1/endpoints/{ENDPOINT_ID}")

st.title("💎 Diamond Price Predictor")

carat = st.number_input("Carat", min_value=0.1, step=0.01)
cut = st.selectbox("Cut", ["Fair", "Good", "Very Good", "Premium", "Ideal"])
color = st.text_input("Color (D-Z)")
clarity = st.text_input("Clarity (e.g. SI1, VS2)")
depth = st.number_input("Depth", step=0.1)
table = st.number_input("Table", step=0.1)
x = st.number_input("X", step=0.01)
y = st.number_input("Y", step=0.01)
z = st.number_input("Z", step=0.01)

if st.button("Predict Price"):
    instance = [{
        "carat": carat,
        "cut": cut,
        "color": color,
        "clarity": clarity,
        "depth": depth,
        "table": table,
        "x": x,
        "y": y,
        "z": z
    }]
    prediction = endpoint.predict(instances=instance)
    price = prediction.predictions[0]["value"]
    st.success(f"💰 Predicted Diamond Price: ${price:,.2f}")
