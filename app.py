import streamlit as st
from supabase import create_client, Client
from datetime import datetime

# --- Load secrets ---
SUPABASE_URL = st.secrets["supabase_url"]
SUPABASE_KEY = st.secrets["supabase_key"]

# --- Connect to Supabase ---
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Page config ---
st.set_page_config("💧 บันทึกค่าน้ำ", layout="centered")
st.title("💧 ระบบบันทึกค่าน้ำแต่ละบ้าน")

# --- Load house list ---
@st.cache_data
def load_houses():
    res = supabase.table("houses").select("*").execute()
    return res.data

houses = load_houses()
address_list = [h["address"] for h in houses]

# --- UI เลือกบ้าน ---
selected_address = st.selectbox("🏠 เลือกบ้าน", address_list)

# หา previous_meter ของบ้านนั้น
selected_house = next((h for h in houses if h["address"] == selected_address), None)
if selected_house is None:
    st.error("ไม่พบข้อมูลบ้าน")
    st.stop()

previous_meter = selected_house["previous_meter"]
st.info(f"🔁 มิเตอร์ล่าสุด: {previous_meter}")

# --- กรอกมิเตอร์ใหม่ ---
current_meter = st.number_input("📥 มิเตอร์ปัจจุบัน", min_value=previous_meter, step=1.0)

if st.button("💾 บันทึกข้อมูล"):
    # คำนวณหน่วยและราคาน้ำ
    units_used = current_meter - previous_meter
    price = calculate_price(units_used)

    # --- บันทึกลง water_usage ---
    supabase.table("water_usage").insert({
        "address": selected_address,
        "previous_meter": previous_meter,
        "current_meter": current_meter,
        "units_used": units_used,
        "price": price,
        "created_at": datetime.utcnow().isoformat()
    }).execute()

    # --- อัปเดต previous_meter ใน houses ---
    supabase.table("houses").update({
        "previous_meter": current_meter
    }).eq("id", selected_house["id"]).execute()

    st.success(f"✅ บันทึกสำเร็จ: ใช้ {units_used} หน่วย = {price:.2f} บาท")

# --- สูตรราคาน้ำ (แบบง่าย) ---
def calculate_price(units):
    return units * 10  # แก้เป็นขั้นบันไดได้ภายหลัง
