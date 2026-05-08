import streamlit as st
from fpdf import FPDF
from PIL import Image
import tempfile
import os
import json
import extra_streamlit_components as stx
from streamlit_drawable_canvas import st_canvas
import numpy as np

# --- FUNGSI GENERATE PDF ---
def generate_pdf(data, sig_pelanggan=None, sig_sales=None):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    
    # --- KOP SURAT ---
    if os.path.exists('logo.png'):
        pdf.image('logo.png', x=10, y=10, w=40) 
        text_x = 55 
    else:
        text_x = 10
    pdf.set_xy(text_x, 12)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 8, txt="CV. PUMA UTAMA MAKMUR ARTARIA", ln=True)
    pdf.set_xy(text_x, 20)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 5, txt="Jalan Babatan Pantai XII No.31, Dukuh Sutorejo, Mulyorejo, Surabaya, 60113, Telp:031 3891571, HP: 0881-9776-552")
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # Helper: Checkbox, Radio, Row (Sama seperti versi sebelumnya)
    def draw_checkbox(x, y, label, is_checked):
        pdf.rect(x, y + 1.5, 3, 3) 
        if is_checked:
            pdf.set_xy(x - 0.5, y + 1)
            pdf.set_font("Arial", 'B', 8)
            pdf.cell(4, 4, txt="X", align='C')
        pdf.set_xy(x + 5, y)
        pdf.set_font("Arial", '', 9)
        pdf.cell(pdf.get_string_width(label) + 2, 6, txt=label)

    def draw_radio_row(label, options, selected, x_start=10, top_hari=""):
        pdf.set_x(x_start)
        pdf.set_font("Arial", '', 9)
        pdf.cell(40, 6, txt=label)
        for opt in options:
            curr_x = pdf.get_x()
            curr_y = pdf.get_y()
            draw_checkbox(curr_x, curr_y, f"TOP {top_hari} HARI" if (selected == "TOP" and top_hari and opt == "TOP") else "TOP ....... HARI" if opt == "TOP" else opt, opt == selected)
        pdf.ln(6)

    def add_row(label1, val1, label2="", val2=""):
        pdf.set_font("Arial", '', 9)
        start_y = pdf.get_y()
        pdf.set_xy(10, start_y)
        pdf.cell(35, 6, txt=label1, border=0); pdf.cell(5, 6, txt=":", border=0)
        pdf.multi_cell(55, 6, txt=str(val1), border='B')
        y_left = pdf.get_y()
        if label2:
            pdf.set_xy(110, start_y)
            pdf.cell(35, 6, txt=label2, border=0); pdf.cell(5, 6, txt=":", border=0)
            pdf.multi_cell(50, 6, txt=str(val2), border='B')
            pdf.set_y(max(y_left, pdf.get_y()))
        else: pdf.set_y(y_left)
        pdf.ln(1)

    # --- ISI DATA (Halaman 1) ---
    # Jenis Usaha Row
    y = pdf.get_y(); pdf.cell(35, 6, txt="JENIS USAHA", border=0); pdf.cell(5, 6, txt=":", border=0)
    draw_checkbox(50, y, "PERORANGAN", data['jenis_usaha'] == "PERORANGAN")
    pdf.set_xy(110, y); pdf.cell(35, 6, txt="KODE PELANGGAN", border=0); pdf.cell(5, 6, txt=":", border=0); pdf.cell(50, 6, txt=str(data['kode_pelanggan']), border='B'); pdf.ln(6)
    draw_checkbox(50, pdf.get_y(), "BADAN USAHA", data['jenis_usaha'] == "BADAN USAHA"); pdf.ln(8)

    add_row("NAMA OUTLET", data['nama_outlet'], "TGL PENGAJUAN", data['tgl_pengajuan'])
    add_row("ALAMAT KIRIM", data['alamat_kirim'], "NAMA PEMILIK", data['nama_pemilik'])
    add_row("ALAMAT TAGIH", data['alamat_tagih'], "TELEPON", data['telp_pemilik'])
    add_row("KELURAHAN", data['kelurahan'], "ALAMAT", data['alamat_pemilik'])
    add_row("KECAMATAN", data['kecamatan'], "NIK", data['nik'])
    add_row("KAB / KOTA", data['kota'], "NAMA PIC", data['nama_pic'])
    add_row("KODE POS", data['kode_pos'], "TELEPON", data['telp_pic'])
    add_row("TELEPON", data['telepon'], "JABATAN", data['jabatan'])
    add_row("EMAIL", data['email'], "JUMLAH STORE", data['jumlah_store'])
    add_row("JADWAL KUNJUNGAN", data['jadwal_kunjungan'], "CHANNEL DIST", data['channel_dist'])
    add_row("JADWAL PENAGIHAN", data['jadwal_penagihan'])
    add_row("JADWAL PENGIRIMAN", data['jadwal_pengiriman'])
    
    pdf.ln(3); pdf.set_font("Arial", 'B', 9); pdf.cell(190, 6, txt="BANGUNAN OUTLET", ln=True)
    draw_radio_row("STATUS KEPEMILIKAN :", ["PRIBADI", "KELUARGA", "SEWA"], data['status_kepemilikan'])
    draw_radio_row("JENIS BANGUNAN :", ["MODERN STORE", "RUKO", "RUMAH TINGGAL", "STAND PASAR"], data['jenis_bangunan'])
    pdf.set_x(10); pdf.cell(40, 6, txt="LINK LOKASI G-MAP :"); pdf.multi_cell(150, 6, txt=data['link_gmap'], border='B'); pdf.ln(2)
    draw_radio_row("TIPE PENJUALAN :", ["CBD", "COD", "TOP"], data['tipe_penjualan'], top_hari=data['top_hari'])
    draw_radio_row("JENIS PEMBAYARAN :", ["TRANSFER", "BG", "TUNAI"], data['jenis_pembayaran'])
    pdf.set_x(10); pdf.cell(40, 6, txt="NAMA REKENING BANK :"); pdf.multi_cell(150, 6, txt=data['nama_rekening'], border='B')
    pdf.set_x(10); pdf.cell(35, 6, txt="LIMIT PIUTANG"); pdf.cell(5, 6, txt=": Rp"); pdf.cell(50, 6, txt=data['limit_piutang'], border='B')
    pdf.cell(40, 6, txt="LIMIT LEMBAR NOTA :", align='R'); pdf.cell(60, 6, txt=str(data['limit_nota']), border='B', ln=True)

    pdf.ln(3); y = pdf.get_y(); pdf.cell(40, 6, txt="STATUS PERPAJAKAN :"); draw_checkbox(50, y, "NONPKP", data['status_pajak'] == "NONPKP"); draw_checkbox(75, y, "PKP", data['status_pajak'] == "PKP"); pdf.ln(8)
    pdf.cell(40, 6, txt="NOMOR NPWP :"); pdf.multi_cell(150, 6, txt=data['npwp'], border='B')
    pdf.cell(40, 6, txt="ALAMAT NPWP :"); pdf.multi_cell(150, 6, txt=data['alamat_npwp'], border='B')

    # --- HALAMAN 2: LAMPIRAN & TTD ---
    pdf.add_page()
    def draw_img(label, img_file, x, y, w, h=45):
        pdf.set_fill_color(210, 210, 210); pdf.rect(x, y, w, 5, 'DF')
        pdf.set_xy(x, y); pdf.set_font("Arial", '', 8); pdf.cell(w, 5, txt=label, align='C')
        pdf.rect(x, y+5, w, h)
        if img_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                img = Image.open(img_file)
                if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                img.save(tmp.name, format="JPEG")
                pdf.image(tmp.name, x=x, y=y+5, w=w, h=h)
            os.remove(tmp.name)

    draw_img("KTP", data['ktp_img'], 10, 10, 92)
    draw_img("NPWP", data['npwp_img'], 105, 10, 95)
    pdf.set_fill_color(170, 170, 170); pdf.rect(10, 65, 190, 6, 'DF'); pdf.set_xy(10, 65); pdf.set_text_color(255, 255, 255); pdf.set_font("Arial", 'B', 10); pdf.cell(190, 6, txt="FOTO LOKASI", align='C'); pdf.set_text_color(0, 0, 0)
    draw_img("TAMPAK DEPAN", data['depan_img'], 10, 71, 92)
    draw_img("TAMPAK DALAM", data['dalam_img'], 105, 71, 95)
    draw_img("TAMPAK KIRI", data['kiri_img'], 10, 125, 92)
    draw_img("TAMPAK KANAN", data['kanan_img'], 105, 125, 95)

    # --- BAGIAN TANDA TANGAN DIGITAL ---
    y_sig = 190
    pdf.set_xy(10, y_sig); pdf.set_font("Arial", 'B', 9)
    pdf.cell(45, 5, txt="PELANGGAN"); pdf.cell(45, 5, txt="SALES"); pdf.cell(50, 5, txt="SUPERVISOR")
    pdf.set_fill_color(150, 150, 150); pdf.set_text_color(255, 255, 255); pdf.cell(50, 6, txt="VALIDATOR", align='C', fill=True, ln=True)
    
    # Render Tanda Tangan Pelanggan
    if sig_pelanggan is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            sig_pelanggan.save(tmp.name)
            pdf.image(tmp.name, x=10, y=y_sig+5, h=20)
        os.remove(tmp.name)
    
    # Render Tanda Tangan Sales
    if sig_sales is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            sig_sales.save(tmp.name)
            pdf.image(tmp.name, x=55, y=y_sig+5, h=20)
        os.remove(tmp.name)

    pdf.set_text_color(0, 0, 0); pdf.set_font("Arial", '', 9)
    y_line = y_sig + 25
    pdf.line(10, y_line, 45, y_line); pdf.line(55, y_line, 90, y_line); pdf.line(100, y_line, 140, y_line)
    pdf.set_xy(10, y_line + 1); pdf.cell(45, 5, txt=f"Nama : {data['nama_pemilik']}") # Nama Terang Pelanggan
    pdf.set_xy(55, y_line + 1); pdf.cell(45, 5, txt=f"Nama : {data['nama_sales']}")   # Nama Terang Sales
    pdf.set_xy(100, y_line + 1); pdf.cell(40, 5, txt="Nama :")
    
    pdf.set_fill_color(230, 230, 230); pdf.rect(150, y_sig + 6, 50, 20, 'DF'); pdf.set_xy(155, y_sig + 8)
    pdf.cell(40, 5, txt="FALSE ADMIN", ln=True); pdf.set_x(155); pdf.cell(40, 5, txt="FALSE MANAGER")
    
    return pdf.output(dest='S').encode('latin1')

# --- TAMPILAN WEB (STREAMLIT) ---
st.set_page_config(page_title="Aplikasi Form NOO", layout="wide")
cookie_manager = stx.CookieManager()
draft_str = cookie_manager.get(cookie="noo_draft")
draft_data = json.loads(draft_str) if draft_str and isinstance(draft_str, str) else draft_str if isinstance(draft_str, dict) else {}

def get_val(key): return draft_data.get(key, "")
def get_idx(opts, key): val = draft_data.get(key, ""); return opts.index(val) if val in opts else 0

st.title("Aplikasi Input Form Pengajuan NOO")

# ... (Bagian Form 1, 2, 3, 4 Tetap Sama dengan sebelumnya) ...
# [Persingkat agar fokus ke TTD]

# --- UI BAGIAN 5: DIGITAL SIGNATURE (BARU) ---
st.markdown("---")
st.subheader("5. Tanda Tangan Digital")
st.info("Silakan coretkan tanda tangan langsung di bawah ini.")

col_sig1, col_sig2 = st.columns(2)

with col_sig1:
    st.write(f"**Tanda Tangan Pelanggan ({nama_pemilik if 'nama_pemilik' in locals() else '...'})**")
    canvas_pelanggan = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=3,
        stroke_color="#000000",
        background_color="#eeeeee",
        height=150,
        key="canvas_pelanggan",
    )

with col_sig2:
    st.write(f"**Tanda Tangan Sales ({nama_sales if 'nama_sales' in locals() else '...'})**")
    canvas_sales = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=3,
        stroke_color="#000000",
        background_color="#eeeeee",
        height=150,
        key="canvas_sales",
    )

# --- SUBMIT & RESET ---
st.markdown("---")
col_btn1, col_btn2 = st.columns([1, 4])

with col_btn1:
    if st.button("🗑️ Hapus Draft & Reset"):
        cookie_manager.delete("noo_draft"); st.rerun()

with col_btn2:
    if st.button("✅ Submit & Buat PDF", type="primary"):
        # Konversi Kanvas ke Image PIL
        img_sig_p = Image.fromarray(canvas_pelanggan.image_data.astype(np.uint8)) if canvas_pelanggan.image_data is not None else None
        img_sig_s = Image.fromarray(canvas_sales.image_data.astype(np.uint8)) if canvas_sales.image_data is not None else None
        
        data_input = {
            'jenis_usaha': jenis_usaha, 'nama_outlet': nama_outlet, 'alamat_kirim': alamat_kirim,
            'alamat_tagih': alamat_tagih, 'kelurahan': kelurahan, 'kecamatan': kecamatan,
            'kota': kota, 'kode_pos': kode_pos, 'telepon': telepon, 'email': email,
            'jadwal_kunjungan': jadwal_kunjungan, 'jadwal_penagihan': jadwal_penagihan,
            'jadwal_pengiriman': jadwal_pengiriman, 'kode_pelanggan': kode_pelanggan,
            'tgl_pengajuan': tgl_pengajuan.strftime("%d %B %Y"), 'nama_pemilik': nama_pemilik,
            'telp_pemilik': telp_pemilik, 'alamat_pemilik': alamat_pemilik, 'nik': nik,
            'nama_pic': nama_pic, 'telp_pic': telp_pic, 'jabatan': jabatan,
            'jumlah_store': jumlah_store, 'channel_dist': channel_dist,
            'status_pajak': status_pajak, 'npwp': npwp, 'alamat_npwp': alamat_npwp, 
            'tipe_faktur': tipe_faktur, 'metode_faktur': metode_faktur, 'ket_po': ket_po, 
            'diskon': diskon, 'nama_sales': nama_sales, 'status_kepemilikan': status_kepemilikan, 
            'jenis_bangunan': jenis_bangunan, 'link_gmap': link_gmap, 'tipe_penjualan': tipe_penjualan, 
            'top_hari': top_hari, 'jenis_pembayaran': jenis_pembayaran, 'nama_rekening': nama_rekening,
            'limit_piutang': limit_piutang, 'limit_nota': limit_nota,
            'ktp_img': ktp_img, 'npwp_img': npwp_img, 'depan_img': depan_img, 'dalam_img': dalam_img,
            'kiri_img': kiri_img, 'kanan_img': kanan_img
        }
        
        pdf_bytes = generate_pdf(data_input, img_sig_p, img_sig_s)
        st.success("PDF berhasil dibuat!")
        st.download_button(label="📄 Download PDF", data=pdf_bytes, file_name=f"Form_NOO_{nama_outlet}.pdf", mime="application/pdf")

# Auto-Save Logic (Sama seperti sebelumnya)
current_data = {
    'jenis_usaha': jenis_usaha, 'nama_outlet': nama_outlet, 'alamat_kirim': alamat_kirim,
    'alamat_tagih': alamat_tagih, 'kelurahan': kelurahan, 'kecamatan': kecamatan,
    'kota': kota, 'kode_pos': kode_pos, 'telepon': telepon, 'email': email,
    'jadwal_kunjungan': jadwal_kunjungan, 'jadwal_penagihan': jadwal_penagihan,
    'jadwal_pengiriman': jadwal_pengiriman, 'kode_pelanggan': kode_pelanggan,
    'nama_pemilik': nama_pemilik, 'telp_pemilik': telp_pemilik, 'alamat_pemilik': alamat_pemilik, 
    'nik': nik, 'nama_pic': nama_pic, 'telp_pic': telp_pic, 'jabatan': jabatan,
    'jumlah_store': jumlah_store, 'channel_dist': channel_dist,
    'status_kepemilikan': status_kepemilikan, 'jenis_bangunan': jenis_bangunan,
    'link_gmap': link_gmap, 'tipe_penjualan': tipe_penjualan, 'top_hari': top_hari,
    'jenis_pembayaran': jenis_pembayaran, 'nama_rekening': nama_rekening,
    'limit_piutang': limit_piutang, 'limit_nota': limit_nota, 'status_pajak': status_pajak, 
    'npwp': npwp, 'alamat_npwp': alamat_npwp, 'tipe_faktur': tipe_faktur, 
    'metode_faktur': metode_faktur, 'ket_po': ket_po, 'diskon': diskon, 'nama_sales': nama_sales
}

current_json = json.dumps(current_data)
if current_json != draft_str:
    cookie_manager.set("noo_draft", current_json)