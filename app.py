import streamlit as st
import requests

# Set the configuration for the web page
st.set_page_config(page_title="AI Expense Tracker", page_icon="💸", layout="centered")

BASE_URL = "https://expensetracker-production-c898.up.railway.app"

# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.income = 0.0
    st.session_state.budget_data = None

# ==========================================
# VIEW 1: LOGIN / SIGNUP SCREEN
# ==========================================
if not st.session_state.logged_in:
    st.title("Welcome to AI Expense Tracker")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login to your account")
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login"):
            res = requests.post(f"{BASE_URL}/login/", json={"username": login_user, "password": login_pass})
            if res.status_code == 200:
                data = res.json()
                st.session_state.logged_in = True
                st.session_state.user_id = data["user_id"]
                st.session_state.username = login_user
                st.session_state.income = data.get("income", 0.0)
                st.rerun()
            else:
                st.error("Invalid credentials.")

    with tab2:
        st.subheader("Create a new account")
        reg_user = st.text_input("New Username", key="reg_user")
        reg_pass = st.text_input("New Password", type="password", key="reg_pass")
        
        if st.button("Sign Up"):
            res = requests.post(f"{BASE_URL}/signup/", json={"username": reg_user, "password": reg_pass})
            if res.status_code == 200:
                st.success("Account created! Please log in.")
            else:
                st.error("Username already exists.")

# ==========================================
# VIEW 2: THE USER DASHBOARD
# ==========================================
else:
    # Header with Logout Button
    col1, col2 = st.columns([0.8, 0.2])
    col1.title(f"Welcome, {st.session_state.username}!")
    if col2.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()

    # ==========================================
    # Section 1: Set Income
    # ==========================================
    st.subheader("1. Enter Your Monthly Income")
    new_income = st.number_input("Monthly Income (₹)", min_value=0.0, value=float(st.session_state.income), step=1000.0)
    
    if st.button("Save Income"):
        res = requests.put(f"{BASE_URL}/users/{st.session_state.user_id}/income", json={"monthly_income": new_income})
        if res.status_code == 200:
            st.session_state.income = new_income
            st.success("Income updated!")

    # ==========================================
    # Section 2: Strategy Planner
    # ==========================================
    st.subheader("2. Design Your Budget Strategy")
    st.markdown("Adjust the sliders below. The default is the **50/30/20 Rule**, but you have full control.")
    
    needs_pct = st.slider("Needs / Essentials (%)", 0, 100, 50)
    wants_pct = st.slider("Wants / Discretionary (%)", 0, 100, 30)
    savings_pct = st.slider("Savings & Investments (%)", 0, 100, 20)
    
    total_pct = needs_pct + wants_pct + savings_pct
    
    if total_pct != 100:
        st.warning(f"Your allocations currently equal {total_pct}%. Please adjust them to equal exactly 100%.")
    else:
        # Fetch the dynamic calculation from the backend
        if st.session_state.income > 0:
            params = {"needs_pct": needs_pct, "wants_pct": wants_pct, "savings_pct": savings_pct}
            res = requests.get(f"{BASE_URL}/users/{st.session_state.user_id}/budget-advice", params=params)
            
            if res.status_code == 200:
                budget_data = res.json()["breakdown"]
                st.session_state.budget_data = budget_data
                
                st.success("Budget Calculated!")
                c1, c2, c3 = st.columns(3)
                c1.metric(f"Needs ({needs_pct}%)", f"₹{budget_data['needs']:,.2f}")
                c2.metric(f"Wants ({wants_pct}%)", f"₹{budget_data['wants']:,.2f}")
                c3.metric(f"Savings ({savings_pct}%)", f"₹{budget_data['savings']:,.2f}")

    st.divider()

    # ==========================================
    # Section 3: Expense Tracker
    # ==========================================
    st.subheader("3. Log a Transaction")
    
    with st.form("transaction_form"):
        col_a, col_b = st.columns(2)
        
        with col_a:
            tx_amount = st.number_input("Amount (₹)", min_value=1.0, step=10.0)
            tx_category = st.selectbox("Budget Category", ["Needs", "Wants", "Savings"])
        
        with col_b:
            tx_type = st.selectbox("Expense Type", ["Fixed", "Variable"])
            st.write("") 
            st.write("")
            submitted = st.form_submit_button("Log Transaction")
            
        if submitted:
            tx_payload = {
                "user_id": st.session_state.user_id,
                "amount": tx_amount,
                "category": tx_category,
                "expense_type": tx_type
            }
            
            tx_res = requests.post(f"{BASE_URL}/transactions/", json=tx_payload)
            if tx_res.status_code == 200:
                st.success(f"Logged ₹{tx_amount} under {tx_category}!")
            else:
                st.error("Failed to log transaction.")

    # ==========================================
    # Section 4: Transaction History & Budget vs Actual
    # ==========================================
    st.subheader("4. Recent Transactions")
    
    history_res = requests.get(f"{BASE_URL}/users/{st.session_state.user_id}/transactions")
    
    if history_res.status_code == 200:
        transactions = history_res.json()
        
        if len(transactions) > 0:
            spent_needs = sum(t["amount"] for t in transactions if t["category"] == "Needs")
            spent_wants = sum(t["amount"] for t in transactions if t["category"] == "Wants")
            spent_savings = sum(t["amount"] for t in transactions if t["category"] == "Savings")
            
            if st.session_state.budget_data:
                st.markdown("### Remaining Budget")
                r1, r2, r3 = st.columns(3)
                r1.metric("Needs Left", f"₹{st.session_state.budget_data['needs'] - spent_needs:,.2f}")
                r2.metric("Wants Left", f"₹{st.session_state.budget_data['wants'] - spent_wants:,.2f}")
                r3.metric("Savings Left", f"₹{st.session_state.budget_data['savings'] - spent_savings:,.2f}")
            
            st.markdown("### History")
            st.dataframe(transactions, use_container_width=True)
        else:
            st.info("No transactions logged yet. Add one above!")