import streamlit as st


def run():

    st.title("🧠 Loan Eligibility - Deep Learning")

    st.info("Deep Learning Application")

    salary = st.number_input("Salary", 5000, 500000, 50000)

    experience = st.slider("Experience", 0, 30, 5)

    credit = st.slider("Credit Score", 300, 900, 700)

    if st.button("Predict"):

        st.success("Neural Network Prediction Coming Soon")