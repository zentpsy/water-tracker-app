import streamlit as st
from supabase import create_client
from datetime import datetime

# === CONFIG ===
SUPABASE_URL = st.secrets["supabase_url"]
SUPABASE_KEY = st.secrets["supabase_key"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config("💧 ระบบค่าน้ำ", layout="centered")
st.title("💧คำนวณค่าน้ำ")

# === ฟังก์ชันคำนวณค่าน้ำ ===
def calculate_price(units):
    return units * 10  # ปรับราคาต่อหน่วยได้ที่นี่

# === ดึงข้อมูลบ้านจาก Supabase ===
@st.cache_data(ttl=60)
def load_houses():
    res = supabase.table("houses").select("*").execute()
    return res.data

houses = load_houses()
if not houses:
    st.warning("⚠️ ยังไม่มีข้อมูลบ้านใน Supabase")
    st.stop()

# === เตรียมตัวแปรควบคุมฟอร์มเพิ่มบ้าน ===
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False

# === รายชื่อบ้าน ===
address_list = [h.get("address", "").strip() for h in houses]
col1, col2 = st.columns([4, 1])

with col1:
    selected_address = st.selectbox("🏠 เลือกบ้าน", address_list)

with col2:
    st.markdown("""
        <style>
        div.stButton > button:first-child {
            margin-top: 11px;
            width: 120px;
            height: 38px;
            font-size: 18px;
            border-radius: 6px;
        }
        </style>
    """, unsafe_allow_html=True)
    if st.button("เพิ่มบ้าน +"):
        st.session_state.show_add_form = not st.session_state.show_add_form

# === ฟอร์มเพิ่มบ้านใหม่ ===
if st.session_state.show_add_form:
    with st.form("add_house_form", clear_on_submit=True):
        new_address = st.text_input("🏡 ชื่อบ้าน (เช่น บ้านเลขที่ 999)")
        new_previous_meter = st.number_input("📟 ค่ามิเตอร์ล่าสุด", min_value=0.0, step=0.1, format="%.2f")
        submitted = st.form_submit_button("✅ เพิ่มบ้านใหม่")
    
        if submitted:
            clean_address = new_address.strip()
            existing_addresses = [addr.strip() for addr in address_list]
    
            if clean_address == "":
                st.warning("⚠️ กรุณากรอกชื่อบ้านให้ถูกต้อง")
            elif clean_address in existing_addresses:
                st.warning("⚠️ บ้านนี้มีอยู่แล้วในระบบ")
            else:
                data_to_insert = {
                    "address": clean_address,
                    "previous_meter": float(new_previous_meter)
                }
                try:
                    result = supabase.table("houses").insert(data_to_insert).execute()
    
                    if result.data:
                        st.success("✅ เพิ่มบ้านใหม่เรียบร้อยแล้ว")
                        st.session_state.show_add_form = False
                        st.rerun()
                    else:
                        st.error(f"❌ เพิ่มบ้านไม่สำเร็จ: {result.error}")
                except Exception as e:
                    st.error(f"❌ เกิดข้อผิดพลาดขณะ insert: {e}")


# === ค้นหาบ้านที่เลือก ===
selected_house = next((h for h in houses if h.get("address", "").strip() == selected_address.strip()), None)
if selected_house:
    previous_meter = selected_house.get("previous_meter", 0)
else:
    st.error("ไม่พบข้อมูลบ้านที่เลือก")
    st.stop()

# === กรอกค่ามิเตอร์ปัจจุบัน ===
current_meter = st.number_input(
    "📥 ค่ามิเตอร์ปัจจุบัน",
    min_value=float(previous_meter),
    step=0.1,
    format="%.2f"
)

# === แสดงค่ามิเตอร์ล่าสุด + ปัจจุบัน (บรรทัดเดียว) ===
st.markdown(
    f"""
    <div style='background-color:#e6f4ff; padding:10px 15px; border-radius:10px; border:1px solid #cce0ff; font-size:16px;'>
        🔁 มิเตอร์ล่าสุด: <b>{previous_meter}</b> &nbsp;&nbsp;|&nbsp;&nbsp; 📥 ค่ามิเตอร์ปัจจุบัน: <b>{current_meter}</b>
    </div>
    """,
    unsafe_allow_html=True
)

# === แสดงผลแบบเรียลไทม์
if current_meter > previous_meter:
    units_used = current_meter - previous_meter
    price = calculate_price(units_used)
    col1, col2 = st.columns(2)
    col1.metric("💧 หน่วยที่ใช้", f"{units_used:.2f} หน่วย")
    col2.metric("💸 ค่าน้ำ", f"{price:.2f} บาท")
elif current_meter == previous_meter:
    st.info("📌 ยังไม่มีการใช้น้ำเพิ่มเติม")
else:
    st.warning("❌ ค่ามิเตอร์ต้องไม่ต่ำกว่าค่าก่อนหน้า")

# --- เพิ่ม CSS ปรับปุ่มบันทึกที่นี่ ---
st.markdown(
    """
    <style>
    div.stButton > button:first-child:hover {
        background-color: #2196F3;
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 12px 36px;
        border-radius: 8px;
        border: none;
        min-width: 250px;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #1976D2;
        cursor: pointer;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# === ปุ่มบันทึก
col1, col2, col3 = st.columns([2, 3, 2])  # ปรับความกว้างคอลัมน์ตามต้องการ
with col2:
    if st.button("💾 บันทึกการใช้น้ำ") and current_meter > previous_meter:
        insert_result = supabase.table("water_usage").insert({
            "address": selected_address,
            "previous_meter": previous_meter,
            "current_meter": current_meter,
            "units_used": units_used,
            "price": price,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        update_result = supabase.table("houses").update({
            "previous_meter": current_meter
        }).eq("id", selected_house["id"]).execute()

        st.success(f"✅ บันทึกสำเร็จ: ใช้ไป {units_used:.2f} หน่วย = {price:.2f} บาท 💧")
