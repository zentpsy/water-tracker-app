import streamlit as st
from supabase import create_client
from datetime import datetime

st.title("💧 ระบบค่าน้ำ - DEBUG MODE")

try:
    # เชื่อมต่อ Supabase
    st.write("📌 Connecting to Supabase...")
    SUPABASE_URL = st.secrets["supabase_url"]
    SUPABASE_KEY = st.secrets["supabase_key"]
    st.write("✅ Found secrets")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    st.write("✅ Supabase client created")

    # ดึงข้อมูลบ้าน
    response = supabase.table("houses").select("*").execute()
    houses = response.data
    st.write("📦 houses:", houses)

    if houses is None or len(houses) == 0:
        st.warning("⚠️ ไม่พบข้อมูลบ้านใน Supabase")
        st.stop()

    # รายชื่อบ้าน
    address_list = [h.get("address", "").strip() for h in houses]
    st.write("📋 รายชื่อบ้าน:", address_list)

    # เลือกบ้าน
    selected_address = st.selectbox("🏠 เลือกบ้าน", address_list)

    # หาบ้านที่เลือก
    selected_house = next((h for h in houses if h.get("address", "").strip() == selected_address), None)
    st.write("✅ บ้านที่เลือก:", selected_house)

    if selected_house:
        previous_meter = selected_house.get("previous_meter", 0)
        st.info(f"🔁 มิเตอร์ล่าสุด: {previous_meter}")
    else:
        st.warning("⚠️ ไม่พบข้อมูลบ้านที่เลือก")

except Exception as e:
    st.error(f"❌ ERROR: {e}")
