# frontend.py - Puskesmas Sangkali
import streamlit as st
import pandas as pd
from datetime import datetime
import re
import requests
from io import StringIO

st.set_page_config(
    page_title="Puskesmas Sangkali",
    page_icon="🏥",
    layout="wide"
)

# CSS
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #14532d 0%, #166534 100%);
    padding: 2rem;
    border-radius: 20px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}
.main-header h1 { margin: 0; }
.data-card {
    background: white;
    padding: 1.5rem;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    margin-bottom: 1rem;
}
.result-box {
    background: #f8fafc;
    padding: 1rem;
    border-radius: 12px;
    border-left: 5px solid #14532d;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>Puskesmas Sangkali</h1>
    <p>Pelayanan Kesehatan Masyarakat</p>
</div>
""", unsafe_allow_html=True)

# Data nama
DAFTAR_NAMA = [
    "Ahmad Fauzi", "Anisa Rahma", "Budi Santoso", "Citra Dewi", "Dedi Kurniawan",
    "Eka Fitriani", "Fajar Pratama", "Gita Puspita", "Hendra Gunawan", "Indah Lestari",
    "Joko Susilo", "Kartika Sari", "Lukman Hakim", "Maya Sari", "Nanda Putra",
    "Oktavia Dewi", "Prabowo Subroto", "Qonita Zahra", "Rizki Amelia", "Siti Nurjanah",
    "Teguh Prasetyo", "Umi Kalsum", "Vina Oktaviani", "Wahyu Setiawan", "Xena Aulia",
    "Yusuf Maulana", "Zahra Firdaus", "Agus Salim", "Dewi Sartika", "Eko Prasetyo",
    "Fatimah Azzahra", "Gilang Ramadhan", "Hani Nurfadillah", "Ikhsan Pratama", "Jihan Nabila",
    "Khairul Anwar", "Laila Nuraini", "Miftahul Jannah", "Nadya Puspita", "Oscar Fernando"
]

# Fungsi baca Google Sheets CSV
def read_google_sheet_csv(url):
    try:
        sheet_id = None
        publish_match = re.search(r'/spreadsheets/d/e/([a-zA-Z0-9-_]+)', url)
        if publish_match:
            sheet_id = publish_match.group(1)
            csv_url = f"https://docs.google.com/spreadsheets/d/e/{sheet_id}/pub?output=csv"
        else:
            direct_match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
            if direct_match:
                sheet_id = direct_match.group(1)
                csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
            else:
                if 'output=csv' in url or 'export' in url:
                    csv_url = url
                else:
                    return None, "URL tidak valid"
        
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(csv_url, headers=headers)
        response.raise_for_status()
        df = pd.read_csv(StringIO(response.text))
        return df, None
    except Exception as e:
        return None, str(e)

# Inisialisasi data
if "data_kegiatan" not in st.session_state:
    st.session_state.data_kegiatan = [
        {"tanggal": "2026-06-10", "lokasi": "Balai Desa Sangkali", "kegiatan": "Posyandu Balita", "penyerta": "dr. Anita, 10 kader, 35 balita"},
        {"tanggal": "2026-06-15", "lokasi": "SDN Sangkali 1", "kegiatan": "Imunisasi Sekolah", "penyerta": "2 perawat, 1 bidan, 50 siswa"},
        {"tanggal": "2026-06-20", "lokasi": "Puskesmas Sangkali", "kegiatan": "Penyuluhan Lansia", "penyerta": "dr. Budi, 3 perawat, 30 lansia"},
    ]

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2922/2922561.png", width=100)
    st.title("Menu")
    page = st.radio("Pilih Halaman", ["Halaman User", "Halaman Admin"])

# ========== HALAMAN USER ==========
if page == "Halaman User":
    st.title("Cari Jadwal Kegiatan")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("user_form"):
            nama = st.selectbox("Nama Lengkap", DAFTAR_NAMA)
            tanggal = st.date_input("Tanggal Kegiatan", datetime.now().date())
            
            if st.form_submit_button("Cari Jadwal"):
                hasil = [d for d in st.session_state.data_kegiatan if d["tanggal"] == str(tanggal)]
                if hasil:
                    st.success(f"Halo {nama}")
                    for h in hasil:
                        st.markdown(f"""
                        <div class="result-box">
                            <b>Lokasi:</b> {h['lokasi']}<br>
                            <b>Kegiatan:</b> {h['kegiatan']}<br>
                            <b>Penyerta:</b> {h['penyerta']}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning(f"Tidak ada kegiatan tanggal {tanggal}")
    
    with col2:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown("**Informasi**")
        st.markdown("- Datang 15 menit lebih awal\n- Bawa KMS\n- Gunakan masker")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Jadwal terdekat
    st.subheader("Jadwal Terdekat")
    df = pd.DataFrame(st.session_state.data_kegiatan)
    st.dataframe(df[["tanggal", "lokasi", "kegiatan"]], use_container_width=True, hide_index=True)

# ========== HALAMAN ADMIN ==========
else:
    st.title("Halaman Admin")
    
    if not st.session_state.admin_logged_in:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Login"):
                if username == "admin" and password == "admin123":
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("Login gagal")
    else:
        st.success("Admin: Selamat datang")
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()
        
        tab1, tab2, tab3, tab4 = st.tabs(["Input Manual", "Google Sheet", "Pencarian", "Kelola Data"])
        
        # Tab 1: Input Manual
        with tab1:
            with st.form("input_form"):
                col1, col2 = st.columns(2)
                with col1:
                    tgl = st.date_input("Tanggal")
                    lokasi = st.text_input("Lokasi")
                with col2:
                    kegiatan = st.text_input("Kegiatan")
                    penyerta = st.text_area("Penyerta", height=100)
                if st.form_submit_button("Simpan"):
                    st.session_state.data_kegiatan.append({
                        "tanggal": str(tgl),
                        "lokasi": lokasi,
                        "kegiatan": kegiatan,
                        "penyerta": penyerta
                    })
                    st.success("Tersimpan!")
                    st.rerun()
        
        # Tab 2: Google Spreadsheet
        with tab2:
            st.subheader("Sync dari Google Spreadsheet")
            st.caption("File > Share > Publish to web > CSV > Copy link")
            
            url = st.text_input("Link CSV dari Google Spreadsheet")
            
            if st.button("Ambil Data"):
                if url:
                    df, err = read_google_sheet_csv(url)
                    if err:
                        st.error(f"Error: {err}")
                    else:
                        st.success(f"Baca {len(df)} baris")
                        st.dataframe(df.head())
                        
                        cols = ["tanggal", "lokasi", "kegiatan", "penyerta"]
                        if all(c in df.columns for c in cols):
                            if st.button("Import ke Database"):
                                for _, row in df.iterrows():
                                    st.session_state.data_kegiatan.append({
                                        "tanggal": str(row["tanggal"]),
                                        "lokasi": str(row["lokasi"]),
                                        "kegiatan": str(row["kegiatan"]),
                                        "penyerta": str(row["penyerta"])
                                    })
                                st.success("Data diimport!")
                                st.rerun()
                        else:
                            st.error(f"Kolom harus: {cols}")
        
        # Tab 3: Pencarian (output penyerta)
        with tab3:
            with st.form("search_form"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    tgl = st.date_input("Tanggal")
                with col2:
                    lok = st.text_input("Lokasi (opsional)")
                with col3:
                    keg = st.text_input("Kegiatan (opsional)")
                
                if st.form_submit_button("Cari Penyerta"):
                    hasil = []
                    for d in st.session_state.data_kegiatan:
                        if d["tanggal"] != str(tgl):
                            continue
                        if lok and lok.lower() not in d["lokasi"].lower():
                            continue
                        if keg and keg.lower() not in d["kegiatan"].lower():
                            continue
                        hasil.append(d["penyerta"])
                    
                    if hasil:
                        for i, h in enumerate(hasil, 1):
                            st.info(f"Data {i}: {h}")
                    else:
                        st.warning("Tidak ditemukan")
        
        # Tab 4: Kelola Data
        with tab4:
            df = pd.DataFrame(st.session_state.data_kegiatan)
            if len(df) > 0:
                st.dataframe(df, use_container_width=True)
                
                pilihan = st.multiselect("Pilih data yang akan dihapus",
                    [f"{row['tanggal']} - {row['kegiatan']}" for _, row in df.iterrows()])
                
                if st.button("Hapus"):
                    indices = [i for i, row in df.iterrows() 
                              for p in pilihan 
                              if p == f"{row['tanggal']} - {row['kegiatan']}"]
                    st.session_state.data_kegiatan = [item for idx, item in enumerate(st.session_state.data_kegiatan) 
                                                     if idx not in indices]
                    st.success("Data dihapus!")
                    st.rerun()
            else:
                st.info("Belum ada data")

# Footer
st.markdown("---")
st.markdown("<div style='text-align:center'>Puskesmas Sangkali © 2026</div>", unsafe_allow_html=True)
