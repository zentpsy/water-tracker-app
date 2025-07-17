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
# -- ตัวอย่าง: ข้อมูลที่ดึงมาจาก Supabase
address_list = [h["address"] for h in houses if "address" in h]

# -- ค้นหา + เลือกบ้าน
st.markdown("### 🏠 เลือกบ้านที่ต้องการ")
search_col1, search_col2 ,col2 = st.columns([3, 1, 1])

with search_col1:
    search_input = st.text_input("🔍 ค้นหาชื่อบ้าน", placeholder="พิมพ์บางส่วนของชื่อบ้าน")

# -- กรองชื่อบ้านที่ตรงกับคำค้นหา
matches = [addr for addr in address_list if search_input.lower() in addr.lower()] if search_input else address_list

with search_col2:
    if matches:
        selected_address = st.selectbox(" ", matches, label_visibility="collapsed")
    else:
        selected_address = None
        st.warning("⚠️ ไม่พบชื่อบ้านที่ตรงกับคำค้นหา")

# -- ดึงข้อมูลบ้านที่เลือก
if selected_address:
    selected_house = next(
        (h for h in houses if h.get("address", "").strip() == selected_address.strip()),
        None
    )
else:
    selected_house = None  

with col2:
   
    if st.button("เพิ่มที่อยู่ +"):
        st.session_state.show_add_form = not st.session_state.show_add_form
        
    st.markdown('</div>', unsafe_allow_html=True)
        
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


# === ปุ่มบันทึก
col1, col2, col3 = st.columns([2, 3, 2])  # ปรับความกว้างคอลัมน์ตามต้องการ
with col1:
    
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
with col3:
