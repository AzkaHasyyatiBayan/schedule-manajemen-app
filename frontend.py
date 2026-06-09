import streamlit as st
import pandas as pd
import requests
import re
import random
import calendar
from datetime import datetime, date, timedelta
from collections import defaultdict
from io import BytesIO, StringIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

# ---------- Konfigurasi Halaman ----------
st.set_page_config(page_title="Puskesmas Sangkali", page_icon="assets/logo.png", layout="wide")

# ---------- CSS ----------
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
<style>
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #14532d 0%, #166534 60%, #15803d 100%);
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 10px;
    font-weight: 500;
    width: 100%;
    margin-bottom: 4px;
    padding: 0.5rem 0.75rem;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.28);
}
/* FIX 1: Logo sidebar terpusat */
.sidebar-logo-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 1.5rem 1rem 0.5rem;
    width: 100%;
    text-align: center;
}
.sidebar-logo-wrap img {
    display: block;
    margin: 0 auto;
    width: 90px;
    border-radius: 50%;
    border: 3px solid rgba(255,255,255,0.35);
    background: rgba(255,255,255,0.1);
    padding: 4px;
}
/* Override Streamlit image container agar center */
[data-testid="stSidebar"] [data-testid="stImage"] {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}
[data-testid="stSidebar"] [data-testid="stImage"] img {
    margin: 0 auto !important;
}
.sidebar-puskesmas-name {
    font-size: 0.95rem;
    font-weight: 700;
    text-align: center;
    margin: 0.4rem 0 0.25rem;
    width: 100%;
}
.sidebar-puskesmas-sub {
    font-size: 0.75rem;
    text-align: center;
    opacity: 0.75;
    margin-bottom: 0.5rem;
    width: 100%;
}
.sidebar-menu-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
    padding: 0.5rem 0 0.2rem;
    opacity: 0.55;
    text-align: center !important;
}
.sidebar-menu-icon {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 0.85rem;
    margin-bottom: 2px;
}
/* FIX 1: Badge admin tanpa border/kotak */
.sidebar-user-badge {
    font-size: 0.82rem;
    text-align: center;
    margin: 4px 0 8px;
    display: block;
    padding: 4px 0;
}
.badge-online {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(187,247,208,0.2); color: #bbf7d0;
    font-size: 0.78rem; font-weight: 600;
    padding: 3px 10px; border-radius: 999px;
    border: 1px solid rgba(187,247,208,0.3);
}
.badge-offline {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(254,202,202,0.2); color: #fecaca;
    font-size: 0.78rem; font-weight: 600;
    padding: 3px 10px; border-radius: 999px;
    border: 1px solid rgba(254,202,202,0.3);
}
.main-header {
    background: linear-gradient(135deg, rgba(20,83,45,0.85) 0%, rgba(22,101,52,0.85) 100%),
                url('assets/header-bg.jpg') center/cover no-repeat;
    padding: 4rem 2rem;
    border-radius: 20px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}
.main-header h1 { font-size: 2.5rem; font-weight: 700; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
.main-header p { font-size: 1.2rem; margin-top: 0.5rem; text-shadow: 1px 1px 3px rgba(0,0,0,0.3); }
.receipt-box {
    background: #fffef8;
    border: 1px solid #e2e0d8;
    border-radius: 4px;
    padding: 0;
    margin: 1rem 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 4px 12px rgba(0,0,0,0.06);
    font-family: 'Courier New', monospace;
    position: relative;
}
.receipt-box::before {
    content: "";
    display: block;
    height: 6px;
    background: radial-gradient(circle at 6px 6px, transparent 6px, #fffef8 6px) -6px 0,
                linear-gradient(#fffef8, #fffef8);
    background-size: 12px 6px, 100% 100%;
    margin-bottom: 2px;
}
.receipt-box::after {
    content: "";
    display: block;
    height: 6px;
    background: radial-gradient(circle at 6px 0px, transparent 6px, #fffef8 6px) -6px 0;
    background-size: 12px 6px;
    margin-top: 2px;
}
.receipt-header { background: #14532d; color: white; text-align: center; padding: 1rem 1.25rem 0.85rem; }
.receipt-header h3 { margin: 0; font-size: 1rem; font-weight: 700; text-transform: uppercase; }
.receipt-body { padding: 0.5rem 1.25rem; }
.receipt-item { padding: 0.75rem 0; border-bottom: 1px dashed #ddd8cc; }
.receipt-item:last-child { border-bottom: none; }
.receipt-item-title { font-weight: 700; color: #14532d; font-size: 0.92rem; }
.receipt-item-row { display: flex; justify-content: space-between; font-size: 0.82rem; color: #4b5563; }
.receipt-item-label { color: #6b7280; min-width: 80px; }
.receipt-item-value { color: #1f2937; text-align: right; word-break: break-word; }
.receipt-status-badge {
    font-size: 0.72rem; font-weight: 700; padding: 2px 9px; border-radius: 3px; text-transform: uppercase;
}
.status-past { background: #f3f4f6; color: #6b7280; border: 1px solid #d1d5db; }
.status-today { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
.status-soon { background: #dbeafe; color: #1d4ed8; border: 1px solid #93c5fd; }
.status-future { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
.receipt-footer {
    text-align: center; padding: 0.75rem 1.25rem 0.9rem; color: #9ca3af; font-size: 0.75rem; border-top: 2px dashed #c8c5b8;
}
.receipt-barcode { font-size: 1.6rem; letter-spacing: 0.05em; color: #374151; margin: 0.3rem 0; }
.data-card {
    background: white; padding: 1.25rem; border-radius: 14px; border: 1px solid #e5e7eb; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.stat-card {
    background: linear-gradient(135deg, #f0fdf4, #dcfce7); border: 1px solid #bbf7d0; padding: 1.1rem 1.25rem; border-radius: 14px; text-align: center;
}
.stat-card-num { font-size: 1.8rem; font-weight: 700; color: #15803d; }
.history-item { background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 0.85rem 1rem; margin-bottom: 0.6rem; }
.history-item-hadir { border-left: 5px solid #16a34a; }
.history-item-tidak { border-left: 5px solid #dc2626; }
.history-item-netral { border-left: 5px solid #9ca3af; }
.history-badge-hadir {
    background: #dcfce7; color: #15803d; font-size: 0.75rem; font-weight: 600; padding: 2px 10px; border-radius: 999px;
}
.history-badge-tidak {
    background: #fee2e2; color: #dc2626; font-size: 0.75rem; font-weight: 600; padding: 2px 10px; border-radius: 999px;
}
.history-badge-netral {
    background: #f3f4f6; color: #6b7280; font-size: 0.75rem; font-weight: 600; padding: 2px 10px; border-radius: 999px;
}
.stTabs [data-baseweb="tab-list"] { gap: 6px; background: #f0fdf4; border-radius: 12px; padding: 5px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; padding: 8px 16px; font-weight: 500; font-size: 0.88rem; color: #166534; }
.stTabs [aria-selected="true"] { background-color: #14532d !important; color: white !important; }
.puskesmas-footer {
    background: rgba(20, 83, 45, 0.06); padding: 2.5rem 2rem 1.5rem; border-radius: 20px 20px 0 0; margin-top: 2rem;
}
.footer-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem; margin-bottom: 1.75rem; }
.footer-section h4 {
    font-size: 0.95rem; font-weight: 700; color: #14532d;
    border-bottom: 1px solid rgba(20,83,45,0.1); padding-bottom: 0.4rem; margin-bottom: 0.75rem;
}
.footer-section p, .footer-section a { font-size: 0.85rem; color: #374151; line-height: 1.9; text-decoration: none; }
.footer-section a:hover { color: #14532d; }
.footer-section i { width: 18px; margin-right: 6px; color: #166534; }
.footer-social a {
    width: 36px; height: 36px; background: rgba(20,83,45,0.05); border: 1px solid rgba(20,83,45,0.15);
    border-radius: 50%; display: inline-flex; align-items: center; justify-content: center;
    color: #14532d; margin-right: 8px; transition: all 0.2s; text-decoration: none;
}
.footer-social a:hover { background: rgba(20,83,45,0.15); transform: translateY(-2px); }
.footer-divider { border-top: 1px solid rgba(0,0,0,0.05); margin: 1rem 0; }
.footer-bottom { text-align: center; font-size: 0.8rem; color: #6b7280; }
@media (max-width: 768px) {
    .main-header h1 { font-size: 1.6rem; }
    .footer-grid { grid-template-columns: 1fr; }
}
</style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
for key, default in [
    ('logged_in', False), ('token', None), ('username', ''),
    ('page', 'user'), ('edit_data', None), ('edit_id', None),
    ('last_csv_url', ''), ('notif', None), ('pending_delete_ids', []),
    ('user_history_status', {}),
    ('show_csv_input', False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- CONSTANTS ----------
API_BASE = "http://localhost:8000/api"

DAFTAR_NAMA = [
    "Isep Deni Herdian, S.Kep.,MMRS",
    "Isep Suhendar,SKM",
    "Bdn. Yeni Yulyani Setianingsih, S.ST",
    "Bdn. Nina Ainun, S.Tr.Keb",
    "Rita Sahara, S.Tr.Keb",
    "Dewi Sri Mulyani, Am.Keb",
    "Pipit Puspitasari, Am.Keb",
    "Mira Jatnikawati, Am.Keb",
    "Reni Mustikasari, Am.Keb",
    "Alitsa Nuur Fithri, S.ST",
    "Yesi Apriyani, Am.Keb",
    "Asri Awulan, S.Tr.Keb",
    "Pia Nur Podiana, A.Md.Keb",
    "Intang Sri Purnama, AM.Keb",
    "Ucu Lestari, AM.Keb",
    "Annisa Nafaulloh,S.Tr.Keb.,Bdn",
    "Mutia Wulansari.,S.Kep.,Ners",
    "Ujang Effendi, S.Kep.,Ners",
    "Liska Permatasari, S.Kep.,Ners",
    "Dede Khaerul Kamal Muchtar, AMK",
    "Iman Nurul Haq, A.Md.Kep",
    "Wida Idul Adha, S.Kep.,Ners",
    "Oriany Kemala Dewi, Amd.Kep",
    "Haeriah, A.Md.Kep",
    "Dede Aan Septiantini, A.Md.Kep",
    "dr.Ferry Nalapraya",
    "dr.Muhammad Azhary Romdhon",
    "dr.Iwan Setiawan",
    "dr. Siti Hana Fukui",
    "dr. Volti Diana Suryawadi",
    "drg.Rifan Hanggoro.M.M.R.S",
    "Endah Setiawati,S.Tr.Kes",
    "Khilman Husna Pratama, S.Farm.,Apt",
    "Vita Tyana Virista, A.Md.AK",
    "Gina Giovany, A.Md.AK",
    "Eko Wahyu Saputro, S.K.M",
    "Nurul Hasanah, A.Md.KL",
    "Nova Silpiany Perdany, A.Md.Farm",
    "Ameilia Putri Isyari, S.Gz",
    "Annisa Fauziah, A.Md.Gz",
    "Rudi Sutikno, SKM",
    "Yogi Aris Diyanto, S.E",
    "Rangga Ismardana Gasbela,S.T",
    "Winda Siti Sarah, AMd.RMIK",
    "Pupung Juliana",
    "Salsa Sabila",
    "Andina Dea Priatna, SKM",
    "Iip Supyan"
]

PENDAFTARAN_TETAP  = ["Winda Siti Sarah, AMd.RMIK", "Pupung Juliana", "Salsa Sabila"]
BP_GIGI_TETAP      = ["drg.Rifan Hanggoro.M.M.R.S", "Endah Setiawati,S.Tr.Kes"]
APOTEK_TETAP       = ["Khilman Husna Pratama, S.Farm.,Apt", "Nova Silpiany Perdany, A.Md.Farm"]
LAB_TETAP          = ["Vita Tyana Virista, A.Md.AK", "Gina Giovany, A.Md.AK"]
PUSTU_CIANGIR      = "Haeriah, A.Md.Kep"
PUSTU_SUMELAP      = "Ujang Effendi, S.Kep.,Ners"
ADMINISTRASI_TETAP = ["Rangga Ismardana Gasbela,S.T", "Yogi Aris Diyanto, S.E"]
ADMINISTRASI_EXTRA = ["Liska Permatasari, S.Kep.,Ners", "Alitsa Nuur Fithri, S.ST", "Andina Dea Priatna, SKM"]
NAMA_DIECUALIKAN   = ["Isep Deni Herdian, S.Kep.,MMRS", "Isep Suhendar,SKM"]

ROLE_MAP = {
    'dokter': ['dr.', 'drg.'],
    'perawat_ners': ['Ners', 'S.Kep', 'Amd.Kep', 'A.Md.Kep'],
    'bidan': ['Bdn.', 'S.Tr.Keb', 'Am.Keb', 'A.Md.Keb'],
    'promkes': ['Promosi', 'SKM'],
    'sanitarian': ['Sanitarian', 'S.K.M', 'A.Md.KL'],
    'gizi': ['S.Gz', 'A.Md.Gz'],
    'apoteker': ['Apt', 'S.Farm'],
    'lab': ['A.Md.AK'],
    'gigi': ['drg.', 'S.Tr.Kes'],
    'administrasi': ['S.E', 'S.T', 'S.Kep', 'S.ST', 'SKM', 'AMd.RMIK'],
}

def get_karyawan_by_role(role_key, exclude=None):
    if exclude is None: exclude = []
    keywords = ROLE_MAP.get(role_key, [])
    hasil = []
    for nama in DAFTAR_NAMA:
        if nama in exclude: continue
        if any(kw.lower() in nama.lower() for kw in keywords):
            hasil.append(nama)
    return list(set(hasil))

def filter_nama(nama_list):
    return [n for n in nama_list if n not in NAMA_DIECUALIKAN]

def get_by_role_clean(keywords):
    semua = [n for n in DAFTAR_NAMA if any(kw.lower() in n.lower() for kw in keywords)]
    return filter_nama(semua)

# ---------- HELPER API ----------
def auth_headers():
    return {"Authorization": f"Token {st.session_state.token}"}

def api_get(path, params=None, auth=False):
    h = auth_headers() if auth else {}
    return requests.get(f"{API_BASE}/{path}", params=params, headers=h, timeout=10)

def api_post(path, data, auth=False):
    h = {"Content-Type": "application/json"}
    if auth: h.update(auth_headers())
    return requests.post(f"{API_BASE}/{path}", json=data, headers=h, timeout=10)

def api_put(path, data):
    return requests.put(f"{API_BASE}/{path}", json=data, headers=auth_headers(), timeout=10)

def api_delete(path):
    return requests.delete(f"{API_BASE}/{path}", headers=auth_headers(), timeout=10)

def parse_penyerta(teks):
    if not teks: return []
    if ';' in teks:
        return [p.strip() for p in teks.split(';') if p.strip()]
    parts = re.split(r', (?=[A-Z])', teks)
    return [p.strip() for p in parts if p.strip()]

def show_notif(message, notif_type="success"):
    icons = {"success": "✅", "error": "❌", "info": "ℹ️"}
    st.toast(message, icon=icons.get(notif_type, "ℹ️"))

# ---------- FIX 3 & 4: PDF & CSV FUNCTIONS ----------

def generate_jadwal_pdf(data):
    """FIX 3: PDF sekarang menampilkan data row per row dengan benar"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=0.4*inch, rightMargin=0.4*inch,
        topMargin=0.5*inch, bottomMargin=0.5*inch
    )
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=14,
        alignment=1,
        spaceAfter=6,
        textColor=colors.HexColor('#14532d')
    )
    sub_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,
        spaceAfter=14,
        textColor=colors.HexColor('#166534')
    )
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=7,
        leading=9,
        wordWrap='LTR'
    )

    story = []
    story.append(Paragraph("JADWAL PELAYANAN PUSKESMAS SANGKALI", title_style))
    story.append(Paragraph(f"Dicetak: {datetime.now().strftime('%d %B %Y, %H:%M')}", sub_style))
    story.append(Spacer(1, 6))

    if not data:
        story.append(Paragraph("Tidak ada data jadwal.", styles['Normal']))
        doc.build(story)
        buffer.seek(0)
        return buffer

    df = pd.DataFrame(data)

    # Pastikan kolom yang dibutuhkan ada
    for col in ['tanggal', 'lokasi', 'kegiatan', 'penyerta']:
        if col not in df.columns:
            df[col] = ''

    df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
    df = df.sort_values('tanggal')
    df['tanggal_str'] = df['tanggal'].dt.strftime('%A,\n%d %b %Y')

    # Header tabel
    col_widths = [1.5*inch, 1.4*inch, 2.0*inch, 5.6*inch]
    headers = ['TANGGAL', 'LOKASI', 'KEGIATAN', 'PELAKSANA / PENYERTA']

    table_data = [[Paragraph(f'<b>{h}</b>', cell_style) for h in headers]]

    for _, row in df.iterrows():
        tgl_display = row['tanggal_str'] if pd.notna(row['tanggal']) else str(row.get('tanggal', ''))
        penyerta_bersih = str(row.get('penyerta', '')).replace(';', '\n').strip()
        table_data.append([
            Paragraph(tgl_display, cell_style),
            Paragraph(str(row.get('lokasi', '')), cell_style),
            Paragraph(str(row.get('kegiatan', '')), cell_style),
            Paragraph(penyerta_bersih, cell_style),
        ])

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#14532d')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0fdf4')]),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#d1d5db')),
        ('TOPPADDING', (0, 1), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        f"Dicetak dari Sistem Puskesmas Sangkali © {datetime.now().year} | Total: {len(df)} kegiatan",
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=colors.grey, alignment=1)
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_csv(data, filename="jadwal.csv"):
    """FIX 4: CSV sekarang benar-benar dipisah per kolom, bukan numpuk di satu kolom"""
    if not data:
        st.download_button("Download CSV", data=b"TANGGAL,LOKASI,KEGIATAN,PELAKSANA\n",
                           file_name=filename, mime='text/csv', use_container_width=True)
        return

    df = pd.DataFrame(data)

    # Rename kolom sesuai kebutuhan
    rename_map = {
        'tanggal': 'TANGGAL',
        'lokasi': 'LOKASI',
        'kegiatan': 'KEGIATAN',
        'penyerta': 'PELAKSANA'
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Pastikan hanya kolom yang diperlukan, dalam urutan yang benar
    kolom_diinginkan = ['TANGGAL', 'LOKASI', 'KEGIATAN', 'PELAKSANA']
    kolom_tersedia = [c for c in kolom_diinginkan if c in df.columns]
    df = df[kolom_tersedia]

    # Format tanggal jika ada
    if 'TANGGAL' in df.columns:
        df['TANGGAL'] = pd.to_datetime(df['TANGGAL'], errors='coerce').dt.strftime('%Y-%m-%d')

    # Tulis CSV dengan benar: pakai StringIO lalu encode
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False, encoding='utf-8-sig', sep=',', quoting=1)
    csv_bytes = csv_buffer.getvalue().encode('utf-8-sig')

    st.download_button(
        "⬇️ Download CSV",
        data=csv_bytes,
        file_name=filename,
        mime='text/csv',
        use_container_width=True
    )


# ---------- TOKEN URL ----------
params = st.query_params
if not st.session_state.logged_in and 'token' in params:
    token = params['token']
    try:
        resp = requests.get(f"{API_BASE}/verify-token/", headers={"Authorization": f"Token {token}"}, timeout=5)
        if resp.status_code == 200:
            d = resp.json()
            st.session_state.logged_in = True
            st.session_state.token = token
            st.session_state.username = d.get('username', 'Admin')
            st.query_params.clear()
            st.rerun()
        else:
            st.query_params.clear()
    except:
        pass

if st.session_state.notif:
    show_notif(st.session_state.notif)
    st.session_state.notif = None

# ---------- SIDEBAR ----------
with st.sidebar:
    # FIX 1: Logo terpusat - gunakan st.columns trick untuk centering
    col_left, col_center, col_right = st.columns([0.5, 3, 0.5])
    with col_center:
        try:
            st.image("assets/logo.png", width=90)
        except:
            st.markdown("""
            <div style="display:flex;justify-content:center;">
            <svg width="80" height="80" viewBox="0 0 80 80">
                <circle cx="40" cy="40" r="38" fill="rgba(255,255,255,0.15)" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
                <rect x="35" y="20" width="10" height="40" rx="3" fill="white"/>
                <rect x="20" y="35" width="40" height="10" rx="3" fill="white"/>
            </svg>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-puskesmas-name">UPTD Puskesmas<br>Sangkali</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-puskesmas-sub">Tasikmalaya, Jawa Barat</div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-menu-label">Navigasi</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([0.2, 0.8])
    with col1:
        st.markdown('<div class="sidebar-menu-icon"><i class="fa-solid fa-calendar-days"></i></div>', unsafe_allow_html=True)
    with col2:
        if st.button("Jadwal Kegiatan", use_container_width=True):
            st.session_state.page = "user"; st.rerun()
    if not st.session_state.logged_in:
        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            st.markdown('<div class="sidebar-menu-icon"><i class="fa-solid fa-lock"></i></div>', unsafe_allow_html=True)
        with col2:
            if st.button("Login Admin", use_container_width=True):
                st.session_state.page = "admin_login"; st.rerun()
    else:
        # FIX 1: Badge admin tanpa kotak/border
        st.markdown(
            f'<div class="sidebar-user-badge"><i class="fa-solid fa-circle-user"></i> {st.session_state.username}</div>',
            unsafe_allow_html=True
        )
        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            st.markdown('<div class="sidebar-menu-icon"><i class="fa-solid fa-gauge"></i></div>', unsafe_allow_html=True)
        with col2:
            if st.button("Dashboard Admin", use_container_width=True):
                st.session_state.page = "admin_dashboard"; st.rerun()
        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            st.markdown('<div class="sidebar-menu-icon"><i class="fa-solid fa-right-from-bracket"></i></div>', unsafe_allow_html=True)
        with col2:
            if st.button("Logout", use_container_width=True):
                try: api_post("logout/", {}, auth=True)
                except: pass
                st.session_state.logged_in = False; st.session_state.token = None; st.session_state.username = ''
                st.session_state.page = "user"; st.query_params.clear(); st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)
    try:
        r = requests.get(f"{API_BASE}/jadwal-terdekat/", timeout=3)
        if r.status_code == 200:
            st.markdown('<span class="badge-online"><i class="fa-solid fa-circle-dot"></i> Online</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge-offline"><i class="fa-solid fa-circle-exclamation"></i> Error</span>', unsafe_allow_html=True)
    except:
        st.markdown('<span class="badge-offline"><i class="fa-solid fa-circle-exclamation"></i> Offline</span>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.7rem; opacity:0.6; text-align:center;"><i class="fa-solid fa-clock"></i> Senin–Jumat 07:30–14:00</div>', unsafe_allow_html=True)

# ---------- HEADER ----------
if st.session_state.page == "user":
    st.markdown('<div class="main-header"><h1>Puskesmas Sangkali</h1><p>Sistem Informasi Manajemen Kegiatan</p></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="main-header"><h1>Puskesmas Sangkali</h1><p>Dashboard Manajemen</p></div>', unsafe_allow_html=True)

# ============================================================
# USER PAGE
# ============================================================
if st.session_state.page == "user":
    # Notifikasi
    try:
        today = date.today(); tomorrow = today + timedelta(days=1)
        resp_notif = requests.get(f"{API_BASE}/jadwal-terdekat/", timeout=3)
        if resp_notif.status_code == 200:
            jadwal = resp_notif.json()
            notif_hari_ini = [j for j in jadwal if j['tanggal'] == str(today)]
            notif_besok = [j for j in jadwal if j['tanggal'] == str(tomorrow)]
            if notif_hari_ini:
                items = ''.join(f"<li><b>{j['kegiatan']}</b> — {j['lokasi']}</li>" for j in notif_hari_ini[:6])
                st.markdown(f"<div style='background:#dcfce7;border:1px solid #bbf7d0;padding:1rem;border-radius:12px;margin-bottom:0.75rem;'><i class='fa-solid fa-circle-exclamation'></i> <b>Hari ini:</b><ul>{items}</ul></div>", unsafe_allow_html=True)
            if notif_besok:
                items = ''.join(f"<li><b>{j['kegiatan']}</b> — {j['lokasi']}</li>" for j in notif_besok[:6])
                st.markdown(f"<div style='background:#eff6ff;border:1px solid #bfdbfe;padding:1rem;border-radius:12px;margin-bottom:0.75rem;'><i class='fa-solid fa-calendar-check'></i> <b>Besok:</b><ul>{items}</ul></div>", unsafe_allow_html=True)
    except: pass

    # Cari Jadwal
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown('<div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem"><i class="fa-solid fa-magnifying-glass" style="color:#14532d;"></i><span style="font-size:1.3rem;font-weight:700;color:#14532d;">Cari Jadwal Kegiatan</span></div>', unsafe_allow_html=True)
        with st.form("user_form"):
            nama = st.selectbox("Nama Lengkap", DAFTAR_NAMA)
            tanggal = st.date_input("Tanggal", datetime.now().date())
            if st.form_submit_button("Cari"):
                resp = api_get("search-user/", params={"nama": nama, "tanggal": str(tanggal)})
                if resp.status_code == 200 and resp.json():
                    hasil = resp.json()
                    tgl_fmt = tanggal.strftime('%A, %d %B %Y')
                    items = ""
                    for h in hasil:
                        peny_items = " &bull; ".join(parse_penyerta(h['penyerta'])) or h['penyerta']
                        items += f"<div class='receipt-item'><div class='receipt-item-title'>{h['kegiatan']}</div><div class='receipt-item-row'><span class='receipt-item-label'>Lokasi</span><span class='receipt-item-value'>{h['lokasi']}</span></div><div class='receipt-item-row'><span class='receipt-item-label'>Penyerta</span><span class='receipt-item-value'>{peny_items}</span></div></div>"
                    st.markdown(f"<div class='receipt-box'><div class='receipt-header'><h3>Jadwal Kegiatan</h3><p>{tgl_fmt}</p></div><div class='receipt-body'>{items}</div><div class='receipt-footer'><div class='receipt-barcode'>|||||||||||||||||||||||</div>Puskesmas Sangkali</div></div>", unsafe_allow_html=True)
                else:
                    st.warning("Tidak ada kegiatan.")
    with col2:
        st.markdown('<div class="data-card"><div style="display:flex;align-items:center;gap:6px;margin-bottom:0.5rem"><i class="fa-solid fa-circle-info" style="color:#14532d;"></i><span style="font-weight:700;color:#14532d;">Informasi</span></div><ul style="font-size:0.88rem;line-height:1.8;"><li>Datang 15 menit lebih awal</li><li>Bawa KMS/BPJS</li><li>Gunakan masker</li></ul></div>', unsafe_allow_html=True)

    # FIX 2: History Kehadiran User - perbaikan query API
    st.markdown("---")
    st.markdown('<div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem"><i class="fa-solid fa-clock-rotate-left" style="color:#14532d;"></i><span style="font-size:1.2rem;font-weight:700;color:#14532d;">Riwayat Kehadiran Saya</span></div>', unsafe_allow_html=True)
    col_f1, col_f2, col_f3 = st.columns([2,2,1])
    with col_f1: nama_riwayat = st.selectbox("Nama", DAFTAR_NAMA, key="nama_riwayat")
    with col_f2: bulan_riwayat = st.selectbox("Bulan", ["Semua"] + list(calendar.month_name)[1:], key="bulan_riwayat")
    with col_f3: tahun_riwayat = st.number_input("Tahun", value=datetime.now().year, min_value=2020, max_value=2030)
    if st.button("Tampilkan Riwayat"):
        try:
            # FIX 2: Coba endpoint search-user terlebih dulu, lalu fallback ke kegiatan/
            berhasil = False

            # Coba endpoint kegiatan/ dengan auth jika login, tanpa auth jika tidak
            resp = api_get("kegiatan/", auth=st.session_state.logged_in)

            if resp.status_code == 200:
                berhasil = True
                raw_data = resp.json()
            else:
                # Fallback: coba tanpa auth
                resp2 = api_get("kegiatan/")
                if resp2.status_code == 200:
                    berhasil = True
                    raw_data = resp2.json()

            if berhasil and raw_data:
                df = pd.DataFrame(raw_data)
                df['tanggal_dt'] = pd.to_datetime(df['tanggal'], errors='coerce')

                # Filter berdasarkan nama - cek setiap bagian nama
                nama_parts = [p.strip() for p in nama_riwayat.replace(',', ' ').split() if len(p.strip()) > 2]
                keyword_utama = nama_riwayat.split(',')[0].strip()

                def cek_nama_match(penyerta_text):
                    if not penyerta_text:
                        return False
                    return keyword_utama.lower() in penyerta_text.lower()

                df_filtered = df[df['penyerta'].apply(cek_nama_match)]
                df_filtered = df_filtered[df_filtered['tanggal_dt'].dt.year == tahun_riwayat]

                if bulan_riwayat != "Semua":
                    bulan_num = list(calendar.month_name).index(bulan_riwayat)
                    df_filtered = df_filtered[df_filtered['tanggal_dt'].dt.month == bulan_num]

                df_filtered = df_filtered.sort_values('tanggal_dt', ascending=False)

                if df_filtered.empty:
                    st.info(f"Tidak ada kegiatan ditemukan untuk {nama_riwayat}.")
                else:
                    st.success(f"Ditemukan {len(df_filtered)} kegiatan")
                    for _, row in df_filtered.iterrows():
                        id_keg = row.get('id')
                        status = st.session_state.user_history_status.get(id_keg, 'belum')
                        if status == 'hadir':
                            cls = "history-item-hadir"; badge = "Hadir"; badge_cls = "history-badge-hadir"
                        elif status == 'tidak_hadir':
                            cls = "history-item-tidak"; badge = "Tidak Hadir"; badge_cls = "history-badge-tidak"
                        else:
                            cls = "history-item-netral"; badge = "Belum"; badge_cls = "history-badge-netral"
                        st.markdown(
                            f"<div class='history-item {cls}'>"
                            f"<b>{row['tanggal_dt'].strftime('%A, %d %B %Y')}</b> — {row['kegiatan']}<br>"
                            f"<small>{row['lokasi']}</small><br>"
                            f"<span class='{badge_cls}'>{badge}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                        if row['tanggal_dt'].date() <= date.today():
                            ca, cb, _ = st.columns([1, 1, 2])
                            with ca:
                                if st.button("Hadir", key=f"hadir_{id_keg}"):
                                    st.session_state.user_history_status[id_keg] = 'hadir'; st.rerun()
                            with cb:
                                if st.button("Tidak", key=f"tidak_{id_keg}"):
                                    st.session_state.user_history_status[id_keg] = 'tidak_hadir'; st.rerun()
            elif berhasil and not raw_data:
                st.info("Belum ada data kegiatan di sistem.")
            else:
                st.warning("Gagal memuat data. Pastikan server berjalan dan endpoint /api/kegiatan/ dapat diakses.")
        except requests.exceptions.ConnectionError:
            st.error("Tidak dapat terhubung ke server. Pastikan server Django sudah berjalan.")
        except requests.exceptions.Timeout:
            st.error("Koneksi timeout. Server tidak merespons.")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")

    # Jadwal Terdekat
    st.markdown("---")
    st.markdown('<div style="display:flex;align-items:center;gap:8px;"><i class="fa-solid fa-calendar-week" style="color:#14532d;"></i><span style="font-size:1.2rem;font-weight:700;color:#14532d;">Jadwal Terdekat</span></div>', unsafe_allow_html=True)
    try:
        resp_jadwal = api_get("jadwal-terdekat/")
        if resp_jadwal.status_code == 200:
            jadwal = resp_jadwal.json()
            if jadwal:
                df = pd.DataFrame(jadwal)
                df.columns = ['Tanggal', 'Lokasi', 'Kegiatan', 'Penyerta']
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Belum ada jadwal terdekat.")
        else:
            st.warning("Gagal memuat jadwal.")
    except:
        st.warning("Gagal memuat jadwal.")

# ============================================================
# LOGIN ADMIN
# ============================================================
elif st.session_state.page == "admin_login":
    col_c, col_m, col_c2 = st.columns([1,2,1])
    with col_m:
        st.markdown("<h3 style='text-align:center;color:#14532d;'><i class='fa-solid fa-lock'></i> Login Admin</h3>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Masuk"):
                if not username or not password: show_notif("Isi username dan password.", "error")
                else:
                    resp = api_post("login/", {"username": username, "password": password})
                    if resp.status_code == 200:
                        d = resp.json()
                        st.session_state.logged_in = True; st.session_state.token = d['token']
                        st.session_state.username = d.get('username', username)
                        st.session_state.page = "admin_dashboard"
                        st.query_params["token"] = d['token']; st.rerun()
                    elif resp.status_code == 429: show_notif("Terlalu banyak percobaan.", "error")
                    else: show_notif(resp.json().get('error', 'Login gagal'), "error")

# ============================================================
# DASHBOARD ADMIN
# ============================================================
elif st.session_state.page == "admin_dashboard":
    if not st.session_state.logged_in or not st.session_state.token:
        st.warning("Login dulu."); st.session_state.page = "admin_login"; st.rerun()

    st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:1rem;"><i class="fa-solid fa-gauge" style="color:#14532d;"></i><span style="font-size:1.4rem;font-weight:700;color:#14532d;">Dashboard Admin</span><span style="margin-left:auto;background:#dcfce7;color:#15803d;font-weight:600;padding:4px 12px;border-radius:999px;">{st.session_state.username}</span></div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Input Manual", "Google Sheet", "Pencarian", "Kelola Data",
        "History", "Randomize (Dalam Gedung)"
    ])

    # ── Tab 1: Input Manual ──
    with tab1:
        with st.form("input_form"):
            col1, col2 = st.columns(2)
            with col1: tgl = st.date_input("Tanggal"); lokasi = st.text_input("Lokasi")
            with col2: kegiatan = st.text_input("Nama Kegiatan")
            penyerta_terpilih = st.multiselect("Pilih Penyerta", options=DAFTAR_NAMA)
            if not penyerta_terpilih:
                penyerta = st.text_area("Atau tulis manual (pisahkan ;)", height=80)
            else: penyerta = "; ".join(penyerta_terpilih); st.caption(f"Penyerta: {penyerta}")
            if st.form_submit_button("Simpan"):
                if not lokasi or not kegiatan: show_notif("Lokasi dan Kegiatan wajib diisi.", "error")
                else:
                    resp = api_post("kegiatan/", {"tanggal": str(tgl), "lokasi": lokasi, "kegiatan": kegiatan, "penyerta": penyerta}, auth=True)
                    if resp.status_code == 201: st.session_state.notif = "Data berhasil disimpan!"; st.rerun()
                    else: show_notif(f"Gagal: {resp.text}", "error")

    # ── Tab 2: Google Sheet ──
    with tab2:
        st.markdown('<h4><i class="fa-solid fa-cloud-arrow-up"></i> Sync Google Spreadsheet</h4>', unsafe_allow_html=True)
        st.info("Kolom: `tanggal`, `lokasi`, `kegiatan`, `penyerta`")
        if st.session_state.last_csv_url:
            st.markdown(f"Link tersimpan: {st.session_state.last_csv_url}")
            col_upd, col_del = st.columns(2)
            with col_upd:
                if st.button("Update Link"): st.session_state.show_csv_input = True
            with col_del:
                if st.button("Hapus Link"): st.session_state.last_csv_url = ""; st.rerun()
            if st.session_state.get('show_csv_input'):
                csv_url = st.text_input("Link CSV baru", key="csv_url_new")
                sync_mode = st.radio("Mode", ['append','replace'], horizontal=True, format_func=lambda x: "Tambahkan" if x=='append' else "Ganti semua")
                if st.button("Simpan & Sync"):
                    if csv_url:
                        resp = api_post("sync-sheets/", {"csv_url": csv_url, "mode": sync_mode}, auth=True)
                        if resp.status_code == 200:
                            st.session_state.last_csv_url = csv_url; st.session_state.show_csv_input = False
                            st.session_state.notif = "Sync berhasil!"; st.rerun()
                        else: show_notif(resp.json().get('error'), "error")
        else:
            csv_url = st.text_input("Link CSV terpublikasi", key="csv_url_blank")
            sync_mode = st.radio("Mode", ['append','replace'], horizontal=True, format_func=lambda x: "Tambahkan" if x=='append' else "Ganti semua")
            if st.button("Ambil & Simpan"):
                if csv_url:
                    resp = api_post("sync-sheets/", {"csv_url": csv_url, "mode": sync_mode}, auth=True)
                    if resp.status_code == 200: st.session_state.last_csv_url = csv_url; st.session_state.notif = "Sync berhasil!"; st.rerun()
                    else: show_notif(resp.json().get('error'), "error")

    # ── Tab 3: Pencarian ──
    with tab3:
        try:
            resp_data = api_get("kegiatan/", auth=True)
            semua_data = resp_data.json() if resp_data.status_code == 200 else []
        except: semua_data = []
        lokasi_list = sorted(set(d['lokasi'] for d in semua_data if d.get('lokasi')))
        kegiatan_list = sorted(set(d['kegiatan'] for d in semua_data if d.get('kegiatan')))
        penyerta_set = set()
        for d in semua_data:
            for n in parse_penyerta(d.get('penyerta','')):
                if n: penyerta_set.add(n)
        penyerta_list = sorted(penyerta_set)

        st.markdown('<h4><i class="fa-solid fa-filter"></i> Filter Pencarian</h4>', unsafe_allow_html=True)
        with st.form("search_form"):
            col1, col2, col3 = st.columns(3)
            with col1: tgl_src = st.date_input("Tanggal", value=None, key="src_tgl")
            with col2:
                lok_dd = st.selectbox("Lokasi", ["Semua"] + lokasi_list + ["Cari manual..."])
                lok_src = st.text_input("Ketik lokasi") if lok_dd == "Cari manual..." else ("" if lok_dd == "Semua" else lok_dd)
            with col3:
                keg_dd = st.selectbox("Kegiatan", ["Semua"] + kegiatan_list + ["Cari manual..."])
                keg_src = st.text_input("Ketik kegiatan") if keg_dd == "Cari manual..." else ("" if keg_dd == "Semua" else keg_dd)
            peny_dd = st.selectbox("Penyerta", ["Semua"] + penyerta_list + ["Cari manual..."])
            peny_src = st.text_input("Ketik penyerta") if peny_dd == "Cari manual..." else ("" if peny_dd == "Semua" else peny_dd)

            if st.form_submit_button("Cari"):
                params = {}
                if tgl_src: params["tanggal"] = str(tgl_src)
                if lok_src: params["lokasi"] = lok_src
                if keg_src: params["kegiatan"] = keg_src
                if peny_src: params["penyerta"] = peny_src
                if not params:
                    st.warning("Isi minimal satu filter.")
                else:
                    try:
                        resp = api_get("search-admin/", params=params, auth=True)
                        if resp.status_code == 200:
                            hasil = resp.json()
                            if hasil:
                                groups = defaultdict(list)
                                for item in hasil:
                                    key = (item['tanggal'], item['lokasi'], item['kegiatan'])
                                    groups[key].append(item['penyerta'])
                                st.success(f"Ditemukan {len(groups)} grup data")
                                for (tanggal, lokasi, kegiatan), list_penyerta in groups.items():
                                    all_names = []
                                    for p_text in list_penyerta:
                                        all_names.extend(parse_penyerta(p_text))
                                    penyerta_gabung = '<br>'.join(all_names)
                                    st.markdown(f"""
                                    <div class="result-box">
                                        <b>{tanggal}</b> - {lokasi}<br>
                                        {kegiatan}<br>
                                        <small>{penyerta_gabung}</small>
                                    </div>
                                    """, unsafe_allow_html=True)
                            else:
                                st.info("Tidak ditemukan")
                        else:
                            show_notif("Gagal mengambil data", "error")
                    except Exception as e:
                        st.error(f"Error: {e}")

        # Cek Karyawan Tidak Terjadwal
        st.markdown("---")
        st.markdown('<h4><i class="fa-solid fa-user-plus"></i> Cek Karyawan Tidak Terjadwal</h4>', unsafe_allow_html=True)
        st.caption("Lihat karyawan tanpa jadwal dalam gedung pada tanggal tertentu.")
        col_cek1, col_cek2, col_cek3 = st.columns([2, 2, 1])
        with col_cek1: tgl_cek = st.date_input("Pilih Tanggal", datetime.now().date(), key="tgl_cek_karyawan")
        with col_cek2: role_filter = st.multiselect("Filter Role", ["Dokter","Perawat","Bidan","Promkes","Sanitarian","Gizi","Apoteker","Lab","Gigi","Administrasi"], default=[])
        with col_cek3:
            if st.button("Cek", use_container_width=True, type="primary"):
                tgl_str = str(tgl_cek)
                NAMA_DIECUALIKAN = ["Isep Deni Herdian, S.Kep.,MMRS", "Isep Suhendar,SKM"]
                def get_karyawan_by_role_local(role_keywords):
                    role_map = {
                        'dokter': ['dr.', 'drg.'], 'perawat_ners': ['Ners', 'S.Kep', 'Amd.Kep', 'A.Md.Kep'],
                        'bidan': ['Bdn.', 'S.Tr.Keb', 'Am.Keb', 'A.Md.Keb'], 'promkes': ['Promosi', 'SKM'],
                        'sanitarian': ['Sanitarian', 'S.K.M', 'A.Md.KL'], 'gizi': ['S.Gz', 'A.Md.Gz'],
                        'apoteker': ['Apt', 'S.Farm'], 'lab': ['A.Md.AK'], 'gigi': ['drg.', 'S.Tr.Kes'],
                        'administrasi': ['S.E', 'S.T', 'S.Kep', 'S.ST', 'SKM', 'AMd.RMIK']
                    }
                    keywords = role_map.get(role_keywords, [])
                    hasil = []
                    for nama in DAFTAR_NAMA:
                        for kw in keywords:
                            if kw.lower() in nama.lower():
                                if nama not in NAMA_DIECUALIKAN: hasil.append(nama); break
                    return list(set(hasil))
                semua_karyawan = []
                if not role_filter: roles = list(ROLE_MAP.keys())
                else: roles = [r for r in role_filter if r in ROLE_MAP]
                for role in roles: semua_karyawan.extend(get_karyawan_by_role_local(role))
                semua_karyawan = list(set(semua_karyawan))
                if not semua_karyawan:
                    st.warning("Tidak ada karyawan.")
                else:
                    try:
                        resp_jadwal = api_get("kegiatan/", auth=True)
                        if resp_jadwal.status_code == 200:
                            jadwal_tanggal = [j for j in resp_jadwal.json() if j['tanggal'] == tgl_str]
                            karyawan_terjadwal = set()
                            for j in jadwal_tanggal: karyawan_terjadwal.update(parse_penyerta(j['penyerta']))
                            tidak_terjadwal = [k for k in semua_karyawan if k not in karyawan_terjadwal]
                            if tidak_terjadwal:
                                st.warning(f"{len(tidak_terjadwal)} karyawan tidak terjadwal.")
                                df = pd.DataFrame({"No": range(1,len(tidak_terjadwal)+1), "Nama": sorted(tidak_terjadwal)})
                                st.dataframe(df, use_container_width=True, hide_index=True)
                                st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8-sig'), f"tidak_terjadwal_{tgl_str}.csv", 'text/csv')
                            else: st.success("Semua sudah terjadwal.")
                    except: st.error("Gagal mengambil data.")

    # ── Tab 4: Kelola Data ──
    with tab4:
        st.subheader("Daftar Semua Kegiatan")
        try:
            resp = api_get("kegiatan/", auth=True)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    df_raw = pd.DataFrame(data)
                    df_grouped = (
                        df_raw.groupby(['tanggal', 'lokasi', 'kegiatan'], sort=False)
                        .agg(penyerta=('penyerta', lambda x: ';\n'.join(x.tolist())), ids=('id', list))
                        .reset_index()
                    )
                    df_grouped.columns = ['Tanggal', 'Lokasi', 'Kegiatan', 'Penyerta', 'IDs']

                    # pending delete
                    if st.session_state.pending_delete_ids:
                        flat_ids = [i for sub in st.session_state.pending_delete_ids for i in sub]
                        if flat_ids:
                            with st.spinner("Menghapus..."):
                                resp_del = api_post("kegiatan/bulk-delete/", {"ids": flat_ids}, auth=True)
                                if resp_del.status_code == 200:
                                    st.session_state.notif = resp_del.json().get('message')
                                    st.session_state.pending_delete_ids = []
                                    st.rerun()
                                else: show_notif("Gagal menghapus", "error")

                    event = st.dataframe(
                        df_grouped[['Tanggal', 'Lokasi', 'Kegiatan', 'Penyerta']],
                        use_container_width=True, hide_index=True,
                        on_select="rerun", selection_mode="multi-row", key="kelola_data"
                    )
                    selected_rows = event.selection.rows if event.selection else []
                    if selected_rows:
                        selected_ids = [df_grouped.iloc[i]['IDs'] for i in selected_rows]
                        st.markdown(f"**{len(selected_ids)} grup terpilih**")
                        if st.button("Hapus Data Terpilih"): st.session_state.pending_delete_ids = selected_ids; st.rerun()

                    # Edit
                    st.markdown("---")
                    st.markdown('<h4><i class="fa-solid fa-pen-to-square"></i> Edit Data</h4>', unsafe_allow_html=True)
                    opsi_edit = ["—"] + [f"{r['Tanggal']} | {r['Lokasi']} | {r['Kegiatan']}" for _,r in df_grouped.iterrows()]
                    pilihan = st.selectbox("Pilih kegiatan", opsi_edit)
                    if pilihan != "—":
                        tgl_pilih, lok_pilih, keg_pilih = pilihan.split(" | ")
                        matched = df_grouped[(df_grouped['Tanggal']==tgl_pilih)&(df_grouped['Lokasi']==lok_pilih)&(df_grouped['Kegiatan']==keg_pilih)]
                        if not matched.empty:
                            edit_id = matched.iloc[0]['IDs'][0]
                            if st.button("Muat Data"):
                                resp_det = api_get(f"kegiatan/{edit_id}/", auth=True)
                                if resp_det.status_code == 200:
                                    st.session_state.edit_data = resp_det.json(); st.session_state.edit_id = edit_id; st.rerun()
                    if st.session_state.edit_data and st.session_state.edit_id:
                        with st.form("edit_form"):
                            tgl_ed = st.date_input("Tanggal", value=pd.to_datetime(st.session_state.edit_data['tanggal']))
                            lok_ed = st.text_input("Lokasi", value=st.session_state.edit_data['lokasi'])
                            keg_ed = st.text_input("Nama Kegiatan", value=st.session_state.edit_data['kegiatan'])
                            peny_ed = st.text_area("Penyerta", value=st.session_state.edit_data['penyerta'])
                            if st.form_submit_button("Update"):
                                resp_upd = api_put(f"kegiatan/{st.session_state.edit_id}/", {"tanggal":str(tgl_ed),"lokasi":lok_ed,"kegiatan":keg_ed,"penyerta":peny_ed})
                                if resp_upd.status_code == 200:
                                    st.session_state.notif = "Data diperbarui!"; st.session_state.edit_data = None; st.session_state.edit_id = None; st.rerun()
                                else: show_notif(resp_upd.text,"error")

                    # Hapus per bulan
                    st.markdown("---")
                    st.markdown('<h4><i class="fa-solid fa-calendar-xmark"></i> Hapus per Bulan/Tahun</h4>', unsafe_allow_html=True)
                    col_m, col_y, col_btn = st.columns([2,2,1])
                    with col_m: bulan = st.selectbox("Bulan", range(1,13), index=datetime.now().month-1)
                    with col_y: tahun = st.number_input("Tahun", value=datetime.now().year)
                    with col_btn:
                        if st.button("Hapus"):
                            resp_del = api_post("delete-by-date/", {"month": bulan, "year": tahun}, auth=True)
                            if resp_del.status_code == 200: st.session_state.notif = resp_del.json()['message']; st.rerun()
                            else: show_notif("Gagal","error")

                    # Download semua data - FIX 3 & 4
                    st.markdown("---")
                    st.markdown('<h5>⬇Download Data Kegiatan</h5>', unsafe_allow_html=True)
                    with st.container():
                        col_dl1, col_dl2 = st.columns(2)
                        with col_dl1:
                            generate_csv(data, "semua_kegiatan.csv")
                        with col_dl2:
                            pdf_buf = generate_jadwal_pdf(data)
                            st.download_button(
                                "⬇Download PDF",
                                data=pdf_buf,
                                file_name="semua_kegiatan.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                else: st.info("Belum ada data")
            else: show_notif("Gagal memuat data","error")
        except Exception as e: st.error(f"Error: {e}")

    # ── Tab 5: History ──
    with tab5:
        st.subheader("History Kegiatan")
        st.caption("Riwayat kegiatan yang sudah lewat dan akan datang")
        col_f1, col_f2, col_f3 = st.columns([2,2,1])
        with col_f1: filter_status = st.selectbox("Status", ["Semua","Sudah Lewat","Hari Ini","Akan Datang"])
        with col_f2: filter_bulan = st.selectbox("Bulan", ["Semua"]+list(calendar.month_name)[1:])
        with col_f3:
            if st.button("Refresh"): st.rerun()
        try:
            resp = api_get("kegiatan/", auth=True)
            if resp.status_code == 200:
                all_data = resp.json()
                if all_data:
                    today = date.today()
                    df = pd.DataFrame(all_data)
                    df['tanggal_date'] = pd.to_datetime(df['tanggal']).dt.date
                    df = df.sort_values('tanggal_date', ascending=False)
                    if filter_status == "Sudah Lewat": df = df[df['tanggal_date'] < today]
                    elif filter_status == "Hari Ini": df = df[df['tanggal_date'] == today]
                    elif filter_status == "Akan Datang": df = df[df['tanggal_date'] > today]
                    if filter_bulan != "Semua":
                        bulan_num = list(calendar.month_name).index(filter_bulan)
                        df = df[pd.to_datetime(df['tanggal']).dt.month == bulan_num]
                    filtered_data = df.to_dict('records')

                    if df.empty:
                        st.info("Tidak ada data sesuai filter")
                    else:
                        st.write(f"Total: {len(df)} kegiatan")
                        items = ""
                        for _, row in df.iterrows():
                            tgl_d = row['tanggal_date']
                            if tgl_d < today: sts = "Sudah Lewat"; badge = "status-past"
                            elif tgl_d == today: sts = "HARI INI"; badge = "status-today"
                            elif tgl_d == today + timedelta(days=1): sts = "Besok"; badge = "status-soon"
                            else: sts = "Akan Datang"; badge = "status-future"
                            tgl_fmt = pd.to_datetime(row['tanggal']).strftime('%A, %d %B %Y')
                            items += f"""
                            <div class="receipt-item">
                                <div class="receipt-item-title">{row['kegiatan']} <span class="receipt-status-badge {badge}">{sts}</span></div>
                                <div class="receipt-item-row"><span class="receipt-item-label">Tanggal</span><span class="receipt-item-value">{tgl_fmt}</span></div>
                                <div class="receipt-item-row"><span class="receipt-item-label">Lokasi</span><span class="receipt-item-value">{row['lokasi']}</span></div>
                                <div class="receipt-item-row"><span class="receipt-item-label">Penyerta</span><span class="receipt-item-value">{row['penyerta'][:120]}{'...' if len(row['penyerta'])>120 else ''}</span></div>
                            </div>"""
                        st.markdown(f"""
                        <div class="receipt-box">
                            <div class="receipt-header"><h3>History Kegiatan</h3><p>{filter_status} &mdash; {filter_bulan}</p></div>
                            <div class="receipt-body">{items}</div>
                            <div class="receipt-footer"><div class="receipt-barcode">|||||||||||||||||||||||</div>{len(df)} kegiatan &bull; Puskesmas Sangkali</div>
                        </div>
                        """, unsafe_allow_html=True)
                        # FIX 3 & 4: Download dengan fungsi yang sudah diperbaiki
                        with st.container():
                            col_csv, col_pdf = st.columns(2)
                            with col_csv:
                                generate_csv(filtered_data, "history_kegiatan.csv")
                            with col_pdf:
                                pdf_buf = generate_jadwal_pdf(filtered_data)
                                st.download_button(
                                    "⬇Download PDF",
                                    data=pdf_buf,
                                    file_name="history_kegiatan.pdf",
                                    mime="application/pdf",
                                    use_container_width=True
                                )
                else: st.info("Belum ada data kegiatan")
            else: show_notif("Gagal memuat data","error")
        except Exception as e: st.error(f"Error: {e}")

        # Hapus massal
        st.markdown("---")
        st.subheader("Hapus Massal")
        if st.button("Hapus Semua Kegiatan yang Sudah Lewat"):
            st.warning("Yakin ingin menghapus SEMUA kegiatan yang sudah lewat?")
            col_ya, col_tidak = st.columns(2)
            with col_ya:
                if st.button("Ya, Hapus"):
                    try:
                        resp = api_get("kegiatan/", auth=True)
                        if resp.status_code == 200:
                            all_data = resp.json()
                            today = date.today()
                            ids_to_delete = [item['id'] for item in all_data if datetime.strptime(item['tanggal'], '%Y-%m-%d').date() < today]
                            if ids_to_delete:
                                resp_del = api_post("kegiatan/bulk-delete/", {"ids": ids_to_delete}, auth=True)
                                if resp_del.status_code == 200: st.session_state.notif = f"{len(ids_to_delete)} kegiatan dihapus!"; st.rerun()
                                else: show_notif("Gagal menghapus","error")
                            else: st.info("Tidak ada kegiatan lewat.")
                    except Exception as e: st.error(f"Error: {e}")
            with col_tidak:
                if st.button("Batal"): st.rerun()

    # ── Tab 6: Randomize ──
    with tab6:
        st.subheader("Randomize Jadwal Bulanan (Dalam Gedung)")
        st.caption("Generate jadwal otomatis untuk hari kerja Senin-Sabtu")
        st.warning("Pastikan data PIKET PERSALINAN sudah diinput via SPS terlebih dahulu. Jika ada PIKET PERSALINAN MALAM pada suatu hari, maka esok harinya tidak akan digenerate jadwal dalam gedung.")
        
        NAMA_DIECUALIKAN = ["Isep Deni Herdian, S.Kep.,MMRS", "Isep Suhendar,SKM"]
        
        col_bulan, col_tahun, col_gen = st.columns([2, 2, 1])
        with col_bulan:
            bulan_pilih = st.selectbox("Bulan", range(1, 13), index=datetime.now().month-1,
                                       format_func=lambda x: calendar.month_name[x])
        with col_tahun:
            tahun_pilih = st.number_input("Tahun", value=datetime.now().year, min_value=2020, max_value=2030)
        with col_gen:
            st.write("")
            minggu_pilih = st.selectbox("Minggu ke-", [1, 2, 3, 4, 5], index=0)
            if st.button("Generate Jadwal", use_container_width=True, type="primary"):
                with st.spinner(f"Menggenerate jadwal untuk minggu ke-{minggu_pilih}..."):
                    import calendar as cal_mod
                    import random as rnd_mod
                    from datetime import timedelta as td_mod

                    def filter_nama(nama_list):
                        return [n for n in nama_list if n not in NAMA_DIECUALIKAN]
                    
                    def get_by_role(keywords):
                        semua = [n for n in DAFTAR_NAMA if any(kw.lower() in n.lower() for kw in keywords)]
                        return filter_nama(semua)
                    
                    def cek_piket_malam(tanggal):
                        try:
                            resp = api_get("kegiatan/", auth=True)
                            if resp.status_code == 200:
                                data = resp.json()
                                for item in data:
                                    if item['tanggal'] == tanggal and item['kegiatan'] == 'PIKET PERSALINAN MALAM':
                                        return True
                        except: pass
                        return False
                    
                    semua_dokter = get_by_role(['dr.', 'drg.'])
                    semua_perawat = get_by_role(['Ners', 'S.Kep', 'Amd.Kep', 'A.Md.Kep'])
                    semua_bidan = get_by_role(['Bdn.', 'S.Tr.Keb', 'Am.Keb', 'A.Md.Keb'])
                    semua_promkes = get_by_role(['Promosi', 'SKM'])
                    semua_sanitarian = get_by_role(['Sanitarian', 'S.K.M', 'A.Md.KL'])
                    semua_gizi = get_by_role(['S.Gz', 'A.Md.Gz'])
                    
                    pool_ilp = list(set(semua_perawat + semua_bidan + semua_promkes + semua_sanitarian + semua_gizi))
                    
                    tetap_pendaftaran = filter_nama(PENDAFTARAN_TETAP)
                    tetap_bpgigi = filter_nama(BP_GIGI_TETAP)
                    tetap_apotek = filter_nama(APOTEK_TETAP)
                    tetap_lab = filter_nama(LAB_TETAP)
                    tetap_ciangir = PUSTU_CIANGIR
                    tetap_sumelap = PUSTU_SUMELAP
                    tetap_admin = filter_nama(ADMINISTRASI_TETAP)
                    extra_admin = filter_nama(ADMINISTRASI_EXTRA)
                    
                    used_this_week = set()
                    usage_count = {nama: 0 for nama in pool_ilp + semua_dokter + semua_perawat + semua_bidan}
                    
                    def random_pick_with_fairness(lst, count=1, exclude=None):
                        exclude = exclude or set()
                        available = [x for x in lst if x not in exclude and x not in used_this_week]
                        if not available: available = [x for x in lst if x not in exclude]
                        if not available or len(available) < count: return []
                        available.sort(key=lambda x: usage_count.get(x, 0))
                        return rnd_mod.sample(available[:min(count*3, len(available))], min(count, len(available)))
                    
                    cal_m = cal_mod.monthcalendar(tahun_pilih, bulan_pilih)
                    minggu_index = minggu_pilih - 1
                    if minggu_index >= len(cal_m):
                        st.error(f"Bulan ini hanya memiliki {len(cal_m)} minggu"); st.stop()
                    
                    week = cal_m[minggu_index]
                    work_days = [d for idx, d in enumerate(week) if d != 0 and idx < 6]
                    if not work_days:
                        st.warning(f"Minggu ke-{minggu_pilih} tidak memiliki hari kerja"); st.stop()
                    
                    hari_names = ["Senin","Selasa","Rabu","Kamis","Jumat","Sabtu"]
                    jadwal_baru = []; skipped_days = []
                    
                    for tgl in work_days:
                        tgl_str = f"{tahun_pilih}-{bulan_pilih:02d}-{tgl:02d}"
                        tgl_obj = datetime(tahun_pilih, bulan_pilih, tgl)
                        nama_hari = hari_names[tgl_obj.weekday()]
                        tgl_sebelum = (tgl_obj - td_mod(days=1)).strftime('%Y-%m-%d')
                        if cek_piket_malam(tgl_sebelum): skipped_days.append(tgl_str); continue
                        used_today = set()
                        if tetap_pendaftaran:
                            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'PENDAFTARAN', 'penyerta': '; '.join(tetap_pendaftaran)})
                            used_today.update(tetap_pendaftaran)
                        for i in range(1, 3):
                            p = random_pick_with_fairness(pool_ilp, 1, used_today)
                            if p: used_today.add(p[0]); used_this_week.add(p[0]); usage_count[p[0]] = usage_count.get(p[0],0)+1; jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': f'SKRINING ILP {i}', 'penyerta': p[0]})
                        p = random_pick_with_fairness(pool_ilp, 3, used_today)
                        if len(p) >= 3:
                            used_today.update(p); used_this_week.update(p)
                            for n in p: usage_count[n] = usage_count.get(n,0)+1
                            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'POLI PROLANIS', 'penyerta': '; '.join(p)})
                        for i in range(1, 3):
                            dok = random_pick_with_fairness(semua_dokter, 1, used_today)
                            if dok: used_today.add(dok[0]); used_this_week.add(dok[0]); usage_count[dok[0]] = usage_count.get(dok[0],0)+1; jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': f'KLASTER DEWASA-LANSIA {i}', 'penyerta': dok[0]})
                            else:
                                per = random_pick_with_fairness(semua_perawat, 1, used_today)
                                if per: used_today.add(per[0]); used_this_week.add(per[0]); usage_count[per[0]] = usage_count.get(per[0],0)+1; jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': f'KLASTER DEWASA-LANSIA {i}', 'penyerta': per[0]})
                        for label in ['KLASTER IBU KIA & USG', 'KLASTER ANAK']:
                            b = random_pick_with_fairness(semua_bidan, 2, used_today)
                            d = random_pick_with_fairness(semua_dokter, 1, used_today)
                            used_today.update(b); used_this_week.update(b)
                            for n in b: usage_count[n] = usage_count.get(n,0)+1
                            if d: used_today.add(d[0]); used_this_week.add(d[0]); usage_count[d[0]] = usage_count.get(d[0],0)+1
                            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': label, 'penyerta': f"{'; '.join(b)}; {d[0] if d else 'Tidak ada'}"})
                        if nama_hari == "Kamis":
                            b = random_pick_with_fairness(semua_bidan, 2, used_today)
                            used_today.update(b); used_this_week.update(b)
                            for n in b: usage_count[n] = usage_count.get(n,0)+1
                            jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'R. IMUNISASI', 'penyerta': '; '.join(b) if b else 'Tidak ada'})
                        p = random_pick_with_fairness(semua_perawat, 1, used_today)
                        if p: used_today.add(p[0]); used_this_week.add(p[0]); usage_count[p[0]] = usage_count.get(p[0],0)+1; jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'R. TINDAKAN', 'penyerta': p[0]})
                        if tetap_bpgigi: jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'BP GIGI', 'penyerta': '; '.join(tetap_bpgigi)}); used_today.update(tetap_bpgigi)
                        if tetap_apotek: jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'APOTEK', 'penyerta': '; '.join(tetap_apotek)}); used_today.update(tetap_apotek)
                        if tetap_lab: jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'LAB', 'penyerta': '; '.join(tetap_lab)}); used_today.update(tetap_lab)
                        if nama_hari == "Selasa":
                            petugas_tb = "Mutia Wulansari.,S.Kep.,Ners"
                            if petugas_tb not in NAMA_DIECUALIKAN: jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'R. TB', 'penyerta': petugas_tb}); used_today.add(petugas_tb); used_this_week.add(petugas_tb); usage_count[petugas_tb] = usage_count.get(petugas_tb,0)+1
                        extra = random_pick_with_fairness(extra_admin, 2)
                        semua_admin = tetap_admin + extra
                        if semua_admin: jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Dalam Gedung', 'kegiatan': 'ADMINISTRASI', 'penyerta': '; '.join(semua_admin)}); used_today.update(semua_admin); used_this_week.update(semua_admin)
                        for n in semua_admin: usage_count[n] = usage_count.get(n,0)+1
                        jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Pustu Ciangir', 'kegiatan': 'PELAYANAN PUSTU', 'penyerta': tetap_ciangir})
                        jadwal_baru.append({'tanggal': tgl_str, 'lokasi': 'Pustu Sumelap', 'kegiatan': 'PELAYANAN PUSTU', 'penyerta': tetap_sumelap})
                        used_today.add(tetap_ciangir); used_today.add(tetap_sumelap)
                    
                    if skipped_days: st.info(f"Hari berikut ini TIDAK digenerate karena H-1 ada PIKET PERSALINAN MALAM: {', '.join(skipped_days)}")
                    saved = 0; progress_text = st.empty(); progress_bar = st.progress(0)
                    existing_all = []
                    try:
                        r_existing = api_get("kegiatan/", auth=True)
                        if r_existing.status_code == 200: existing_all = r_existing.json()
                    except: pass
                    existing_set = {(e['tanggal'], e['kegiatan']) for e in existing_all}
                    for i, j in enumerate(jadwal_baru):
                        progress_text.text(f"Menyimpan {i+1} dari {len(jadwal_baru)}: {j['kegiatan']}")
                        progress_bar.progress((i+1)/len(jadwal_baru))
                        if (j['tanggal'], j['kegiatan']) not in existing_set:
                            try:
                                r = api_post("kegiatan/", j, auth=True)
                                if r.status_code == 201: saved += 1; existing_set.add((j['tanggal'], j['kegiatan']))
                            except: pass
                    progress_text.empty(); progress_bar.empty()
                    if saved > 0: st.session_state.notif = f"Berhasil generate {saved} jadwal untuk minggu ke-{minggu_pilih}!"; st.balloons(); st.rerun()
                    else: st.error("Gagal menyimpan jadwal. Cek koneksi ke server Django.")
        
        st.markdown("---")
        st.subheader("Hasil Generate Jadwal")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            bulan_filter = st.selectbox("Filter Bulan", range(1, 13), index=datetime.now().month-1,
                                       format_func=lambda x: calendar.month_name[x], key="filter_bulan")
        with col_f2:
            tahun_filter = st.number_input("Filter Tahun", value=datetime.now().year, key="filter_tahun")
        try:
            resp = api_get("kegiatan/", auth=True)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    df = pd.DataFrame(data)
                    df['tanggal'] = pd.to_datetime(df['tanggal'])
                    df_filter = df[(df['tanggal'].dt.month == bulan_filter) & (df['tanggal'].dt.year == tahun_filter)]
                    df_filter = df_filter.sort_values('tanggal')
                    if not df_filter.empty:
                        st.dataframe(df_filter[['tanggal', 'lokasi', 'kegiatan', 'penyerta']], use_container_width=True, hide_index=True)
                    else: st.info(f"Belum ada jadwal untuk {bulan_filter}/{tahun_filter}")
                else: st.info("Belum ada data")
        except: st.warning("Gagal mengambil data")

# ---------- FOOTER ----------
st.markdown("""
<div class="puskesmas-footer">
    <div class="footer-grid">
        <div class="footer-section">
            <h4>Puskesmas Sangkali</h4>
            <p><i class="fa-solid fa-location-dot"></i> Jl. Sangkali No. 1, Tamansari<br>Tasikmalaya, Jawa Barat</p>
            <p><i class="fa-solid fa-phone"></i> (0265) 123456</p>
            <p><i class="fa-solid fa-envelope"></i> puskesmas@sangkali.id</p>
        </div>
        <div class="footer-section">
            <h4>Jam Operasional</h4>
            <p><i class="fa-solid fa-clock"></i> Senin–Kamis: 07:30–14:00</p>
            <p><i class="fa-solid fa-clock"></i> Jumat: 07:30–11:30</p>
            <p><i class="fa-solid fa-clock"></i> Sabtu: 07:30–12:00</p>
        </div>
        <div class="footer-section">
        </div>
    </div>
    <hr class="footer-divider">
    <div class="footer-bottom">&copy; 2026 UPTD Puskesmas Sangkali</div>
</div>
""", unsafe_allow_html=True)