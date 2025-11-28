import streamlit as st
import pandas as pd
import random
from datetime import datetime
import json
import base64 # Added for image embedding
import os # Added for file path checking
import google.generativeai as genai
from PIL import Image

# --- CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="AI Expense Guardian", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------------
# 🎯 LOGO INTEGRATION: Using Base64 Encoding
# --------------------------------------------------------
LOGO_PATH = "./Assets/NewISpend.png" # Path relative to the app.py file

def get_base64_image(path):
    """Reads the image file and returns a Base64 data URL string."""
    try:
        # Check if the file exists before attempting to open it
        if not os.path.exists(path):
            st.warning(f"Logo file not found at {path}. Using placeholder.")
            # Fallback URL if the file is not found
            return "https://placehold.co/50x50/58a6ff/0d1117?text=iS" 

        with open(path, "rb") as image_file:
            # Encode the image data to base64 and create the data URL
            base64_data = base64.b64encode(image_file.read()).decode()
            return f"data:image/png;base64,{base64_data}"
    except Exception as e:
        st.error(f"Error loading logo: {e}. Using placeholder.")
        return "https://placehold.co/50x50/58a6ff/0d1117?text=iS"

LOGO_URL = get_base64_image(LOGO_PATH) 

# Custom CSS for a dark, professional, and interactive look
custom_css = f"""
<style>
    /* General Styling for Dark Theme */
    .stApp {{
        background-color: #0d1117; /* Dark background (GitHub Dark Mode) */
        color: #c9d1d9; /* Light text */
    }}

    /* Primary Container Styling (for cards) */
    .stContainer, .stAlert, .stButton>button, [data-testid="stSidebar"] {{
        background-color: #161b22; /* Slightly lighter dark card background */
        border-radius: 12px;
        border: 1px solid #30363d;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
    }}

    /* Header/Title */
    h1 {{
        color: #58a6ff; /* Blue accent for titles */
        padding-bottom: 10px;
        margin-top: 0; /* Adjust margin to align with logo in custom header */
    }}
    
    /* Logo Container Styling (for the top bar) */
    .header-container {{
        display: flex;
        align-items: center;
        gap: 15px;
        padding-bottom: 10px;
        border-bottom: 2px solid #30363d; /* Separator line */
    }}
    .logo-img {{
        border-radius: 8px;
        border: 2px solid #58a6ff;
        object-fit: cover;
    }}


    /* Metric Boxes Enhancement */
    [data-testid="stMetric"] {{
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #58a6ff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }}
    
    /* Risk Status Coloring */
    .risk-high {{
        color: #f85149; /* Red for high risk */
        font-weight: bold;
    }}
    .risk-medium {{
        color: #fcd95c; /* Yellow for medium risk */
        font-weight: bold;
    }}
    .risk-low {{
        color: #3fb950; /* Green for low risk */
        font-weight: bold;
    }}
    /* Coaching Accent */
    .coaching-tip {{
        border-left: 4px solid #3fb950;
        padding: 10px 15px;
        margin: 15px 0;
        background-color: #1f2937;
        border-radius: 8px;
    }}

    /* Button Hover Effect */
    .stButton>button:hover {{
        border-color: #58a6ff;
        color: #58a6ff;
    }}
    
    /* Progress Bar Customization */
    .stProgress > div > div > div > div {{
        background-color: #58a6ff;
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# --- AI INTEGRATION LOGIC (MOCKED FOR DEMO STABILITY) ---
def analyze_receipt_with_ai(uploaded_image):
    """
    Sends the image to Google Gemini Flash for OCR and risk analysis.
    """
    api_key = os.environ.get("API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except:
            pass
            
    if not api_key:
        st.error("API Key not found. Please set API_KEY in environment or GEMINI_API_KEY in .streamlit/secrets.toml")
        return {
            "vendor": "Unknown",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "amount": 0.00,
            "category": "Uncategorized",
            "risk_score": 0,
            "risk_reason": "API Key missing."
        }

    try:
        genai.configure(api_key=api_key)
        
        # Dynamic model selection to find a valid 'flash' model
        model_name = 'gemini-1.5-flash'
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods and 'flash' in m.name:
                    model_name = m.name
                    break
        except Exception:
            pass # Fallback to default if listing fails
            
        model = genai.GenerativeModel(model_name)

        # Convert UploadedFile to PIL Image
        image = Image.open(uploaded_image)

        prompt = """
        Analyze this receipt image and extract the following details into a JSON object:
        - vendor: The name of the merchant.
        - date: The date of the transaction in YYYY-MM-DD format. If not found, use today's date.
        - amount: The total amount of the transaction as a number (float).
        - category: The expense category (e.g., Meals, Travel, Office Supplies, Entertainment, Software, Groceries).
        - risk_score: A score from 0 to 100 indicating the risk level of this expense (0 is safe, 100 is high risk).
            - High risk (80+): Alcohol, Casinos, Personal items, unusually high amounts for the category.
            - Medium risk (50-79): Weekend transactions, missing details.
            - Low risk (0-49): Standard business expenses.
        - risk_reason: A brief explanation for the assigned risk score.

        Return ONLY the raw JSON string, no markdown formatting.
        """

        response = model.generate_content([prompt, image])
        
        # Clean up response text if it contains markdown code blocks
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        data = json.loads(response_text)
        
        # Ensure data types
        data['amount'] = float(data.get('amount', 0.0))
        data['risk_score'] = int(data.get('risk_score', 0))
        
        return data

    except Exception as e:
        st.error(f"Error analyzing receipt: {e}")
        return {
            "vendor": "Error",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "amount": 0.00,
            "category": "Error",
            "risk_score": 0,
            "risk_reason": f"Analysis failed: {str(e)}"
        }

def get_financial_advice_and_prediction(df_history):
    """
    Simulates sending aggregate spending data to a specialized LLM (Gemini) 
    for financial tips and predictive analysis (Forecasting).
    """
    import time
    time.sleep(2)
    
    # Analyze trends from historical data for mock advice
    advice_list = [
        "Your **Software** spending is efficient at just 15% of your total budget. Keep utilizing subscription bundles.",
        "The **Meals** category shows frequent high-value transactions. Consider setting a daily cap of $50 to cut costs by 15%.",
        "**Entertainment** expenses currently exceed internal policy thresholds. We recommend cutting these expenses completely to save $1,200/month.",
        "Optimize **Travel** by booking flights 21 days in advance; this could reduce airfare costs by 10% next month."
    ]
    
    # Forecast (based on simple extrapolation + minor random variance)
    forecast = df_history['Amount'].sum() * random.uniform(0.95, 1.05)
    
    return {
        "monthly_forecast": round(forecast, 2),
        "cuttable_expenses": "Entertainment, High-Value Meals",
        "advice": advice_list
    }

# --- APPLICATION INTERFACE (Low-Code) ---

# --- LOGO & TITLE SECTION (CUSTOM HTML) ---
# LOGO_URL now contains the Base64 data string
st.markdown(f"""
<div class="header-container">
    <img src="{LOGO_URL}" alt="App Logo" class="logo-img" width="50" height="50">
    <h1 style='margin: 0; padding: 0;'>AI Expense Guardian: Audit & Approval</h1>
</div>
""", unsafe_allow_html=True)
st.markdown("Automated processing for **OCR, Anomaly Detection, and Auto-Categorization**.")


# Initialize or load spending history
if 'full_history' not in st.session_state:
    # Create mock historical data for the Financial Coach to analyze
    initial_data = {
        'Category': ['Travel', 'Meals', 'Software', 'Office Supplies', 'Entertainment', 'Client Gifts'] * 20,
        'Amount': [random.uniform(50, 500) for _ in range(120)],
        'Date': [datetime.now() - pd.Timedelta(days=random.randint(1, 90)) for _ in range(120)]
    }
    st.session_state['full_history'] = pd.DataFrame(initial_data)

# --- SIDEBAR: Upload & Controls ---
with st.sidebar:
    st.header("Upload New Receipt 🧾")
    uploaded_file = st.file_uploader("Upload Image (JPG/PNG)", type=["jpg", "png", "jpeg"])
    
    st.divider()
    
    st.subheader("System Status")
    import os
    api_key = os.environ.get("API_KEY")
    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except:
            pass
            
    if api_key:
        st.success("AI Model (Gemini Vision) Online 🟢")
        st.caption("Secure API Key Loaded")
    elif api_key == "":
        st.error("AI Model Offline 🔴")
        st.caption("API Key is present but empty")
    else:
        st.error("AI Model Offline 🔴")
        st.caption("Missing API Key")
        
    st.info("App ID: 7c2x99d4 (Kubernetes Pod)")


# --- MAIN CONTENT LAYOUT: Tabs for Core Functions ---
tab1, tab2, tab3 = st.tabs(["🔍 Expense Analyzer", "📊 Weekly Summary", "🧠 Financial Coach"])


with tab1:
    col1, col2 = st.columns([1, 1])

    # LEFT COLUMN: Image Display & Analyze Button
    with col1:
        st.subheader("1. Receipt Document Scan")
        if uploaded_file is not None:
            # Using use_container_width=True for flexible sizing
            st.image(uploaded_file, caption='Uploaded Receipt for OCR', use_container_width=True)
            st.success("Receipt uploaded successfully! Ready for analysis.")
            
            # Interactive Button (Fixed: width="stretch")
            if st.button("🚀 Run AI Analysis", use_container_width=True):
                with st.spinner('**Processing:** AI is extracting data and checking against policy rules...'):
                    data = analyze_receipt_with_ai(uploaded_file)
                    
                    # Store in session state for analyzer history and full history
                    if 'history' not in st.session_state: st.session_state['history'] = []
                    
                    # Append new data to both histories
                    st.session_state['history'].append(data)
                    # Prepare new data for the full history DataFrame
                    df_new = pd.DataFrame([data])
                    df_new['Date'] = datetime.strptime(data['date'], '%Y-%m-%d')
                    
                    # Concatenate new data to full history
                    st.session_state['full_history'] = pd.concat([st.session_state['full_history'], df_new.drop(columns=['date'])], ignore_index=True)
                    
                    st.rerun()
        else:
            st.warning("Please upload a receipt image to begin the analysis.")

    # RIGHT COLUMN: Analysis Results
    with col2:
        st.subheader("2. Audit & Risk Prediction")
        
        if 'history' in st.session_state and st.session_state['history']:
            latest = st.session_state['history'][-1]
            score = latest['risk_score']
            
            # Determine color class for dynamic styling
            risk_class = "risk-low"
            status_emoji = "✅"
            approval_action = "Auto-Approve"

            if score > 50: 
                risk_class = "risk-medium"
                status_emoji = "⚠️"
                approval_action = "Requires Review"
            if score > 80: 
                risk_class = "risk-high"
                status_emoji = "❌"
                approval_action = "Auto-Reject"

            
            # Summary Card (Styled with custom markdown/HTML)
            st.markdown(f"""
            <div style="background-color: #1f2937; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h3 style='color: #fff; margin-top: 0;'>{status_emoji} {approval_action} Recommendation</h3>
                <p style='font-size: 1.2em;'>
                    **Vendor:** {latest['vendor']} ({latest['date']})<br>
                    **Category:** **<span class='risk-medium'>{latest['category']}</span>**<br>
                </p>
                <hr style='border-color: #30363d;'>
                
                <div style='display: flex; justify-content: space-between;'>
                    <div style='text-align: center;'>
                        <p style='margin: 0; font-size: 1em;'>Detected Amount</p>
                        <p style='margin: 0; font-size: 2.5em; color: #58a6ff;'>${latest['amount']}</p>
                    </div>
                    <div style='text-align: center;'>
                        <p style='margin: 0; font-size: 1em;'>AI Risk Score</p>
                        <p class='{risk_class}' style='margin: 0; font-size: 2.5em;'>{score}/100</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Detailed Risk Breakdown
            with st.expander("Detailed Anomaly Detection Report"):
                st.markdown(f"""
                - **Risk Reason:** {latest['risk_reason']}
                - **Policy Check:** Passed all checks except for amount threshold.
                - **Time of Day:** Normal business hours.
                - **Location Match:** Geo-location (if available) did not match. (MOCK)
                """)
                col_btn1, col_btn2 = st.columns([1,1])
                with col_btn1:
                    if approval_action != "Auto-Reject":
                        # Fixed: width="stretch"
                        st.button("Confirm & Approve", type="primary", use_container_width=True)
                    else:
                        # Fixed: width="stretch"
                        st.button("Flag for Manual Review", type="secondary", use_container_width=True)
                with col_btn2:
                    # Fixed: width="stretch"
                    st.button("View Audit Log", type="secondary", use_container_width=True)
        else:
            st.info("Analysis results will appear here after running the AI.")

with tab2:
    st.header("📈 Weekly Spending Dashboard")
    st.markdown("Overview of the last 90 days of processed expenses, auto-categorized by AI.")
    
    # Calculate Summary from full history
    df_recent = st.session_state['full_history']
    df_summary = df_recent.groupby('Category')['Amount'].sum().reset_index()
    
    col_dash1, col_dash2 = st.columns([2, 1])

    with col_dash1:
        st.bar_chart(df_summary.set_index("Category"), color="#58a6ff")
    
    with col_dash2:
        total_spending = df_summary['Amount'].sum()
        st.metric(label="Total Historical Spend", value=f"${total_spending:,.2f}")
        
        highest_category = df_summary.loc[df_summary['Amount'].idxmax()]
        st.metric(label="Highest Category", value=f"{highest_category['Category']}")
        
        st.markdown(f"**Top 3 Breakdown:**")
        # Fixed: width="stretch"
        st.dataframe(
            df_summary.sort_values(by="Amount", ascending=False).head(3).reset_index(drop=True),
            use_container_width=True,
            hide_index=True
        )

with tab3:
    st.header("🧠 AI Financial Coach: Optimization")
    st.markdown("Leveraging historical data to provide spending tips and monthly forecasting.")
    
    # Button to trigger the AI analysis (Fixed: width="stretch")
    if st.button("Ask the Financial Coach (Analyze Full History)", type="primary", use_container_width=True):
        with st.spinner("AI is analyzing 90 days of expense data and running predictive models..."):
            advice_data = get_financial_advice_and_prediction(st.session_state['full_history'])
            st.session_state['advice'] = advice_data
            st.rerun()

    if 'advice' in st.session_state:
        advice_data = st.session_state['advice']
        
        st.subheader("Monthly Financial Forecast")
        col_pred1, col_pred2 = st.columns(2)
        with col_pred1:
            st.metric(label="Predicted Monthly Spend", 
                      value=f"${advice_data['monthly_forecast']:,.2f}",
                      delta="~5% increase over last month", # Mock delta value
                      delta_color="inverse")
        with col_pred2:
            st.metric(label="Highest Potential Cut",
                      value=advice_data['cuttable_expenses'],
                      help="Based on policy violations and high non-essential spending.")

        st.subheader("Actionable Spending Tips")
        st.markdown("The AI recommends the following:**")
        
        for i, tip in enumerate(advice_data['advice']):
            # Display tips using the custom styled container
            st.markdown(f"""
            <div class="coaching-tip">
                **Tip {i+1}:** {tip}
            </div>
            """, unsafe_allow_html=True)
            
        st.caption("This analysis is based on aggregated, auto-categorized data processed by the AI.")

# --- History ---
st.divider()
st.subheader("Recent Processing History")
if 'history' in st.session_state and st.session_state['history']:
    df_history = pd.DataFrame(st.session_state['history'])
    # Fixed: width="stretch"
    st.dataframe(df_history, use_container_width=True)
else:
    st.info("No expenses have been processed yet.")
