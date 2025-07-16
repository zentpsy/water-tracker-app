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
    return units * 10  # หน่วยละ 10 บาท (ปรับได้ภายหลัง)

# === ดึงข้อมูลบ้านจาก Supabase ===
def load_houses():
    res = supabase.table("houses").select("*").execute()
    return res.data

houses = load_houses()

if not houses:
    st.warning("⚠️ ยังไม่มีข้อมูลบ้านใน Supabase")
    st.stop()

# === รายชื่อบ้าน ===
address_list = [h.get("address", "").strip() for h in houses]
# แบ่งเป็น 2 คอลัมน์: dropdown + ปุ่มเพิ่มบ้าน
col1, col2 = st.columns([4, 1])

with col1:
    selected_address = st.selectbox("🏠 เลือกบ้าน", address_list)

with col2:
    if st.button("\u002B เพิ่มบ้าน"):
        st.write("กดปุ่ม + แล้ว")  # ทดสอบว่าแสดงหรือไม่


# === ค้นหาบ้านที่เลือก ===
selected_house = next(
    (h for h in houses if h.get("address", "").strip() == selected_address.strip()),
    None
)

if selected_house:
    previous_meter = selected_house.get("previous_meter", 0)
else:
    st.error("ไม่พบข้อมูลบ้านที่เลือก")
    st.stop()

# === กรอกค่ามิเตอร์ปัจจุบัน ===
current_meter = st.number_input("📥 ค่ามิเตอร์ปัจจุบัน", min_value=previous_meter, step=1)

# === แสดงค่ามิเตอร์ล่าสุด + ปัจจุบัน (บรรทัดเดียว)
st.markdown(
    f"""
    <div style='background-color:#e6f4ff; padding:10px 15px; border-radius:10px; border:1px solid #cce0ff; font-size:16px;'>
        🔁 มิเตอร์ล่าสุด: <b>{previous_meter}</b> &nbsp;&nbsp;|&nbsp;&nbsp; 📥 ค่ามิเตอร์ปัจจุบัน: <b>{int(current_meter)}</b>
    </div>
    """,
    unsafe_allow_html=True
)


# === แสดงผลแบบเรียลไทม์
if current_meter > previous_meter:
    units_used = current_meter - previous_meter
    price = calculate_price(units_used)
    col1, col2 = st.columns(2)
    col1.metric("💧 หน่วยที่ใช้", f"{units_used} หน่วย")
    col2.metric("💸 ค่าน้ำ", f"{price:.2f} บาท")
elif current_meter == previous_meter:
    st.info("📌 ยังไม่มีการใช้น้ำเพิ่มเติม")
else:
    st.warning("❌ ค่ามิเตอร์ต้องไม่ต่ำกว่าค่าก่อนหน้า")

# === ปุ่มบันทึก
if st.button("💾 บันทึกการใช้น้ำ") and current_meter > previous_meter:
    # บันทึกลง water_usage
    insert_result = supabase.table("water_usage").insert({
        "address": selected_address,
        "previous_meter": previous_meter,
        "current_meter": current_meter,
        "units_used": units_used,
        "price": price,
        "created_at": datetime.utcnow().isoformat()
    }).execute()
    st.write(insert_result)

    # อัปเดต previous_meter ใน houses
    update_result = supabase.table("houses").update({
        "previous_meter": current_meter
    }).eq("id", selected_house["id"]).execute()
    st.write(update_result)

    st.success(f"✅ บันทึกสำเร็จ: ใช้ไป {units_used} หน่วย = {price:.2f} บาท 💧")
