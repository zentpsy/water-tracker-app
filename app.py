import streamlit as st
from datetime import datetime

# ตัวอย่าง: สมมติว่าคุณมี address_list กับ selected_house
address_list = ["บ้านเลขที่ 123", "บ้านแม่", "บ้านลุง", "บ้านเลขที่ 789"]
if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False

st.title("💧 ระบบติดตามการใช้น้ำ")

# ==== SECTION: เลือกบ้านและเพิ่มบ้าน ====
st.markdown("### 🏠 เลือกบ้าน")

search_input = st.text_input("🔍 ค้นหาชื่อบ้าน", placeholder="พิมพ์บางส่วนของชื่อบ้าน")
matches = [addr for addr in address_list if search_input.lower() in addr.lower()] if search_input else address_list

if matches:
    selected_address = st.selectbox("🏠 บ้านที่พบ", matches)
else:
    selected_address = None
    st.warning("⚠️ ไม่พบชื่อบ้านที่ตรงกับคำค้นหา")

# ==== ปุ่มเพิ่มบ้านแบบสวย + Responsive ====
st.markdown("""
    <style>
    .blue-btn button {
        background-color: #1f77b4 !important;
        color: white !important;
        width: 100% !important;
        height: 48px;
        font-size: 16px;
        border-radius: 10px;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="blue-btn">', unsafe_allow_html=True)
    if st.button("➕ เพิ่มบ้านใหม่"):
        st.session_state.show_add_form = not st.session_state.show_add_form
    st.markdown('</div>', unsafe_allow_html=True)

# ==== SECTION: ฟอร์มเพิ่มบ้านใหม่ ====
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
                # --- เชื่อมกับ Supabase ที่นี่ ---
                st.success(f"✅ เพิ่มบ้านใหม่เรียบร้อยแล้ว: {clean_address}")
                # จำลองอัปเดต:
                address_list.append(clean_address)
                st.session_state.show_add_form = False
                st.rerun()

# ==== SECTION: บันทึกการใช้น้ำ ====
# จำลองค่า
previous_meter = 100.0
current_meter = st.number_input("📈 มิเตอร์ปัจจุบัน", min_value=previous_meter, step=0.1, format="%.2f")

units_used = current_meter - previous_meter
price_per_unit = 10
price = units_used * price_per_unit

# ปุ่มบันทึกการใช้น้ำแบบกลาง
st.markdown("---")
st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)

if st.button("💾 บันทึกการใช้น้ำ", use_container_width=True) and current_meter > previous_meter:
    # สมมุติการบันทึกลง Supabase
    st.success(f"✅ บันทึกสำเร็จ: ใช้ไป {units_used:.2f} หน่วย = {price:.2f} บาท 💧")

st.markdown("</div>", unsafe_allow_html=True)

