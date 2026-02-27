import streamlit as st
from app.core import ClaimEstimator
import pandas as pd
from PIL import Image
import io

def render_header():
    st.set_page_config(page_title="Instant Motor Claim Estimator", layout="wide")
    st.title("🚗 Instant Motor Claim Estimator")
    st.markdown("### AI-Powered Damage Assessment & Cost Estimation")

def render_sidebar():
    st.sidebar.header("Configuration")
    api_key = st.sidebar.text_input("OpenAI/Gemini API Key (Optional)", type="password")
    model_choice = st.sidebar.selectbox("Select Model", ["Mock (Demo)", "GPT-4o", "Gemini 1.5 Pro"])
    return api_key, model_choice

def process_image(uploaded_file, estimator):
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        
        if st.button("Analyze Damage & Estimate Cost"):
            with st.spinner("Analyzing image for damages..."):
                # Convert to bytes for backend processing
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format=image.format)
                img_bytes = img_byte_arr.getvalue()
                
                # Call backend logic
                result = estimator.analyze_claim(img_bytes)
                
                display_results(result)

def display_results(result):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Damage Assessment")
        damages = result['damage_assessment'].get('damages', [])
        if damages:
            for d in damages:
                st.error(f"**{d['part'].replace('_', ' ').title()}**: {d['severity'].title()} - {d['description']}")
        else:
            st.info("No significant damage detected.")

    with col2:
        st.subheader("💰 Cost Estimate")
        estimate = result['cost_estimate']
        summary = estimate['summary']
        
        # Line Items Table
        line_items = estimate.get('line_items', [])
        if line_items:
            df = pd.DataFrame(line_items)
            st.dataframe(df[['part', 'severity', 'part_cost', 'labor_hours', 'labor_cost', 'total']], hide_index=True)
        
        st.divider()
        st.metric("Total Estimate", f"${summary['total_cost']:.2f}")
        
        st.write(f"**Parts Total:** ${summary['total_parts_cost']:.2f}")
        st.write(f"**Labor Total:** ${summary['total_labor_cost']:.2f} ({summary['total_labor_hours']} hrs @ ${summary['labor_rate']}/hr)")
        st.write(f"**Tax:** ${summary['tax']:.2f}")
        
        if result['status'] == "Pre-Approved":
            st.success("✅ Pre-Approved for Immediate Repair")
        else:
            st.warning("⚠️ Requires Manual Review (Estimate > Threshold)")

def main():
    render_header()
    api_key, model_choice = render_sidebar()
    
    # Initialize Core Logic
    estimator = ClaimEstimator()
    
    # File Upload
    uploaded_file = st.file_uploader("Upload Car Damage Photo", type=['jpg', 'png', 'jpeg'])
    
    process_image(uploaded_file, estimator)

if __name__ == "__main__":
    main()
