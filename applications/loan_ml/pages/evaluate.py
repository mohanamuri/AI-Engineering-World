import streamlit as st


def render():
    st.header("📈 Model Evaluation")

    st.info(
        "Accuracy,\n"
        "Precision,\n"
        "Recall,\n"
        "Confusion Matrix,\n"
        "ROC Curve."
    )