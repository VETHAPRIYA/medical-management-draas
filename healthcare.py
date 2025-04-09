import streamlit as st
import pandas as pd
from pathlib import Path

# Paths to Excel files
inventory_file = Path("inventory.xlsx")
sales_file = Path("sales.xlsx")
patients_file = Path("patients.xlsx")

# Paths to Background Images
supply_chain_background = "scm.jpg"
medical_shop_background = "medic store.jpg"
patient_management_background = "patient.jpg"
medical_records_background = "medical_records.jpg"


# Initialize or add missing columns to each Excel file
def initialize_file(file, columns):
    if not file.exists():
        df = pd.DataFrame(columns=columns)
        df.to_excel(file, index=False)
    else:
        df = pd.read_excel(file)
        for column in columns:
            if column not in df.columns:
                df[column] = pd.NA
        df.to_excel(file, index=False)


# Ensure each file has the required columns
initialize_file(inventory_file, ["item", "initial_quantity", "quantity", "price"])
initialize_file(sales_file, ["patient", "item", "quantity", "total"])
initialize_file(patients_file, ["name", "age", "diagnosis", "medical_history"])


# Functions for reading and writing to Excel
def load_data(file):
    return pd.read_excel(file)


def save_data(file, df):
    df.to_excel(file, index=False)


# Set background image based on the module
def set_background(image_path):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("file://{image_path}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# Title and Navigation
st.title("Medical Management System")

# Sidebar for Navigation
st.sidebar.title("Navigation")
section = st.sidebar.selectbox("Choose Module", (
"Supply Chain", "Medical Shop", "Patient Management", "Billing and Invoicing", "Inventory Management"))

# Load Data
inventory_df = load_data(inventory_file)
sales_df = load_data(sales_file)
patients_df = load_data(patients_file)

# Display and functionality for each module
if section == "Supply Chain":
    set_background(supply_chain_background)
    st.header("Supply Chain Management")

    # Display Inventory with Low Inventory Alerts
    st.subheader("Current Inventory")
    low_stock_alerts = []
    for index, row in inventory_df.iterrows():
        if row['quantity'] <= 0.2 * row['initial_quantity']:
            low_stock_alerts.append(row['item'])
    if low_stock_alerts:
        st.warning(f"Low Inventory Alert: {', '.join(low_stock_alerts)} are below 20% of initial stock.")
    st.write(inventory_df)

    # Add New Stock
    st.subheader("Add New Stock")
    item = st.text_input("Item Name", key="supply_item_name")
    initial_quantity = st.number_input("Initial Quantity", min_value=1, step=1, key="supply_initial_quantity")
    quantity = st.number_input("Additional Quantity", min_value=1, step=1, key="supply_additional_quantity")
    price = st.number_input("Price per unit", min_value=0.0, step=0.1, key="supply_price")
    if st.button("Add Stock", key="supply_add_stock"):
        if item in inventory_df['item'].values:
            inventory_df.loc[inventory_df['item'] == item, 'quantity'] += quantity
        else:
            new_row = pd.DataFrame(
                {"item": [item], "initial_quantity": [initial_quantity], "quantity": [initial_quantity + quantity],
                 "price": [price]})
            inventory_df = pd.concat([inventory_df, new_row], ignore_index=True)
        save_data(inventory_file, inventory_df)
        st.success("Stock added successfully")

elif section == "Medical Shop":
    set_background(medical_shop_background)
    st.header("Medical Shop")

    # Display Sales
    st.subheader("Sales Records")
    st.write(sales_df)

    # Process Sale for a Patient
    st.subheader("Process Sale")
    patient = st.selectbox("Select Patient", patients_df["name"], key="sale_patient_selectbox")
    sale_item = st.selectbox("Item", inventory_df["item"], key="sale_item_selectbox")
    sale_quantity = st.number_input("Quantity", min_value=1, step=1, key="sale_quantity")
    sale_price = inventory_df.loc[inventory_df['item'] == sale_item, 'price'].values[0]
    if st.button("Add Sale", key="add_sale_button"):
        if sale_quantity <= inventory_df.loc[inventory_df['item'] == sale_item, 'quantity'].values[0]:
            new_sale = pd.DataFrame({"patient": [patient], "item": [sale_item], "quantity": [sale_quantity],
                                     "total": [sale_quantity * sale_price]})
            sales_df = pd.concat([sales_df, new_sale], ignore_index=True)
            inventory_df.loc[inventory_df['item'] == sale_item, 'quantity'] -= sale_quantity
            save_data(sales_file, sales_df)
            save_data(inventory_file, inventory_df)
            st.success("Sale processed successfully for patient")
        else:
            st.error("Insufficient stock for this sale")

elif section == "Patient Management":
    set_background(patient_management_background)
    st.header("Patient Management")

    # Display Patients and Medical History
    st.subheader("Patient Records")
    st.write(patients_df[["name", "age", "diagnosis", "medical_history"]])

    # Add New Patient
    st.subheader("Add New Patient")
    patient_name = st.text_input("Patient Name", key="new_patient_name")
    patient_age = st.number_input("Age", min_value=1, step=1, key="new_patient_age")
    patient_diagnosis = st.text_input("Diagnosis", key="new_patient_diagnosis")
    patient_history = st.text_area("Medical History", key="new_patient_history")
    if st.button("Add Patient", key="add_patient_button"):
        new_patient = pd.DataFrame({
            "name": [patient_name],
            "age": [patient_age],
            "diagnosis": [patient_diagnosis],
            "medical_history": [patient_history]
        })
        patients_df = pd.concat([patients_df, new_patient], ignore_index=True)
        save_data(patients_file, patients_df)
        st.success("Patient added successfully")

elif section == "Billing and Invoicing":
    set_background(medical_shop_background)
    st.header("Billing and Invoicing")

    # Display Billing Records
    st.subheader("Billing Records")
    st.write(sales_df)

    # Create Invoice
    st.subheader("Create Invoice")
    patient = st.selectbox("Select Patient for Invoice", patients_df["name"], key="invoice_patient_selectbox")
    invoice_items = sales_df[sales_df["patient"] == patient]
    if not invoice_items.empty:
        total_amount = invoice_items["total"].sum()
        st.write(invoice_items)
        st.write(f"Total Invoice Amount: ${total_amount:.2f}")
        if st.button("Generate Invoice", key="generate_invoice_button"):
            st.success(f"Invoice generated for {patient} with total amount: ${total_amount:.2f}")
    else:
        st.error("No sales found for this patient.")

elif section == "Inventory Management":
    set_background(supply_chain_background)
    st.header("Inventory Management")

    # Display Inventory and Stock Levels
    st.subheader("Current Inventory")
    st.write(inventory_df)

    # Restock Items
    st.subheader("Restock Items")
    item = st.selectbox("Select Item to Restock", inventory_df["item"], key="restock_item_selectbox")
    restock_quantity = st.number_input("Restock Quantity", min_value=1, step=1, key="restock_quantity")
    if st.button("Restock Item", key="restock_button"):
        inventory_df.loc[inventory_df['item'] == item, 'quantity'] += restock_quantity
        save_data(inventory_file, inventory_df)
        st.success(f"Restocked {restock_quantity} units of {item}.")