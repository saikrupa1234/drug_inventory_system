import streamlit as st
from database import (add_drug, get_all_drugs, update_drug, delete_drug,
                      add_supplier, get_all_suppliers, update_supplier, delete_supplier,
                      add_order, get_all_orders, update_inventory,
                      get_low_stock_drugs, get_expiring_soon_drugs,
                      search_drugs, search_suppliers, search_orders,
                      add_user, verify_user)
import random
import string

# Function to generate a simple CAPTCHA text
def generate_captcha():
    """Generates a random 6-character CAPTCHA string."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

# Initialize session state for authentication
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'  # Default to login page
if 'captcha_text' not in st.session_state:
    st.session_state['captcha_text'] = generate_captcha()

# Main app logic
def main_app():
    """Displays the main application interface."""
    st.title("Drug Inventory and Supply Chain Tracking System")

    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Drugs", "Suppliers", "Orders", "Reports", "Logout"])

    if page == "Logout":
        st.session_state['logged_in'] = False
        st.session_state['page'] = 'login'
        st.rerun()

    # Drugs Section
    if page == "Drugs":
        st.header("Manage Drugs")

        # Initialize clear search flag for drugs
        if 'clear_search_drugs' not in st.session_state:
            st.session_state['clear_search_drugs'] = False

        # Reset search term if clear flag is set
        if st.session_state['clear_search_drugs']:
            st.session_state['search_drugs'] = ""
            st.session_state['clear_search_drugs'] = False

        # Form to add a new drug
        with st.form("add_drug_form"):
            st.subheader("Add New Drug")
            name = st.text_input("Drug Name")
            batch_number = st.text_input("Batch Number")
            expiry_date = st.date_input("Expiry Date")
            manufacturer = st.text_input("Manufacturer")
            quantity = st.number_input("Quantity", min_value=0)
            storage_conditions = st.text_area("Storage Conditions")
            submit = st.form_submit_button("Add Drug")

            if submit:
                add_drug(name, batch_number, str(expiry_date), manufacturer, quantity, storage_conditions)
                st.success("Drug added successfully!")

        # Search and display drugs
        st.subheader("All Drugs")
        search_term = st.text_input("Search Drugs by Name", key="search_drugs")
        if search_term:
            drugs = search_drugs(search_term)
        else:
            drugs = get_all_drugs()
        if not drugs:
            st.write("No drugs found.")
        for drug in drugs:
            st.write(f"**{drug['name']}** (Batch: {drug['batch_number']}, Expiry: {drug['expiry_date']}, Qty: {drug['quantity']})")
            if st.button(f"Delete {drug['name']}", key=f"delete_drug_{drug['drug_id']}"):
                delete_drug(drug['drug_id'])
                st.rerun()
        if search_term and st.button("Clear Search", key="clear_search_drugs_button"):
            st.session_state['clear_search_drugs'] = True
            st.rerun()

    # Suppliers Section
    elif page == "Suppliers":
        st.header("Manage Suppliers")

        # Initialize clear search flag for suppliers
        if 'clear_search_suppliers' not in st.session_state:
            st.session_state['clear_search_suppliers'] = False

        # Reset search term if clear flag is set
        if st.session_state['clear_search_suppliers']:
            st.session_state['search_suppliers'] = ""
            st.session_state['clear_search_suppliers'] = False

        # Form to add a new supplier
        with st.form("add_supplier_form"):
            st.subheader("Add New Supplier")
            name = st.text_input("Supplier Name")
            contact_info = st.text_input("Contact Info")
            address = st.text_area("Address")
            submit = st.form_submit_button("Add Supplier")

            if submit:
                add_supplier(name, contact_info, address)
                st.success("Supplier added successfully!")

        # Search and display suppliers
        st.subheader("All Suppliers")
        search_term = st.text_input("Search Suppliers by Name", key="search_suppliers")
        if search_term:
            suppliers = search_suppliers(search_term)
        else:
            suppliers = get_all_suppliers()
        if not suppliers:
            st.write("No suppliers found.")
        for supplier in suppliers:
            st.write(f"**{supplier['name']}** (Contact: {supplier['contact_info']})")
            if st.button(f"Delete {supplier['name']}", key=f"delete_supplier_{supplier['supplier_id']}"):
                delete_supplier(supplier['supplier_id'])
                st.rerun()
        if search_term and st.button("Clear Search", key="clear_search_suppliers_button"):
            st.session_state['clear_search_suppliers'] = True
            st.rerun()

    # Orders Section
    elif page == "Orders":
        st.header("Manage Orders")

        # Initialize clear search flag for orders
        if 'clear_search_orders' not in st.session_state:
            st.session_state['clear_search_orders'] = False

        # Reset search term if clear flag is set
        if st.session_state['clear_search_orders']:
            st.session_state['search_orders'] = ""
            st.session_state['clear_search_orders'] = False

        # Form to place a new order
        with st.form("add_order_form"):
            st.subheader("Place New Order")
            suppliers = get_all_suppliers()
            supplier_options = {supplier['name']: supplier['supplier_id'] for supplier in suppliers}
            selected_supplier = st.selectbox("Select Supplier", list(supplier_options.keys()))
            status = st.selectbox("Status", ["Pending", "Received"])

            # Select drugs and quantities
            drugs = get_all_drugs()
            selected_drugs = st.multiselect("Select Drugs", [drug['name'] for drug in drugs])
            quantities = {}
            for drug_name in selected_drugs:
                drug_id = next(drug['drug_id'] for drug in drugs if drug['name'] == drug_name)
                quantities[drug_name] = st.number_input(f"Quantity for {drug_name}", min_value=1, key=f"qty_{drug_id}")

            submit = st.form_submit_button("Place Order")

            if submit:
                items = [{'drug_id': next(drug['drug_id'] for drug in drugs if drug['name'] == drug_name), 
                          'quantity': quantities[drug_name]} for drug_name in selected_drugs]
                add_order(supplier_options[selected_supplier], status, items)
                st.success("Order placed successfully!")

        # Search and display orders
        st.subheader("All Orders")
        search_term = st.text_input("Search Orders by ID or Supplier Name", key="search_orders")
        if search_term:
            orders = search_orders(search_term)
        else:
            orders = get_all_orders()
        if not orders:
            st.write("No orders found.")
        for order in orders:
            st.write(f"Order ID: {order['order_id']}, Date: {order['order_date']}, Supplier: {order['supplier_name']}, Status: {order['status']}")
        if search_term and st.button("Clear Search", key="clear_search_orders_button"):
            st.session_state['clear_search_orders'] = True
            st.rerun()

    # Reports Section
    elif page == "Reports":
        st.header("Reports")

        # Low stock drugs
        st.subheader("Low Stock Drugs")
        low_stock = get_low_stock_drugs()
        for drug in low_stock:
            st.write(f"**{drug['name']}** (Qty: {drug['quantity']})")

        # Expiring soon drugs
        st.subheader("Drugs Expiring Soon")
        expiring_soon = get_expiring_soon_drugs()
        for drug in expiring_soon:
            st.write(f"**{drug['name']}** (Expiry: {drug['expiry_date']})")

# Login Page
def login_page():
    """Displays the login page."""
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            if verify_user(username, password):
                st.session_state['logged_in'] = True
                st.session_state['page'] = 'main'
                st.rerun()
            else:
                st.error("Invalid username or password.")

    if st.button("Go to Signup"):
        st.session_state['page'] = 'signup'
        st.rerun()

# Signup Page with CAPTCHA
def signup_page():
    """Displays the signup page with CAPTCHA validation."""
    st.title("Signup")
    with st.form("signup_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        # CAPTCHA
        st.write(f"CAPTCHA: **{st.session_state['captcha_text']}**")
        captcha_input = st.text_input("Re-enter the CAPTCHA text")

        submit = st.form_submit_button("Signup")

        if submit:
            if captcha_input != st.session_state['captcha_text']:
                st.error("CAPTCHA validation failed. Please try again.")
                st.session_state['captcha_text'] = generate_captcha()  # Regenerate CAPTCHA
            elif add_user(username, password):
                st.success("Signup successful! Please login.")
                st.session_state['page'] = 'login'
                st.session_state['captcha_text'] = generate_captcha()
                st.rerun()
            else:
                st.error("Username already exists. Please choose a different username.")
                st.session_state['captcha_text'] = generate_captcha()

    if st.button("Go to Login"):
        st.session_state['page'] = 'login'
        st.session_state['captcha_text'] = generate_captcha()
        st.rerun()

# App Navigation Logic
if not st.session_state['logged_in']:
    if st.session_state['page'] == 'login':
        login_page()
    elif st.session_state['page'] == 'signup':
        signup_page()
else:
    main_app()
