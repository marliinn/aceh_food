import streamlit as st
from fpdf import FPDF
from PIL import Image
import tempfile
import os
import json
import extra_streamlit_components as stx
from streamlit_drawable_canvas import st_canvas
import numpy as np

# --- INISIALISASI HALAMAN ---
if 'halaman' not in st.session_state:
    st.session_state.halaman = 1
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}

# --- FUNGSI GENERATE PDF ---
def generate_pdf(data, sig_pelanggan=None, sig_sales=None):
    pdf = FPDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    
    # --- KOP SURAT ---
    if os.path.exists('logo.jpeg'):
        pdf.image('logo.jpeg', x=10, y=10, w=20) 
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
        pdf.cell(35, 6, txt=label1, border=0)
        pdf.cell(5, 6, txt=":", border=0)
        pdf.multi_cell(55, 6, txt=str(val1), border='B')
        y_left = pdf.get_y()
        if label2:
            pdf.set_xy(110, start_y)
            pdf.cell(35, 6, txt=label2, border=0)
            pdf.cell(5, 6, txt=":", border=0)
            pdf.multi_cell(50, 6, txt=str(val2), border='B')
            y_right = pdf.get_y()
            pdf.set_y(max(y_left, y_right))
        else:
            pdf.set_y(y_left)
        pdf.ln(1)

    # --- ISI DATA (Halaman 1) ---
    y = pdf.get_y()
    pdf.cell(35, 6, txt="JENIS USAHA", border=0)
    pdf.cell(5, 6, txt=":", border=0)
    draw_checkbox(50, y, "PERORANGAN", data['jenis_usaha'] == "PERORANGAN")
    pdf.set_xy(110, y)
    pdf.cell(35, 6, txt="KODE PELANGGAN", border=0)
    pdf.cell(5, 6, txt=":", border=0)
    pdf.cell(50, 6, txt=str(data['kode_pelanggan']), border='B')
    pdf.ln(6)
    draw_checkbox(50, pdf.get_y(), "BADAN USAHA", data['jenis_usaha'] == "BADAN USAHA")
    pdf.ln(8)

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
    
    pdf.ln(3)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(190, 6, txt="BANGUNAN OUTLET", ln=True)
    draw_radio_row("STATUS KEPEMILIKAN :", ["PRIBADI", "KELUARGA", "SEWA"], data['status_kepemilikan'])
    draw_radio_row("JENIS BANGUNAN :", ["MODERN STORE", "RUKO", "RUMAH TINGGAL", "STAND PASAR"], data['jenis_bangunan'])
    
    pdf.set_x(10)
    pdf.cell(40, 6, txt="LINK LOKASI G-MAP :")
    pdf.multi_cell(150, 6, txt=data['link_gmap'], border='B')
    
    pdf.ln(2)
    draw_radio_row("TIPE PENJUALAN :", ["CBD", "COD", "TOP"], data['tipe_penjualan'], top_hari=data['top_hari'])
    draw_radio_row("JENIS PEMBAYARAN :", ["TRANSFER", "BG", "TUNAI"], data['jenis_pembayaran'])
    
    pdf.set_x(10)
    pdf.cell(40, 6, txt="NAMA REKENING BANK :")
    pdf.multi_cell(150, 6, txt=data['nama_rekening'], border='B')
    
    pdf.set_x(10)
    pdf.cell(35, 6, txt="LIMIT PIUTANG")
    pdf.cell(5, 6, txt=": Rp")
    pdf.cell(50, 6, txt=data['limit_piutang'], border='B')
    pdf.cell(40, 6, txt="LIMIT LEMBAR NOTA :", align='R')
    pdf.cell(60, 6, txt=str(data['limit_nota']), border='B', ln=True)

    pdf.ln(3)
    y = pdf.get_y()
    pdf.cell(40, 6, txt="STATUS PERPAJAKAN :")
    draw_checkbox(50, y, "NONPKP", data['status_pajak'] == "NONPKP")
    draw_checkbox(75, y, "PKP", data['status_pajak'] == "PKP")
    pdf.ln(8)
    
    pdf.cell(40, 6, txt="NOMOR NPWP :")
    pdf.multi_cell(150, 6, txt=data['npwp'], border='B')
    pdf.cell(40, 6, txt="ALAMAT NPWP :")
    pdf.multi_cell(150, 6, txt=data['alamat_npwp'], border='B')

    pdf.cell(50, 6, txt="TIPE PENERBITAN FAKTUR PAJAK :", ln=True)
    y = pdf.get_y()
    draw_checkbox(20, y, "Faktur Pajak Sesuai Surat Jalan/Nota Kiriman", data['tipe_faktur'] == "Faktur Pajak Sesuai Surat Jalan/Nota Kiriman")
    draw_checkbox(115, y, "Tidak Minta Faktur Pajak", data['tipe_faktur'] == "Tidak Minta Faktur Pajak")
    pdf.ln(6)
    y = pdf.get_y()
    draw_checkbox(20, y, "Faktur Pajak Sesuai Sale Out", data['tipe_faktur'] == "Faktur Pajak Sesuai Sale Out")
    draw_checkbox(115, y, "Yang lain...", data['tipe_faktur'] == "Yang lain...")
    pdf.ln(6)
    y = pdf.get_y()
    draw_checkbox(20, y, "Faktur Pajak Sesuai Totalan (Konsinyasi dikurangi retur)", data['tipe_faktur'] == "Faktur Pajak Sesuai Totalan (Konsinyasi dikurangi retur)")
    pdf.ln(8)

    pdf.cell(50, 6, txt="FAKTUR PAJAK :", ln=True)
    y = pdf.get_y()
    draw_checkbox(20, y, "Dikirim melalui email", data['metode_faktur'] == "Dikirim melalui email")
    draw_checkbox(115, y, "Tidak Minta Faktur Pajak", data['metode_faktur'] == "Tidak Minta Faktur Pajak")
    pdf.ln(6)
    y = pdf.get_y()
    draw_checkbox(20, y, "Diprint dan diikutkan dalam tagihan", data['metode_faktur'] == "Diprint dan diikutkan dalam tagihan")
    draw_checkbox(115, y, "Yang lain...", data['metode_faktur'] == "Yang lain...")
    pdf.ln(8)

    y = pdf.get_y()
    pdf.cell(40, 6, txt="KETERANGAN PO :")
    draw_checkbox(50, y, "MINTA PO", data['ket_po'] == "MINTA PO")
    draw_checkbox(80, y, "LANGSUNG ISI", data['ket_po'] == "LANGSUNG ISI")
    pdf.ln(8)

    pdf.cell(40, 6, txt="DISKON TOKO :")
    pdf.cell(100, 6, txt=str(data['diskon']), border='B', ln=True)
    pdf.cell(40, 6, txt="NAMA SALES :")
    pdf.cell(100, 6, txt=str(data['nama_sales']), border='B', ln=True)

    # --- HALAMAN 2: LAMPIRAN & TTD ---
    pdf.add_page()
    def draw_img(label, img_file, x, y, w, h=45):
        pdf.set_fill_color(210, 210, 210)
        pdf.rect(x, y, w, 5, 'DF')
        pdf.set_xy(x, y)
        pdf.set_font("Arial", '', 8)
        pdf.cell(w, 5, txt=label, align='C')
        pdf.rect(x, y+5, w, h)
        if img_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                img = Image.open(img_file)
                if img.mode in ("RGBA", "P"): 
                    img = img.convert("RGB")
                img.save(tmp.name, format="JPEG")
                pdf.image(tmp.name, x=x, y=y+5, w=w, h=h)
            os.remove(tmp.name)

    draw_img("KTP", data['ktp_img'], 10, 10, 92)
    draw_img("NPWP", data['npwp_img'], 105, 10, 95)
    
    pdf.set_fill_color(170, 170, 170)
    pdf.rect(10, 65, 190, 6, 'DF')
    pdf.set_xy(10, 65)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(190, 6, txt="FOTO LOKASI", align='C')
    pdf.set_text_color(0, 0, 0)
    
    draw_img("TAMPAK DEPAN", data['depan_img'], 10, 71, 92)
    draw_img("TAMPAK DALAM", data['dalam_img'], 105, 71, 95)
    draw_img("TAMPAK KIRI", data['kiri_img'], 10, 125, 92)
    draw_img("TAMPAK KANAN", data['kanan_img'], 105, 125, 95)

    # --- BAGIAN TANDA TANGAN DIGITAL ---
    y_sig = 190
    pdf.set_xy(10, y_sig)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(45, 5, txt="PELANGGAN")
    pdf.cell(45, 5, txt="SALES")
    pdf.cell(50, 5, txt="SUPERVISOR")
    
    pdf.set_fill_color(150, 150, 150)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(50, 6, txt="VALIDATOR", align='C', fill=True, ln=True)
    
    def render_signature(sig_img, x_pos):
        if sig_img is not None:
            try:
                bg = Image.new("RGB", sig_img.size, (255, 255, 255))
                bg.paste(sig_img, mask=sig_img.split()[3])
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                    bg.save(tmp.name, format="JPEG", quality=90)
                    pdf.image(tmp.name, x=x_pos, y=y_sig+5, h=20)
                os.remove(tmp.name)
            except Exception:
                pass

    render_signature(sig_pelanggan, 10)
    render_signature(sig_sales, 55)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 9)
    y_line = y_sig + 25
    pdf.line(10, y_line, 45, y_line)
    pdf.line(55, y_line, 90, y_line)
    pdf.line(100, y_line, 140, y_line)
    
    pdf.set_xy(10, y_line + 1)
    pdf.cell(45, 5, txt=f"Nama : {data['nama_pemilik']}") 
    pdf.set_xy(55, y_line + 1)
    pdf.cell(45, 5, txt=f"Nama : {data['nama_sales']}")   
    pdf.set_xy(100, y_line + 1)
    pdf.cell(40, 5, txt="Nama :")
    
    pdf.set_fill_color(230, 230, 230)
    pdf.rect(150, y_sig + 6, 50, 20, 'DF')
    pdf.set_xy(155, y_sig + 8)
    pdf.cell(40, 5, txt="FALSE ADMIN", ln=True)
    pdf.set_x(155)
    pdf.cell(40, 5, txt="FALSE MANAGER", ln=True)
    
    return pdf.output(dest='S').encode('latin1')


# --- TAMPILAN WEB (STREAMLIT) ---
st.set_page_config(page_title="Aplikasi Form NOO", layout="wide")
st.title("Aplikasi Input Form Pengajuan NOO")

cookie_manager = stx.CookieManager()

# =====================================================================
# HALAMAN 1: ISI DATA TEKS (DENGAN AUTO-SAVE)
# =====================================================================
if st.session_state.halaman == 1:
    
    # Ambil draft auto-save dari cookie
    draft_str = cookie_manager.get(cookie="noo_draft_auto")
    draft_data = {}
    if draft_str and isinstance(draft_str, str):
        try: draft_data = json.loads(draft_str)
        except: pass
    elif isinstance(draft_str, dict): draft_data = draft_str

    def get_val(key): return draft_data.get(key, "")
    def get_idx(opts, key): 
        val = draft_data.get(key, "")
        return opts.index(val) if val in opts else 0

    st.info("🟢 **Langkah 1:** Isi data outlet. Data Anda akan **Otomatis Tersimpan** saat mengetik.")

    # --- UI BAGIAN 1: DATA OUTLET & PIC ---
    st.subheader("1. Data Outlet, Pemilik, & PIC")
    col1, col2 = st.columns(2)
    with col1:
        jenis_usaha_opts = ["PERORANGAN", "BADAN USAHA"]
        jenis_usaha = st.radio("Jenis Usaha", jenis_usaha_opts, index=get_idx(jenis_usaha_opts, 'jenis_usaha'), horizontal=True)
        nama_outlet = st.text_input("Nama Outlet", value=get_val('nama_outlet'))
        alamat_kirim = st.text_input("Alamat Kirim", value=get_val('alamat_kirim'))
        alamat_tagih = st.text_input("Alamat Tagih", value=get_val('alamat_tagih'))
        kelurahan = st.text_input("Kelurahan", value=get_val('kelurahan'))
        kecamatan = st.text_input("Kecamatan", value=get_val('kecamatan'))
        kota = st.text_input("Kab / Kota", value=get_val('kota'))
        kode_pos = st.text_input("Kode Pos", value=get_val('kode_pos'))
        telepon = st.text_input("Telepon Outlet", value=get_val('telepon'))
        email = st.text_input("Email", value=get_val('email'))
        jadwal_kunjungan = st.text_input("Jadwal Kunjungan", value=get_val('jadwal_kunjungan'))
        jadwal_penagihan = st.text_input("Jadwal Penagihan", value=get_val('jadwal_penagihan'))
        jadwal_pengiriman = st.text_input("Jadwal Pengiriman", value=get_val('jadwal_pengiriman'))

    with col2:
        kode_pelanggan = st.text_input("Kode Pelanggan", value=get_val('kode_pelanggan'))
        tgl_pengajuan = st.date_input("Tanggal Pengajuan")
        nama_pemilik = st.text_input("Nama Pemilik", value=get_val('nama_pemilik'))
        telp_pemilik = st.text_input("Telepon Pemilik", value=get_val('telp_pemilik'))
        alamat_pemilik = st.text_area("Alamat Pemilik", value=get_val('alamat_pemilik'))
        nik = st.text_input("NIK Pemilik", value=get_val('nik'))
        nama_pic = st.text_input("Nama PIC", value=get_val('nama_pic'))
        telp_pic = st.text_input("Telepon PIC", value=get_val('telp_pic'))
        jabatan = st.text_input("Jabatan PIC", value=get_val('jabatan'))
        
        val_store = draft_data.get('jumlah_store')
        val_store = int(val_store) if val_store else 1
        jumlah_store = st.number_input("Jumlah Store", min_value=1, step=1, value=val_store if val_store >= 1 else 1)
        channel_dist = st.text_input("Channel Distribusi", value=get_val('channel_dist'))

    st.markdown("---")

    # --- UI BAGIAN 2 & 3: BANGUNAN & PAJAK ---
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("2. Bangunan Outlet & Pembayaran")
        kepemilikan_opts = ["PRIBADI", "KELUARGA", "SEWA"]
        status_kepemilikan = st.radio("Status Kepemilikan", kepemilikan_opts, index=get_idx(kepemilikan_opts, 'status_kepemilikan'), horizontal=True)
        
        bangunan_opts = ["MODERN STORE", "RUKO", "RUMAH TINGGAL", "STAND PASAR"]
        jenis_bangunan = st.radio("Jenis Bangunan", bangunan_opts, index=get_idx(bangunan_opts, 'jenis_bangunan'), horizontal=True)
        link_gmap = st.text_input("Link Lokasi G-MAP", value=get_val('link_gmap'))
        
        jual_opts = ["CBD", "COD", "TOP"]
        tipe_penjualan = st.radio("Tipe Penjualan", jual_opts, index=get_idx(jual_opts, 'tipe_penjualan'), horizontal=True)
        
        top_hari = ""
        if tipe_penjualan == "TOP":
            val_top = draft_data.get('top_hari')
            val_top = int(val_top) if val_top else 1
            top_hari = st.number_input("Jumlah Hari TOP", min_value=1, step=1, value=val_top if val_top >= 1 else 1)
            
        bayar_opts = ["TRANSFER", "BG", "TUNAI"]
        jenis_pembayaran = st.radio("Jenis Pembayaran", bayar_opts, index=get_idx(bayar_opts, 'jenis_pembayaran'), horizontal=True)
        nama_rekening = st.text_input("Nama Rekening Bank", value=get_val('nama_rekening'))
        
        col_limit1, col_limit2 = st.columns(2)
        with col_limit1: limit_piutang = st.text_input("Limit Piutang (Rp)", value=get_val('limit_piutang'))
        with col_limit2: limit_nota = st.text_input("Limit Lembar Nota (Rp)", value=get_val('limit_nota'))

    with col4:
        st.subheader("3. Informasi Pajak, Faktur & Sales")
        pajak_opts = ["NONPKP", "PKP"]
        status_pajak = st.radio("Status Perpajakan", pajak_opts, index=get_idx(pajak_opts, 'status_pajak'), horizontal=True)
        npwp = st.text_input("Nomor NPWP (Jika Ada)", value=get_val('npwp'))
        alamat_npwp = st.text_area("Alamat NPWP", value=get_val('alamat_npwp'))
        
        faktur_opts = ["Faktur Pajak Sesuai Surat Jalan/Nota Kiriman", "Faktur Pajak Sesuai Sale Out", "Faktur Pajak Sesuai Totalan (Konsinyasi dikurangi retur)", "Tidak Minta Faktur Pajak", "Yang lain..."]
        tipe_faktur = st.radio("Tipe Penerbitan Faktur Pajak", faktur_opts, index=get_idx(faktur_opts, 'tipe_faktur'))
        
        metode_opts = ["Dikirim melalui email", "Diprint dan diikutkan dalam tagihan", "Tidak Minta Faktur Pajak", "Yang lain..."]
        metode_faktur = st.radio("Metode Pengiriman Faktur Pajak", metode_opts, index=get_idx(metode_opts, 'metode_faktur'))
        
        po_opts = ["MINTA PO", "LANGSUNG ISI"]
        ket_po = st.radio("Keterangan PO", po_opts, index=get_idx(po_opts, 'ket_po'), horizontal=True)
        diskon = st.text_input("Diskon Toko (%)", value=get_val('diskon'))
        nama_sales = st.text_input("Nama Sales", value=get_val('nama_sales'))

    # Kumpulkan Data Halaman 1
    current_data = {
        'jenis_usaha': jenis_usaha, 'nama_outlet': nama_outlet, 'alamat_kirim': alamat_kirim, 'alamat_tagih': alamat_tagih,
        'kelurahan': kelurahan, 'kecamatan': kecamatan, 'kota': kota, 'kode_pos': kode_pos, 'telepon': telepon, 'email': email,
        'jadwal_kunjungan': jadwal_kunjungan, 'jadwal_penagihan': jadwal_penagihan, 'jadwal_pengiriman': jadwal_pengiriman,
        'kode_pelanggan': kode_pelanggan, 'tgl_pengajuan': tgl_pengajuan.strftime("%d %B %Y"), 'nama_pemilik': nama_pemilik,
        'telp_pemilik': telp_pemilik, 'alamat_pemilik': alamat_pemilik, 'nik': nik, 'nama_pic': nama_pic, 'telp_pic': telp_pic,
        'jabatan': jabatan, 'jumlah_store': jumlah_store, 'channel_dist': channel_dist, 'status_kepemilikan': status_kepemilikan,
        'jenis_bangunan': jenis_bangunan, 'link_gmap': link_gmap, 'tipe_penjualan': tipe_penjualan, 'top_hari': top_hari,
        'jenis_pembayaran': jenis_pembayaran, 'nama_rekening': nama_rekening, 'limit_piutang': limit_piutang, 'limit_nota': limit_nota,
        'status_pajak': status_pajak, 'npwp': npwp, 'alamat_npwp': alamat_npwp, 'tipe_faktur': tipe_faktur, 'metode_faktur': metode_faktur,
        'ket_po': ket_po, 'diskon': diskon, 'nama_sales': nama_sales
    }

    # Auto-Save Logic (HANYA AKTIF DI HALAMAN 1)
    current_json = json.dumps(current_data)
    if current_json != draft_str:
        cookie_manager.set("noo_draft_auto", current_json)

    st.markdown("---")
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        if st.button("🗑️ Hapus Draft", use_container_width=True):
            cookie_manager.delete("noo_draft_auto")
            st.rerun()
    with col_btn2:
        if st.button("Lanjut ke Upload Foto & TTD ➡️", type="primary", use_container_width=True):
            st.session_state.form_data = current_data
            st.session_state.halaman = 2
            st.rerun()


# =====================================================================
# HALAMAN 2: UPLOAD GAMBAR & TANDA TANGAN (TANPA AUTO-SAVE)
# =====================================================================
elif st.session_state.halaman == 2:
    
    data_halaman_1 = st.session_state.form_data
    
    st.info("🟡 **Langkah 2:** Upload gambar dan coretkan tanda tangan Anda. Halaman ini dioptimalkan agar kanvas berjalan lancar tanpa ter-refresh.")
    
    st.subheader("4. Lampiran Foto & Dokumen")
    col_img1, col_img2 = st.columns(2)
    with col_img1:
        ktp_img = st.file_uploader("Upload Foto KTP", type=['jpg', 'jpeg', 'png'])
        depan_img = st.file_uploader("Foto Toko: Tampak Depan", type=['jpg', 'jpeg', 'png'])
        kiri_img = st.file_uploader("Foto Toko: Samping Kiri", type=['jpg', 'jpeg', 'png'])
    with col_img2:
        npwp_img = st.file_uploader("Upload Foto NPWP", type=['jpg', 'jpeg', 'png'])
        dalam_img = st.file_uploader("Foto Toko: Tampak Dalam", type=['jpg', 'jpeg', 'png'])
        kanan_img = st.file_uploader("Foto Toko: Samping Kanan", type=['jpg', 'jpeg', 'png'])

    st.markdown("---")
    st.subheader("5. Tanda Tangan Digital")
    
    col_sig1, col_sig2 = st.columns(2)
    with col_sig1:
        st.write(f"**Tanda Tangan Pelanggan ({data_halaman_1.get('nama_pemilik', '...')})**")
        canvas_pelanggan = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=3, stroke_color="#000000", background_color="#ffffff",
            height=150, width=350, drawing_mode="freedraw", key="canvas_pelanggan",
        )
    with col_sig2:
        st.write(f"**Tanda Tangan Sales ({data_halaman_1.get('nama_sales', '...')})**")
        canvas_sales = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=3, stroke_color="#000000", background_color="#ffffff",
            height=150, width=350, drawing_mode="freedraw", key="canvas_sales",
        )

    st.markdown("---")
    col_back, col_submit = st.columns([1, 4])
    
    with col_back:
        if st.button("⬅️ Kembali Edit Data", use_container_width=True):
            st.session_state.halaman = 1
            st.rerun()
            
    with col_submit:
        if st.button("✅ Submit & Buat PDF", type="primary", use_container_width=True):
            img_sig_p = Image.fromarray(canvas_pelanggan.image_data.astype(np.uint8)) if canvas_pelanggan.image_data is not None else None
            img_sig_s = Image.fromarray(canvas_sales.image_data.astype(np.uint8)) if canvas_sales.image_data is not None else None
            
            # Gabungkan Data Halaman 1 dengan Foto
            data_final = data_halaman_1.copy()
            data_final.update({
                'ktp_img': ktp_img, 'npwp_img': npwp_img, 'depan_img': depan_img, 
                'dalam_img': dalam_img, 'kiri_img': kiri_img, 'kanan_img': kanan_img
            })
            
            pdf_bytes = generate_pdf(data_final, img_sig_p, img_sig_s)
            st.success("PDF berhasil dibuat!")
            st.download_button(label="📄 Download PDF", data=pdf_bytes, file_name=f"Form_NOO_{data_final['nama_outlet']}.pdf", mime="application/pdf", use_container_width=True)