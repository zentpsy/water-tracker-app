import streamlit as st
from supabase import create_client
from datetime import datetime

st.title("🔧 DEBUG MODE")

try:
    st.write("📌 Connecting to Supabase...")
    SUPABASE_URL = st.secrets["supabase_url"]
    SUPABASE_KEY = st.secrets["supabase_key"]
    st.write("✅ Found secrets")

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    st.write("✅ Supabase client created")

    res = supabase.table("houses").select("*").execute()
    st.write("📦 houses:", res.data)

except Exception as e:
    st.error(f"❌ ERROR: {e}")

if not houses:
    st.error("ไม่พบข้อมูลบ้านใน Supabase!")
    st.stop()

address_list = [h.get("address") for h in houses]
st.write("📋 รายชื่อบ้าน:", address_list)

selected_address = st.selectbox("🏠 เลือกบ้าน", address_list)
selected_house = next((h for h in houses if h.get("address") == selected_address), None)
st.write("✅ บ้านที่เลือก:", selected_house)

if selected_house:
    previous_meter = selected_house.get("previous_meter", 0)
    st.info(f"🔁 มิเตอร์ล่าสุด: {previous_meter}")
else:
    st.warning("ไม่สามารถดึงข้อมูลบ้านที่เลือกได้")
st.write()
