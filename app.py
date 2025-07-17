import streamlit as st
from supabase import create_client
from datetime import datetime

# === CONFIG ===
SUPABASE_URL = st.secrets["supabase_url"]
SUPABASE_KEY = st.secrets["supabase_key"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config("💧 ระบบค่าน้ำ", layout="centered")
st.title("💧คำนวณค่าน้ำ")

# === ฟังก์ชั่นคำนวณค่าน้ำ ===
def calculate_price(units):
    return units * 10

# === ดึงข้อมู่บ้าน ===
@st.cache_data(ttl=60)
def load_houses():
    res = supabase.table("houses").select("*").execute()
    return res.data

houses = load_houses()
if not houses:
    st.warning("⚠️ ยังไม่มีข้อมู่บ้าน")
    st.stop()

if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False

address_list = [h["address"] for h in houses if "address" in h]

st.markdown("### 🏠 เลือกบ้าน")
search_col1, search_col2, add_col = st.columns([3, 2, 1])

with search_col1:
    search_input = st.text_input("\ud83d\udd0d ค้นหาชื่อบ้าน", placeholder="พิมพ์บางส่วน")

matches = [addr for addr in address_list if search_input.lower() in addr.lower()] if search_input else address_list

with search_col2:
    if matches:
        selected_address = st.selectbox(" ", matches, label_visibility="collapsed")
    else:
        selected_address = None
        st.warning("⚠️ ไม่พบชื่อบ้าน")

with add_col:
    if st.button("เพิ่มบ้าน +"):
        st.session_state.show_add_form = not st.session_state.show_add_form

if st.session_state.show_add_form:
    with st.form("add_house_form", clear_on_submit=True):
        new_address = st.text_input("🏡 ชื่อบ้าน")
        new_previous_meter = st.number_input("📿 มิเตอร์ล่าสุด", min_value=0.0, step=0.1, format="%.2f")
        submitted = st.form_submit_button("✅ เพิ่ม")

        if submitted:
            clean_address = new_address.strip()
            existing_addresses = [addr.strip() for addr in address_list]

            if clean_address == "":
                st.warning("⚠️ กรุณากรอกชื่อบ้าน")
            elif clean_address in existing_addresses:
                st.warning("⚠️ บ้านนี้มีแล้ว")
            else:
                data_to_insert = {
                    "address": clean_address,
                    "previous_meter": float(new_previous_meter)
                }
                try:
                    result = supabase.table("houses").insert(data_to_insert).execute()
                    if result.data:
                        st.success("✅ เพิ่มเรียบ")
                        st.session_state.show_add_form = False
                        st.rerun()
                    else:
                        st.error(f"❌ เพิ่มไม่สำเร็จ: {result.error}")
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิด: {e}")

selected_house = next((h for h in houses if h.get("address", "").strip() == selected_address.strip()), None)
if selected_house:
    previous_meter = selected_house.get("previous_meter", 0)
else:
    st.error("ไม่พบบ้าน")
    st.stop()

current_meter = st.number_input(
    "📥 มิเตอร์ปัจจุบัน",
    min_value=float(previous_meter),
    step=0.1,
    format="%.2f"
)

st.markdown(
    f"""
    <div style='background-color:#e6f4ff; padding:10px 15px; border-radius:10px; border:1px solid #cce0ff; font-size:16px;'>
        🔁 มิเตอร์ล่าสุด: <b>{previous_meter}</b> &nbsp;&nbsp;|
        &nbsp;&nbsp; 📥 มิเตอร์ปัจจุบัน: <b>{current_meter}</b>
    </div>
    """,
    unsafe_allow_html=True
)

if current_meter > previous_meter:
    units_used = current_meter - previous_meter
    price = calculate_price(units_used)
    col1, col2 = st.columns(2)
    col1.metric("💧 หน่วยที่ใช้", f"{units_used:.2f} หน่วย")
    col2.metric("💸 ค่าน้ำ", f"{price:.2f} บาท")
elif current_meter == previous_meter:
    st.info("📌 ยังไม่มีการใช้น้ำ")
else:
    st.warning("❌ มิเตอร์ต้องไม่ต่ำกว่าเดิม")

col1, col2, col3 = st.columns([2, 3, 2])
with col2:
    if st.button("💾 บันทึก") and current_meter > previous_meter:
        supabase.table("water_usage").insert({
            "address": selected_address,
            "previous_meter": previous_meter,
            "current_meter": current_meter,
            "units_used": units_used,
            "price": price,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        supabase.table("houses").update({
            "previous_meter": current_meter
        }).eq("id", selected_house["id"]).execute()

        st.success(f"✅ บันทึกแล้ว: ใช้ไป {units_used:.2f} หน่วย = {price:.2f} บาท 💧")
