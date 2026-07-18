import streamlit as st
import pandas as pd
import requests
import re
import calendar
from datetime import datetime, date, timedelta
from collections import defaultdict
from io import BytesIO, StringIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

st.set_page_config(page_title="Puskesmas Sangkali", page_icon="assets/logo.png", layout="wide")

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
[data-testid="stSidebar"] .stButton > button:hover { background: rgba(255,255,255,0.28); }
[data-testid="stSidebar"] [data-testid="stImage"] {
    display: flex !important;
    justify-content: center !important;
}
[data-testid="stSidebar"] [data-testid="stImage"] img { margin: 0 auto !important; }
.sidebar-puskesmas-name { font-size:0.95rem; font-weight:700; text-align:center; margin:0.4rem 0 0.25rem; width:100%; }
.sidebar-puskesmas-sub { font-size:0.75rem; text-align:center; opacity:0.75; margin-bottom:0.5rem; width:100%; }
.sidebar-menu-label { font-size:0.7rem; text-transform:uppercase; letter-spacing:0.1em; font-weight:600; padding:0.5rem 0 0.2rem; opacity:0.55; text-align:center !important; }
.sidebar-user-badge { font-size:0.82rem; text-align:center; margin:4px 0 8px; display:block; padding:4px 0; }
.badge-online { display:inline-flex; align-items:center; gap:5px; background:rgba(187,247,208,0.2); color:#bbf7d0; font-size:0.78rem; font-weight:600; padding:3px 10px; border-radius:999px; border:1px solid rgba(187,247,208,0.3); }
.badge-offline { display:inline-flex; align-items:center; gap:5px; background:rgba(254,202,202,0.2); color:#fecaca; font-size:0.78rem; font-weight:600; padding:3px 10px; border-radius:999px; border:1px solid rgba(254,202,202,0.3); }
.main-header { background:linear-gradient(135deg,rgba(20,83,45,0.85) 0%,rgba(22,101,52,0.85) 100%); padding:4rem 2rem; border-radius:20px; color:white; text-align:center; margin-bottom:2rem; }
.main-header h1 { font-size:2.5rem; font-weight:700; margin:0; text-shadow:2px 2px 4px rgba(0,0,0,0.3); }
.main-header p { font-size:1.2rem; margin-top:0.5rem; text-shadow:1px 1px 3px rgba(0,0,0,0.3); }
.receipt-box { background:#fffef8; border:1px solid #e2e0d8; border-radius:4px; padding:0; margin:1rem 0; box-shadow:0 1px 3px rgba(0,0,0,0.08),0 4px 12px rgba(0,0,0,0.06); font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; position:relative; }
.receipt-box::before { content:""; display:block; height:6px; background:radial-gradient(circle at 6px 6px,transparent 6px,#fffef8 6px) -6px 0,linear-gradient(#fffef8,#fffef8); background-size:12px 6px,100% 100%; margin-bottom:2px; }
.receipt-box::after { content:""; display:block; height:6px; background:radial-gradient(circle at 6px 0px,transparent 6px,#fffef8 6px) -6px 0; background-size:12px 6px; margin-top:2px; }
.receipt-header { background:#14532d; color:white; text-align:center; padding:1rem 1.25rem 0.85rem; }
.receipt-header h3 { margin:0; font-size:1rem; font-weight:700; text-transform:uppercase; }
.receipt-body { padding:0.5rem 1.25rem; }
.receipt-item { padding:0.75rem 0; border-bottom:1px dashed #ddd8cc; }
.receipt-item:last-child { border-bottom:none; }
.receipt-item-title { font-weight:700; color:#14532d; font-size:0.92rem; }
.receipt-item-row { display:flex; justify-content:flex-start; align-items:baseline; font-size:0.82rem; color:#4b5563; margin-bottom:0.2rem; }
.receipt-item-label { color:#6b7280; min-width:80px; margin-right:6px; }
.receipt-item-value { color:#1f2937; text-align:left; word-break:break-word; }
.receipt-penyerta-list { margin-top:0.2rem; padding-left:0; }
.receipt-penyerta-list span { display:block; margin-bottom:0.15rem; }
.receipt-status-badge { font-size:0.72rem; font-weight:700; padding:2px 9px; border-radius:3px; text-transform:uppercase; }
.status-past { background:#f3f4f6; color:#6b7280; border:1px solid #d1d5db; }
.status-today { background:#dcfce7; color:#15803d; border:1px solid #86efac; }
.status-soon { background:#dbeafe; color:#1d4ed8; border:1px solid #93c5fd; }
.status-future { background:#fef9c3; color:#854d0e; border:1px solid #fde047; }
.receipt-footer { text-align:center; padding:0.75rem 1.25rem 0.9rem; color:#9ca3af; font-size:0.75rem; border-top:2px dashed #c8c5b8; }
.receipt-barcode { font-size:1.6rem; letter-spacing:0.05em; color:#374151; margin:0.3rem 0; }
.data-card { background:white; padding:1.25rem; border-radius:14px; border:1px solid #e5e7eb; margin-bottom:1rem; box-shadow:0 2px 8px rgba(0,0,0,0.04); }
.stat-card { background:linear-gradient(135deg,#f0fdf4,#dcfce7); border:1px solid #bbf7d0; padding:1.1rem 1.25rem; border-radius:14px; text-align:center; }
.stat-card-num { font-size:1.8rem; font-weight:700; color:#15803d; }
.stTabs [data-baseweb="tab-list"] { gap:6px; background:#f0fdf4; border-radius:12px; padding:5px; }
.stTabs [data-baseweb="tab"] { border-radius:8px; padding:8px 16px; font-weight:500; font-size:0.88rem; color:#166534; }
.stTabs [aria-selected="true"] { background-color:#14532d !important; color:white !important; }
.puskesmas-footer { background:rgba(20,83,45,0.06); padding:2.5rem 2rem 1.5rem; border-radius:20px 20px 0 0; margin-top:2rem; }
.footer-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:2rem; margin-bottom:1.75rem; }
.footer-section h4 { font-size:0.95rem; font-weight:700; color:#14532d; border-bottom:1px solid rgba(20,83,45,0.1); padding-bottom:0.4rem; margin-bottom:0.75rem; }
.footer-section p,.footer-section a { font-size:0.85rem; color:#374151; line-height:1.9; text-decoration:none; }
.footer-section a:hover { color:#14532d; }
.footer-section i { width:18px; margin-right:6px; color:#166534; }
.footer-divider { border-top:1px solid rgba(0,0,0,0.05); margin:1rem 0; }
.footer-bottom { text-align:center; font-size:0.8rem; color:#6b7280; }
@media (max-width:768px) { .main-header h1 { font-size:1.6rem; } .footer-grid { grid-template-columns:1fr; } }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
for key, default in [
    ('logged_in', False), ('token', None), ('username', ''),
    ('page', 'user'), ('edit_data', None), ('edit_id', None),
    ('last_csv_url', ''), ('notif', None), ('pending_delete_ids', []),
    ('user_history_status', {}), ('show_csv_input', False),
    ('confirm_hapus_massal', False),
]:
    if key not in st.session_state:
        st.session_state[key] = default

API_BASE = "https://web-production-dc35a.up.railway.app/api"

DAFTAR_NAMA = [
    "Isep Deni Herdian, S.Kep.,MMRS","Isep Suhendar,SKM",
    "Bdn. Yeni Yulyani Setianingsih, S.ST","Bdn. Nina Ainun, S.Tr.Keb",
    "Rita Sahara, S.Tr.Keb","Dewi Sri Mulyani, Am.Keb",
    "Pipit Puspitasari, Am.Keb","Mira Jatnikawati, Am.Keb",
    "Reni Mustikasari, Am.Keb","Alitsa Nuur Fithri, S.ST",
    "Yesi Apriyani, Am.Keb","Asri Awulan, S.Tr.Keb",
    "Pia Nur Podiana, A.Md.Keb","Intang Sri Purnama, AM.Keb",
    "Ucu Lestari, AM.Keb","Annisa Nafaulloh,S.Tr.Keb.,Bdn",
    "Mutia Wulansari.,S.Kep.,Ners","Ujang Effendi, S.Kep.,Ners",
    "Liska Permatasari, S.Kep.,Ners","Dede Khaerul Kamal Muchtar, AMK",
    "Iman Nurul Haq, A.Md.Kep","Wida Idul Adha, S.Kep.,Ners",
    "Oriany Kemala Dewi, Amd.Kep","Haeriah, A.Md.Kep",
    "Dede Aan Septiantini, A.Md.Kep","dr.Ferry Nalapraya",
    "dr.Muhammad Azhary Romdhon","dr.Iwan Setiawan",
    "dr. Siti Hana Fukui","dr. Volti Diana Suryawadi",
    "drg.Rifan Hanggoro.M.M.R.S","Endah Setiawati,S.Tr.Kes",
    "Khilman Husna Pratama, S.Farm.,Apt","Vita Tyana Virista, A.Md.AK",
    "Gina Giovany, A.Md.AK","Eko Wahyu Saputro, S.K.M",
    "Nurul Hasanah, A.Md.KL","Nova Silpiany Perdany, A.Md.Farm",
    "Ameilia Putri Isyari, S.Gz","Annisa Fauziah, A.Md.Gz",
    "Rudi Sutikno, SKM","Yogi Aris Diyanto, S.E",
    "Rangga Ismardana Gasbela,S.T","Winda Siti Sarah, AMd.RMIK",
    "Pupung Juliana","Salsa Sabila","Andina Dea Priatna, SKM","Iip Supyan"
]

PENDAFTARAN_TETAP  = ["Winda Siti Sarah, AMd.RMIK","Pupung Juliana","Salsa Sabila"]
BP_GIGI_TETAP      = ["drg.Rifan Hanggoro.M.M.R.S","Endah Setiawati,S.Tr.Kes"]
APOTEK_TETAP       = ["Khilman Husna Pratama, S.Farm.,Apt","Nova Silpiany Perdany, A.Md.Farm"]
LAB_TETAP          = ["Vita Tyana Virista, A.Md.AK","Gina Giovany, A.Md.AK"]
PUSTU_CIANGIR      = "Haeriah, A.Md.Kep"
PUSTU_SUMELAP      = "Ujang Effendi, S.Kep.,Ners"
ADMINISTRASI_TETAP = ["Rangga Ismardana Gasbela,S.T","Yogi Aris Diyanto, S.E"]
ADMINISTRASI_EXTRA = ["Liska Permatasari, S.Kep.,Ners","Alitsa Nuur Fithri, S.ST","Andina Dea Priatna, SKM"]
NAMA_DIECUALIKAN   = ["Isep Deni Herdian, S.Kep.,MMRS","Isep Suhendar,SKM"]

ROLE_MAP = {
    'dokter':['dr.','drg.'],
    'perawat_ners':['Ners','S.Kep','Amd.Kep','A.Md.Kep'],
    'bidan':['Bdn.','S.Tr.Keb','Am.Keb','A.Md.Keb'],
    'promkes':['Promosi','SKM'],
    'sanitarian':['Sanitarian','S.K.M','A.Md.KL'],
    'gizi':['S.Gz','A.Md.Gz'],
    'apoteker':['Apt','S.Farm'],
    'lab':['A.Md.AK'],
    'gigi':['drg.','S.Tr.Kes'],
    'administrasi':['S.E','S.T','S.Kep','S.ST','SKM','AMd.RMIK'],
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
    icons = {"success":"✅","error":"❌","info":"ℹ️"}
    st.toast(message, icon=icons.get(notif_type,"ℹ️"))

# ==================== NORMALIZE DATE ====================
def normalize_date(date_str):
    """Konversi tanggal ke format YYYY-MM-DD yang valid untuk Django"""
    if not date_str:
        return None
    try:
        # Format DD-MM-YYYY (prioritas utama)
        parsed = datetime.strptime(date_str.strip(), '%d-%m-%Y')
        return parsed.strftime('%Y-%m-%d')
    except ValueError:
        try:
            # Fallback: coba dengan pandas
            parsed = pd.to_datetime(date_str, dayfirst=True, errors='coerce')
            if pd.notna(parsed):
                return parsed.strftime('%Y-%m-%d')
        except Exception:
            pass
    return None  # Kembalikan None jika gagal, biar tidak masuk ke database

# ── PARSE CSV GOOGLE SHEET ──
def parse_google_sheet_csv(raw_text):
    import csv as _csv
    lines = raw_text.strip().splitlines()
    if not lines:
        return []

    header_parts = [h.strip().lower() for h in lines[0].split(',')]
    col_map = {}
    for i, h in enumerate(header_parts):
        if 'tanggal' in h or h == 'date':
            col_map['tanggal'] = i
        elif 'lokasi' in h or h in ('location', 'tempat'):
            col_map['lokasi'] = i
        elif 'kegiatan' in h or 'activity' in h or 'nama kegiatan' in h:
            col_map['kegiatan'] = i
        elif 'penyerta' in h or 'pelaksana' in h or 'peserta' in h or 'petugas' in h:
            col_map['penyerta'] = i

    required = ['tanggal', 'lokasi', 'kegiatan', 'penyerta']
    missing = [k for k in required if k not in col_map]
    if missing:
        raise ValueError(f"Kolom tidak ditemukan: {missing}. Header terdeteksi: {header_parts}")

    peny_idx = col_map['penyerta']
    results = []

    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        try:
            row = list(_csv.reader([line]))[0]
        except Exception:
            row = []

        if len(row) >= 4:
            if len(row) > peny_idx + 1:
                penyerta_val = ', '.join(r.strip() for r in row[peny_idx:])
            else:
                penyerta_val = row[peny_idx].strip()
            tgl_val = row[col_map['tanggal']].strip()
            lok_val = row[col_map['lokasi']].strip()
            keg_val = row[col_map['kegiatan']].strip()
        else:
            parts = line.split(',', peny_idx)
            if len(parts) <= peny_idx:
                continue
            tgl_val = parts[col_map.get('tanggal', 0)].strip()
            lok_val = parts[col_map.get('lokasi', 1)].strip()
            keg_val = parts[col_map.get('kegiatan', 2)].strip()
            penyerta_val = parts[peny_idx].strip().strip('"')

        tgl_normal = normalize_date(tgl_val)
        if tgl_normal and keg_val:
            results.append({
                'tanggal':  tgl_normal,
                'lokasi':   lok_val,
                'kegiatan': keg_val,
                'penyerta': penyerta_val,
            })
        else:
            print(f"[WARNING] Data dilewati: tanggal={tgl_val}, kegiatan={keg_val}")

    return results

def sync_from_url(csv_url, mode, auth=True):
    try:
        resp = requests.get(csv_url, timeout=15)
        resp.raise_for_status()
        raw = resp.text
        print(f"[DEBUG] CSV berhasil diunduh, panjang: {len(raw)} karakter")
    except Exception as e:
        raise ValueError(f"Gagal mengunduh CSV: {e}")

    records = parse_google_sheet_csv(raw)
    if not records:
        raise ValueError("Tidak ada data valid di spreadsheet.")
    
    print(f"[DEBUG] Jumlah record dari CSV: {len(records)}")

    if mode == 'replace':
        try:
            r_all = api_get("kegiatan/", auth=True)
            if r_all.status_code == 200:
                ids_all = [item['id'] for item in r_all.json()]
                if ids_all:
                    api_post("kegiatan/bulk-delete/", {"ids": ids_all}, auth=True)
                    print(f"[DEBUG] Menghapus {len(ids_all)} data lama")
        except Exception as e:
            print(f"[WARNING] Gagal menghapus data lama: {e}")

    existing_set = set()
    if mode == 'append':
        try:
            r_ex = api_get("kegiatan/", auth=True)
            if r_ex.status_code == 200:
                for item in r_ex.json():
                    existing_set.add((item['tanggal'], item['lokasi'], item['kegiatan']))
                print(f"[DEBUG] Data existing: {len(existing_set)}")
        except Exception as e:
            print(f"[WARNING] Gagal mengambil data existing: {e}")

    saved = skipped = errors = 0
    for rec in records:
        key = (rec['tanggal'], rec['lokasi'], rec['kegiatan'])
        if mode == 'append' and key in existing_set:
            skipped += 1
            continue
        try:
            # ===== TAMBAHKAN FIELD YANG KURANG =====
            rec['kategori'] = 'luar_gedung'
            rec['sub_kategori'] = 'lainnya'
            rec['source'] = 'google_sheet'
            rec['is_auto_generated'] = False
            
            print(f"[DEBUG] Mengirim: {rec}")
            
            r = api_post("kegiatan/", rec, auth=True)
            if r.status_code == 201:
                saved += 1
                existing_set.add(key)
                print(f"[DEBUG] ✅ Berhasil: {rec['kegiatan']}")
            else:
                print(f"[ERROR] ❌ Status {r.status_code}: {r.text}")
                errors += 1
        except Exception as e:
            print(f"[EXCEPTION] ❌ {e}")
            errors += 1

    print(f"[SUMMARY] Saved: {saved}, Skipped: {skipped}, Errors: {errors}")
    return saved, skipped, errors

# ── PDF ──
def generate_jadwal_pdf(data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter),
                            leftMargin=0.4*inch, rightMargin=0.4*inch,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CT', parent=styles['Title'], fontSize=14, alignment=1,
                                 spaceAfter=6, textColor=colors.HexColor('#14532d'))
    sub_style   = ParagraphStyle('CS', parent=styles['Normal'], fontSize=10, alignment=1,
                                 spaceAfter=14, textColor=colors.HexColor('#166534'))
    cell_style  = ParagraphStyle('CE', parent=styles['Normal'], fontSize=7, leading=9, wordWrap='LTR')
    foot_style  = ParagraphStyle('CF', parent=styles['Normal'], fontSize=8,
                                 textColor=colors.grey, alignment=1)

    story = [
        Paragraph("JADWAL PELAYANAN PUSKESMAS SANGKALI", title_style),
        Paragraph(f"Dicetak: {datetime.now().strftime('%d %B %Y, %H:%M')}", sub_style),
        Spacer(1, 6)
    ]

    if not data:
        story.append(Paragraph("Tidak ada data jadwal.", styles['Normal']))
        doc.build(story); buffer.seek(0); return buffer

    df = pd.DataFrame(data)
    for col in ['tanggal','lokasi','kegiatan','penyerta']:
        if col not in df.columns: df[col] = ''
    df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
    df = df.sort_values('tanggal')
    df['tanggal_str'] = df['tanggal'].dt.strftime('%A,\n%d %b %Y')

    col_widths = [1.5*inch, 1.4*inch, 2.0*inch, 5.6*inch]
    headers    = ['TANGGAL','LOKASI','KEGIATAN','PELAKSANA / PENYERTA']
    table_data = [[Paragraph(f'<b>{h}</b>', cell_style) for h in headers]]
    for _, row in df.iterrows():
        tgl_disp = row['tanggal_str'] if pd.notna(row['tanggal']) else str(row.get('tanggal',''))
        peny_raw = str(row.get('penyerta','')).replace(';','\n').strip()
        table_data.append([
            Paragraph(tgl_disp, cell_style),
            Paragraph(str(row.get('lokasi','')), cell_style),
            Paragraph(str(row.get('kegiatan','')), cell_style),
            Paragraph(peny_raw, cell_style),
        ])

    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#14532d')),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
        ('FONTSIZE',(0,0),(-1,0),8),
        ('BOTTOMPADDING',(0,0),(-1,0),8),
        ('TOPPADDING',(0,0),(-1,0),8),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white, colors.HexColor('#f0fdf4')]),
        ('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#d1d5db')),
        ('TOPPADDING',(0,1),(-1,-1),5),
        ('BOTTOMPADDING',(0,1),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),6),
        ('RIGHTPADDING',(0,0),(-1,-1),6),
    ]))
    story.append(t)
    story.append(Spacer(1,20))
    story.append(Paragraph(
        f"Dicetak dari Sistem Puskesmas Sangkali © {datetime.now().year} | Total: {len(df)} kegiatan",
        foot_style
    ))
    doc.build(story)
    buffer.seek(0)
    return buffer

# ── CSV ──
def generate_csv(data, filename="jadwal.csv"):
    if not data:
        st.download_button("Download CSV", data=b"TANGGAL,LOKASI,KEGIATAN,PELAKSANA\n",
                           file_name=filename, mime='text/csv', use_container_width=True)
        return
    df = pd.DataFrame(data)
    rename_map = {'tanggal':'TANGGAL','lokasi':'LOKASI','kegiatan':'KEGIATAN','penyerta':'PELAKSANA'}
    df = df.rename(columns={k:v for k,v in rename_map.items() if k in df.columns})
    kolom = [c for c in ['TANGGAL','LOKASI','KEGIATAN','PELAKSANA'] if c in df.columns]
    df = df[kolom]
    if 'TANGGAL' in df.columns:
        df['TANGGAL'] = pd.to_datetime(df['TANGGAL'], errors='coerce').dt.strftime('%Y-%m-%d')
    buf = StringIO()
    df.to_csv(buf, index=False, sep=',', quoting=1)
    csv_bytes = buf.getvalue().encode('utf-8-sig')
    st.download_button("⬇ Download CSV", data=csv_bytes, file_name=filename,
                       mime='text/csv', use_container_width=True)

# ── TOKEN URL ──
params = st.query_params
if not st.session_state.logged_in and 'token' in params:
    token = params['token']
    try:
        resp = requests.get(f"{API_BASE}/verify-token/", headers={"Authorization":f"Token {token}"}, timeout=5)
        if resp.status_code == 200:
            d = resp.json()
            st.session_state.logged_in = True
            st.session_state.token = token
            st.session_state.username = d.get('username','Admin')
            st.query_params.clear(); st.rerun()
        else: st.query_params.clear()
    except: pass

if st.session_state.notif:
    show_notif(st.session_state.notif)
    st.session_state.notif = None

# ── SIDEBAR ──
with st.sidebar:
    cl, cc, cr = st.columns([0.5,3,0.5])
    with cc:
        try: st.image("assets/logo.png", width=90)
        except:
            st.markdown("""<div style="display:flex;justify-content:center;">
            <svg width="80" height="80" viewBox="0 0 80 80">
            <circle cx="40" cy="40" r="38" fill="rgba(255,255,255,0.15)" stroke="rgba(255,255,255,0.3)" stroke-width="2"/>
            <rect x="35" y="20" width="10" height="40" rx="3" fill="white"/>
            <rect x="20" y="35" width="40" height="10" rx="3" fill="white"/>
            </svg></div>""", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-puskesmas-name">UPTD Puskesmas<br>Sangkali</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-puskesmas-sub">Tasikmalaya, Jawa Barat</div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-menu-label">Navigasi</div>', unsafe_allow_html=True)
    if st.button("Jadwal Kegiatan", use_container_width=True):
        st.session_state.page="user"; st.rerun()
    if not st.session_state.logged_in:
        if st.button("Login Admin", use_container_width=True):
            st.session_state.page="admin_login"; st.rerun()
    else:
        st.markdown(f'<div class="sidebar-user-badge"><i class="fa-solid fa-circle-user"></i> {st.session_state.username}</div>', unsafe_allow_html=True)
        if st.button("Dashboard Admin", use_container_width=True):
            st.session_state.page="admin_dashboard"; st.rerun()
        if st.button("Logout", use_container_width=True):
            try: api_post("logout/",{},auth=True)
            except: pass
            for k in ['logged_in','token','username']:
                st.session_state[k] = False if k=='logged_in' else None if k=='token' else ''
            st.session_state.page="user"; st.query_params.clear(); st.rerun()
    st.markdown("<hr>", unsafe_allow_html=True)
    try:
        r = requests.get(f"{API_BASE}/jadwal-terdekat/", timeout=3)
        if r.status_code==200: st.markdown('<span class="badge-online"><i class="fa-solid fa-circle-dot"></i> Online</span>', unsafe_allow_html=True)
        else: st.markdown('<span class="badge-offline"><i class="fa-solid fa-circle-exclamation"></i> Error</span>', unsafe_allow_html=True)
    except: st.markdown('<span class="badge-offline"><i class="fa-solid fa-circle-exclamation"></i> Offline</span>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.7rem;opacity:0.6;text-align:center;"><i class="fa-solid fa-clock"></i> Senin–Jumat 07:30–14:00</div>', unsafe_allow_html=True)

# ── HEADER ──
if st.session_state.page=="user":
    st.markdown('<div class="main-header"><h1>Puskesmas Sangkali</h1><p>Sistem Informasi Manajemen Kegiatan</p></div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="main-header"><h1>Puskesmas Sangkali</h1><p>Dashboard Manajemen</p></div>', unsafe_allow_html=True)

# ════════════════════════════════════════
# USER PAGE
# ════════════════════════════════════════
if st.session_state.page=="user":
    try:
        today=date.today(); tomorrow=today+timedelta(days=1)
        resp_notif=requests.get(f"{API_BASE}/jadwal-terdekat/", timeout=3)
        if resp_notif.status_code==200:
            jadwal=resp_notif.json()
            notif_hari_ini=[j for j in jadwal if j['tanggal']==str(today)]
            notif_besok=[j for j in jadwal if j['tanggal']==str(tomorrow)]
            if notif_hari_ini:
                items=''.join(f"<li><b>{j['kegiatan']}</b> — {j['lokasi']}</li>" for j in notif_hari_ini[:6])
                st.markdown(f"<div style='background:#dcfce7;border:1px solid #bbf7d0;padding:1rem;border-radius:12px;margin-bottom:0.75rem;'><i class='fa-solid fa-circle-exclamation'></i> <b>Hari ini:</b><ul>{items}</ul></div>", unsafe_allow_html=True)
            if notif_besok:
                items=''.join(f"<li><b>{j['kegiatan']}</b> — {j['lokasi']}</li>" for j in notif_besok[:6])
                st.markdown(f"<div style='background:#eff6ff;border:1px solid #bfdbfe;padding:1rem;border-radius:12px;margin-bottom:0.75rem;'><i class='fa-solid fa-calendar-check'></i> <b>Besok:</b><ul>{items}</ul></div>", unsafe_allow_html=True)
    except: pass

    col1,col2=st.columns([2,1])
    with col1:
        st.markdown('<div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem"><i class="fa-solid fa-magnifying-glass" style="color:#14532d;"></i><span style="font-size:1.3rem;font-weight:700;color:#14532d;">Cari Jadwal Kegiatan</span></div>', unsafe_allow_html=True)
        with st.form("user_form"):
            nama=st.selectbox("Nama Lengkap", DAFTAR_NAMA)
            tanggal=st.date_input("Tanggal", datetime.now().date())
            if st.form_submit_button("Cari"):
                resp=api_get("search-user/", params={"nama":nama,"tanggal":str(tanggal)})
                if resp.status_code==200 and resp.json():
                    hasil=resp.json()
                    tgl_fmt=tanggal.strftime('%A, %d %B %Y')
                    items=""
                    for h in hasil:
                        peny_list = parse_penyerta(h['penyerta'])
                        peny_items = ''.join(f'<span>{p}</span>' for p in peny_list) if peny_list else f'<span>{h["penyerta"]}</span>'
                        items+=f"""<div class="receipt-item">
                            <div class="receipt-item-title">{h['kegiatan']}</div>
                            <div class="receipt-item-row"><span class="receipt-item-label">Lokasi</span><span class="receipt-item-value">{h['lokasi']}</span></div>
                            <div class="receipt-item-row"><span class="receipt-item-label">Penyerta</span><div class="receipt-item-value"><div class="receipt-penyerta-list">{peny_items}</div></div></div>
                        </div>"""
                    st.markdown(f"<div class='receipt-box'><div class='receipt-header'><h3>Jadwal Kegiatan</h3><p>{tgl_fmt}</p></div><div class='receipt-body'>{items}</div><div class='receipt-footer'><div class='receipt-barcode'>|||||||||||||||||||||||</div>Puskesmas Sangkali</div></div>", unsafe_allow_html=True)
                else: st.warning("Tidak ada kegiatan.")
    with col2:
        st.markdown('<div class="data-card"><div style="display:flex;align-items:center;gap:6px;margin-bottom:0.5rem"><i class="fa-solid fa-circle-info" style="color:#14532d;"></i><span style="font-weight:700;color:#14532d;">Informasi</span></div><ul style="font-size:0.88rem;line-height:1.8;"><li>Datang 15 menit lebih awal</li><li>Bawa KMS/BPJS</li><li>Gunakan masker</li></ul></div>', unsafe_allow_html=True)

    # ── Riwayat Kehadiran ──
    st.markdown("---")
    st.markdown('<div style="display:flex;align-items:center;gap:8px;margin-bottom:0.5rem"><i class="fa-solid fa-clock-rotate-left" style="color:#14532d;"></i><span style="font-size:1.2rem;font-weight:700;color:#14532d;">Riwayat Kehadiran Saya</span></div>', unsafe_allow_html=True)
    cf1, cf2, cf3 = st.columns([2, 2, 1])
    with cf1:
        nama_riwayat = st.selectbox("Nama", DAFTAR_NAMA, key="nama_riwayat")
    with cf2:
        bulan_riwayat = st.selectbox("Bulan", ["Semua"] + list(calendar.month_name)[1:], key="bulan_riwayat")
    with cf3:
        tahun_riwayat = st.number_input("Tahun", value=datetime.now().year, min_value=2020, max_value=2030)

    if st.button("Tampilkan Riwayat"):
        try:
            resp = api_get("search-user/", params={"nama": nama_riwayat})
            raw_data = None
            if resp.status_code == 200:
                raw_data = resp.json()
            else:
                for use_auth in ([True, False] if st.session_state.logged_in else [False]):
                    try:
                        r2 = api_get("kegiatan/", auth=use_auth)
                        if r2.status_code == 200:
                            all_d = r2.json()
                            kw = nama_riwayat.split(",")[0].strip()
                            raw_data = [d for d in all_d if kw.lower() in d.get("penyerta", "").lower()]
                            break
                    except:
                        continue

            if not raw_data:
                st.info("Belum ada data kegiatan di sistem.")
            else:
                df = pd.DataFrame(raw_data)
                df["tanggal_dt"] = pd.to_datetime(df["tanggal"], errors="coerce")
                df_filtered = df[df["tanggal_dt"].dt.year == tahun_riwayat]
                if bulan_riwayat != "Semua":
                    bulan_num = list(calendar.month_name).index(bulan_riwayat)
                    df_filtered = df_filtered[df_filtered["tanggal_dt"].dt.month == bulan_num]
                df_filtered = df_filtered.sort_values("tanggal_dt", ascending=False)

                if df_filtered.empty:
                    st.info(f"Tidak ada kegiatan ditemukan untuk {nama_riwayat}.")
                else:
                    st.markdown(f"""
                    <div class="receipt-box" style="margin-bottom:0;border-radius:4px 4px 0 0;">
                        <div class="receipt-header">
                            <h3>Riwayat Kehadiran</h3>
                            <p>{nama_riwayat}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    today_ = date.today()
                    rows_list = list(df_filtered.iterrows())

                    for idx, (_, row) in enumerate(rows_list):
                        unique_key = f"{row['tanggal']}|{row['kegiatan']}|{row['lokasi']}"
                        status = st.session_state.user_history_status.get(unique_key, "belum")
                        tgl_dt = row["tanggal_dt"]
                        tgl_fmt = tgl_dt.strftime("%A, %d %B %Y")
                        sudah_lewat = tgl_dt.date() <= today_
                        is_last = (idx == len(rows_list) - 1)

                        if status == "hadir":
                            badge_html = '<span class="history-badge-hadir">Hadir</span>'
                        elif status == "tidak_hadir":
                            badge_html = '<span class="history-badge-tidak">Tidak Hadir</span>'
                        else:
                            badge_html = '<span class="history-badge-netral">Belum Ditandai</span>'

                        peny_list = parse_penyerta(str(row["penyerta"]))
                        peny_html = "".join(
                            f'<span style="display:block;margin-bottom:0.1rem;">{p}</span>'
                            for p in peny_list
                        ) if peny_list else f'<span>{str(row["penyerta"])}</span>'

                        border_bottom = "border-bottom:1px dashed #ddd8cc;" if not is_last else ""

                        if sudah_lewat:
                            col_info, col_btn = st.columns([4, 1])
                        else:
                            col_info = st.columns(1)[0]
                            col_btn = None

                        with col_info:
                            st.markdown(f"""
                            <div style="background:#fffef8;
                                        border-left:1px solid #e2e0d8;
                                        border-right:{'none' if sudah_lewat else '1px solid #e2e0d8'};
                                        padding:0.75rem 1.25rem;
                                        {border_bottom}">
                                <div class="receipt-item-title" style="margin-bottom:0.3rem;">{row['kegiatan']}</div>
                                <div class="receipt-item-row">
                                    <span class="receipt-item-label">Tanggal</span>
                                    <span class="receipt-item-value">{tgl_fmt}</span>
                                </div>
                                <div class="receipt-item-row">
                                    <span class="receipt-item-label">Lokasi</span>
                                    <span class="receipt-item-value">{row['lokasi']}</span>
                                </div>
                                <div class="receipt-item-row" style="align-items:flex-start;">
                                    <span class="receipt-item-label">Penyerta</span>
                                    <div class="receipt-item-value">{peny_html}</div>
                                </div>
                                <div style="margin-top:0.35rem;">{badge_html}</div>
                            </div>
                            """, unsafe_allow_html=True)

                        if col_btn is not None:
                            with col_btn:
                                st.markdown(f"""
                                <div style="background:#fffef8;
                                            border-right:1px solid #e2e0d8;
                                            padding:0.75rem 0.5rem;
                                            height:100%;
                                            display:flex;
                                            flex-direction:column;
                                            justify-content:center;
                                            gap:6px;
                                            {border_bottom}">
                                </div>
                                """, unsafe_allow_html=True)
                                if st.button(
                                    "✓ Hadir",
                                    key=f"hadir_{unique_key}_{idx}",
                                    use_container_width=True,
                                    type="primary" if status != "hadir" else "secondary",
                                ):
                                    st.session_state.user_history_status[unique_key] = "hadir"
                                    st.rerun()
                                if st.button(
                                    "✗ Tidak",
                                    key=f"tidak_{unique_key}_{idx}",
                                    use_container_width=True,
                                ):
                                    st.session_state.user_history_status[unique_key] = "tidak_hadir"
                                    st.rerun()

                    st.markdown(f"""
                    <div class="receipt-box" style="margin-top:0;border-radius:0 0 4px 4px;
                         border-top:none;box-shadow:none;">
                        <div class="receipt-footer">
                            <div class="receipt-barcode">|||||||||||||||||||||||</div>
                            {len(df_filtered)} kegiatan
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        except requests.exceptions.ConnectionError:
            st.error("Tidak dapat terhubung ke server.")
        except requests.exceptions.Timeout:
            st.error("Koneksi timeout.")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")

    # Jadwal Terdekat
    st.markdown("---")
    st.markdown('<div style="display:flex;align-items:center;gap:8px;"><i class="fa-solid fa-calendar-week" style="color:#14532d;"></i><span style="font-size:1.2rem;font-weight:700;color:#14532d;">Jadwal Terdekat</span></div>', unsafe_allow_html=True)
    try:
        resp_jadwal=api_get("jadwal-terdekat/")
        if resp_jadwal.status_code==200:
            jadwal=resp_jadwal.json()
            if jadwal:
                df=pd.DataFrame(jadwal)
                df.columns=['Tanggal','Lokasi','Kegiatan','Penyerta']
                st.dataframe(df, use_container_width=True, hide_index=True)
            else: st.info("Belum ada jadwal terdekat.")
        else: st.warning("Gagal memuat jadwal.")
    except: st.warning("Gagal memuat jadwal.")

# ════════════════════════════════════════
# LOGIN ADMIN
# ════════════════════════════════════════
elif st.session_state.page=="admin_login":
    _,col_m,_=st.columns([1,2,1])
    with col_m:
        st.markdown("<h3 style='text-align:center;color:#14532d;'><i class='fa-solid fa-lock'></i> Login Admin</h3>", unsafe_allow_html=True)
        with st.form("login_form"):
            username=st.text_input("Username")
            password=st.text_input("Password", type="password")
            if st.form_submit_button("Masuk"):
                if not username or not password: show_notif("Isi username dan password.","error")
                else:
                    resp=api_post("login/",{"username":username,"password":password})
                    if resp.status_code==200:
                        d=resp.json()
                        st.session_state.logged_in=True; st.session_state.token=d['token']
                        st.session_state.username=d.get('username',username)
                        st.session_state.page="admin_dashboard"
                        st.query_params["token"]=d['token']; st.rerun()
                    elif resp.status_code==429: show_notif("Terlalu banyak percobaan.","error")
                    else: show_notif(resp.json().get('error','Login gagal'),"error")

# ════════════════════════════════════════
# DASHBOARD ADMIN
# ════════════════════════════════════════
elif st.session_state.page=="admin_dashboard":
    if not st.session_state.logged_in or not st.session_state.token:
        st.warning("Login dulu."); st.session_state.page="admin_login"; st.rerun()

    st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:1rem;"><i class="fa-solid fa-gauge" style="color:#14532d;"></i><span style="font-size:1.4rem;font-weight:700;color:#14532d;">Dashboard Admin</span><span style="margin-left:auto;background:#dcfce7;color:#15803d;font-weight:600;padding:4px 12px;border-radius:999px;">{st.session_state.username}</span></div>', unsafe_allow_html=True)

    tab1,tab2,tab3,tab4,tab5=st.tabs([
        "Input Manual","Google Sheet","Pencarian","Kelola Data","History"
    ])

    # ── Tab 1: Input Manual ──
    with tab1:
        with st.form("input_form"):
            c1,c2=st.columns(2)
            with c1: tgl=st.date_input("Tanggal"); lokasi=st.text_input("Lokasi")
            with c2: kegiatan=st.text_input("Nama Kegiatan")
            penyerta_terpilih=st.multiselect("Pilih Penyerta", options=DAFTAR_NAMA)
            if not penyerta_terpilih:
                penyerta=st.text_area("Atau tulis manual (pisahkan ;)", height=80)
            else:
                penyerta="; ".join(penyerta_terpilih); st.caption(f"Penyerta: {penyerta}")
            if st.form_submit_button("Simpan"):
                if not lokasi or not kegiatan: show_notif("Lokasi dan Kegiatan wajib diisi.","error")
                else:
                    resp=api_post("kegiatan/",{"tanggal":str(tgl),"lokasi":lokasi,"kegiatan":kegiatan,"penyerta":penyerta},auth=True)
                    if resp.status_code==201: st.session_state.notif="Data berhasil disimpan!"; st.rerun()
                    else: show_notif(f"Gagal: {resp.text}","error")

    # ── Tab 2: Google Sheet ──
    with tab2:
        st.markdown('<h4><i class="fa-solid fa-cloud-arrow-up"></i> Sync Google Spreadsheet</h4>', unsafe_allow_html=True)
        st.info("Kolom yang dibutuhkan: **tanggal**, **lokasi**, **kegiatan**, **penyerta**  \n"
                "Nama dengan koma (gelar) dan nama jamak dipisah titik koma (;) didukung otomatis.")
        st.warning("Mode **Ganti semua** akan menghapus seluruh data lama sebelum mengisi ulang. "
                   "Gunakan **Tambahkan** jika hanya ingin menambah data baru.")

        if st.session_state.last_csv_url:
            url_display = st.session_state.last_csv_url
            short_url = url_display if len(url_display) <= 60 else url_display[:57] + "..."
            st.markdown(
                f"""<div style="background:#f3f4f6;border:1px solid #d1d5db;border-radius:8px;
                    padding:0.55rem 0.9rem;margin-bottom:0.75rem;display:flex;
                    align-items:center;gap:8px;word-break:break-all;">
                  <i class="fa-solid fa-link" style="color:#6b7280;flex-shrink:0;"></i>
                  <a href="{url_display}" target="_blank"
                     style="font-size:0.83rem;color:#374151;text-decoration:none;flex:1;">
                     {short_url}
                  </a>
                </div>""",
                unsafe_allow_html=True,
            )
            btn_u, btn_h, btn_s = st.columns([1, 1, 2])
            with btn_u:
                if st.button("Update Link", key="btn_update_link"):
                    st.session_state.show_csv_input = True
            with btn_h:
                if st.button("Hapus Link", key="btn_hapus_link"):
                    st.session_state.last_csv_url = ""
                    st.session_state.show_csv_input = False
                    st.rerun()
            with btn_s:
                sync_mode_rerun = st.selectbox(
                    "Mode",
                    ['append', 'replace'],
                    format_func=lambda x: "Tambahkan (aman)" if x == 'append' else "Ganti semua (hapus data lama)",
                    key="sync_mode_rerun",
                )
                if st.button("Sync Sekarang", use_container_width=True, key="btn_sync_rerun"):
                    with st.spinner("Mengambil & menyimpan data dari spreadsheet..."):
                        try:
                            saved, skipped, errors = sync_from_url(st.session_state.last_csv_url, sync_mode_rerun)
                            if saved > 0:
                                st.session_state.notif = (
                                    f"Sync berhasil! {saved} disimpan"
                                    + (f", {skipped} dilewati (duplikat)" if skipped else "")
                                    + (f", {errors} gagal" if errors else "")
                                )
                                st.rerun()
                            else:
                                show_notif(f"Tidak ada data baru. {skipped} duplikat, {errors} error.", "info")
                        except Exception as ex:
                            show_notif(f"Gagal: {ex}", "error")

            if st.session_state.get('show_csv_input'):
                st.markdown("---")
                csv_url_new = st.text_input(
                    "Link CSV baru",
                    key="csv_url_new",
                    help="Buka Google Sheet → File → Share → Publish to web → Format CSV → Salin link",
                )
                sync_mode_new = st.radio(
                    "Mode Sync",
                    ['append', 'replace'],
                    horizontal=True,
                    format_func=lambda x: "Tambahkan (aman)" if x == 'append' else "Ganti semua (hapus data lama)",
                    key="sync_mode_new",
                )
                if st.button("Simpan & Sync", key="btn_save_new_link"):
                    if csv_url_new:
                        with st.spinner("Mengambil & menyimpan data dari spreadsheet..."):
                            try:
                                saved, skipped, errors = sync_from_url(csv_url_new, sync_mode_new)
                                st.session_state.last_csv_url  = csv_url_new
                                st.session_state.show_csv_input = False
                                st.session_state.notif = (
                                    f"Sync berhasil! {saved} disimpan"
                                    + (f", {skipped} dilewati" if skipped else "")
                                    + (f", {errors} gagal" if errors else "")
                                )
                                st.rerun()
                            except Exception as ex:
                                show_notif(f"Gagal: {ex}", "error")
                    else:
                        show_notif("Masukkan link CSV terlebih dahulu.", "error")
        else:
            csv_url_blank = st.text_input(
                "Link CSV terpublikasi Google Sheet",
                key="csv_url_blank",
                help="Buka Google Sheet → File → Share → Publish to web → Format CSV → Salin link",
            )
            sync_mode_blank = st.radio(
                "Mode Sync",
                ['append', 'replace'],
                horizontal=True,
                format_func=lambda x: "Tambahkan (aman)" if x == 'append' else "Ganti semua (hapus data lama)",
                key="sync_mode_blank",
            )
            if st.button("Ambil & Simpan", key="btn_ambil_simpan"):
                if csv_url_blank:
                    with st.spinner("Mengambil & menyimpan data dari spreadsheet..."):
                        try:
                            saved, skipped, errors = sync_from_url(csv_url_blank, sync_mode_blank)
                            st.session_state.last_csv_url = csv_url_blank
                            st.session_state.notif = (
                                f"Sync berhasil! {saved} disimpan"
                                + (f", {skipped} dilewati" if skipped else "")
                                + (f", {errors} gagal" if errors else "")
                            )
                            st.rerun()
                        except Exception as ex:
                            show_notif(f"Gagal: {ex}", "error")
                else:
                    show_notif("Masukkan link CSV terlebih dahulu.", "error")

    # ── Tab 3: Pencarian ──
    with tab3:
        try:
            rd=api_get("kegiatan/", auth=True)
            semua_data=rd.json() if rd.status_code==200 else []
        except: semua_data=[]
        lokasi_list=sorted(set(d['lokasi'] for d in semua_data if d.get('lokasi')))
        kegiatan_list=sorted(set(d['kegiatan'] for d in semua_data if d.get('kegiatan')))
        penyerta_set=set()
        for d in semua_data:
            for n in parse_penyerta(d.get('penyerta','')): penyerta_set.add(n)
        penyerta_list=sorted(penyerta_set)

        st.markdown('<h4><i class="fa-solid fa-filter"></i> Filter Pencarian</h4>', unsafe_allow_html=True)
        with st.form("search_form"):
            c1,c2,c3=st.columns(3)
            with c1: tgl_src=st.date_input("Tanggal", value=None, key="src_tgl")
            with c2:
                lok_dd=st.selectbox("Lokasi", ["Semua"]+lokasi_list+["Cari manual..."])
                lok_src=st.text_input("Ketik lokasi") if lok_dd=="Cari manual..." else ("" if lok_dd=="Semua" else lok_dd)
            with c3:
                keg_dd=st.selectbox("Kegiatan", ["Semua"]+kegiatan_list+["Cari manual..."])
                keg_src=st.text_input("Ketik kegiatan") if keg_dd=="Cari manual..." else ("" if keg_dd=="Semua" else keg_dd)
            peny_dd=st.selectbox("Penyerta", ["Semua"]+penyerta_list+["Cari manual..."])
            peny_src=st.text_input("Ketik penyerta") if peny_dd=="Cari manual..." else ("" if peny_dd=="Semua" else peny_dd)
            if st.form_submit_button("Cari"):
                prms={}
                if tgl_src: prms["tanggal"]=str(tgl_src)
                if lok_src: prms["lokasi"]=lok_src
                if keg_src: prms["kegiatan"]=keg_src
                if peny_src: prms["penyerta"]=peny_src
                if not prms: st.warning("Isi minimal satu filter.")
                else:
                    try:
                        resp=api_get("search-admin/", params=prms, auth=True)
                        if resp.status_code==200:
                            hasil=resp.json()
                            if hasil:
                                groups=defaultdict(list)
                                for item in hasil:
                                    groups[(item['tanggal'],item['lokasi'],item['kegiatan'])].append(item['penyerta'])
                                st.success(f"Ditemukan {len(groups)} grup data")
                                for (tgl,lok,keg),list_p in groups.items():
                                    names=[n for p in list_p for n in parse_penyerta(p)]
                                    st.markdown(f"<div class='data-card'><b>{tgl}</b> — {lok}<br><b>{keg}</b><br><small>{'<br>'.join(names)}</small></div>", unsafe_allow_html=True)
                            else: st.info("Tidak ditemukan")
                        else: show_notif("Gagal mengambil data","error")
                    except Exception as e: st.error(f"Error: {e}")

        st.markdown("---")
        st.markdown('<h4><i class="fa-solid fa-user-plus"></i> Cek Karyawan Tidak Terjadwal</h4>', unsafe_allow_html=True)
        st.caption("Lihat karyawan tanpa jadwal dalam gedung pada tanggal tertentu.")
        cc1,cc2,cc3=st.columns([2,2,1])
        with cc1: tgl_cek=st.date_input("Pilih Tanggal", datetime.now().date(), key="tgl_cek_karyawan")
        with cc2: role_filter=st.multiselect("Filter Role", ["Dokter","Perawat","Bidan","Promkes","Sanitarian","Gizi","Apoteker","Lab","Gigi","Administrasi"], default=[])
        with cc3:
            if st.button("Cek", use_container_width=True, type="primary"):
                tgl_str=str(tgl_cek)
                def get_kary_local(rk):
                    rm={'dokter':['dr.','drg.'],'perawat_ners':['Ners','S.Kep','Amd.Kep','A.Md.Kep'],
                        'bidan':['Bdn.','S.Tr.Keb','Am.Keb','A.Md.Keb'],'promkes':['Promosi','SKM'],
                        'sanitarian':['Sanitarian','S.K.M','A.Md.KL'],'gizi':['S.Gz','A.Md.Gz'],
                        'apoteker':['Apt','S.Farm'],'lab':['A.Md.AK'],'gigi':['drg.','S.Tr.Kes'],
                        'administrasi':['S.E','S.T','S.Kep','S.ST','SKM','AMd.RMIK']}
                    kw=rm.get(rk,[])
                    return list(set([n for n in DAFTAR_NAMA if n not in NAMA_DIECUALIKAN and any(k.lower() in n.lower() for k in kw)]))
                semua_k=[]
                roles=list(ROLE_MAP.keys()) if not role_filter else [r for r in role_filter if r in ROLE_MAP]
                for r in roles: semua_k.extend(get_kary_local(r))
                semua_k=list(set(semua_k))
                if not semua_k: st.warning("Tidak ada karyawan.")
                else:
                    try:
                        rj=api_get("kegiatan/", auth=True)
                        if rj.status_code==200:
                            jt=[j for j in rj.json() if j['tanggal']==tgl_str]
                            terjadwal=set()
                            for j in jt: terjadwal.update(parse_penyerta(j['penyerta']))
                            tidak=[k for k in semua_k if k not in terjadwal]
                            if tidak:
                                st.warning(f"{len(tidak)} karyawan tidak terjadwal.")
                                df=pd.DataFrame({"No":range(1,len(tidak)+1),"Nama":sorted(tidak)})
                                st.dataframe(df, use_container_width=True, hide_index=True)
                                st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8-sig'), f"tidak_terjadwal_{tgl_str}.csv",'text/csv')
                            else: st.success("Semua sudah terjadwal.")
                    except: st.error("Gagal mengambil data.")

    # ── Tab 4: Kelola Data ──
    with tab4:
        st.subheader("Daftar Semua Kegiatan")
        try:
            resp=api_get("kegiatan/", auth=True)
            if resp.status_code==200:
                data=resp.json()
                if data:
                    df_raw=pd.DataFrame(data)
                    df_grouped=(
                        df_raw.groupby(['tanggal','lokasi','kegiatan'], sort=False)
                        .agg(penyerta=('penyerta',lambda x:';\n'.join(x.tolist())), ids=('id',list))
                        .reset_index()
                    )
                    df_grouped.columns=['Tanggal','Lokasi','Kegiatan','Penyerta','IDs']

                    if st.session_state.pending_delete_ids:
                        flat_ids=[i for sub in st.session_state.pending_delete_ids for i in sub]
                        if flat_ids:
                            with st.spinner("Menghapus..."):
                                rd=api_post("kegiatan/bulk-delete/",{"ids":flat_ids},auth=True)
                                if rd.status_code==200:
                                    st.session_state.notif=rd.json().get('message')
                                    st.session_state.pending_delete_ids=[]; st.rerun()
                                else: show_notif("Gagal menghapus","error")

                    event=st.dataframe(
                        df_grouped[['Tanggal','Lokasi','Kegiatan','Penyerta']],
                        use_container_width=True, hide_index=True,
                        on_select="rerun", selection_mode="multi-row", key="kelola_data"
                    )
                    selected_rows=event.selection.rows if event.selection else []
                    if selected_rows:
                        sel_ids=[df_grouped.iloc[i]['IDs'] for i in selected_rows]
                        st.markdown(f"**{len(sel_ids)} grup terpilih**")
                        if st.button("Hapus Data Terpilih"):
                            st.session_state.pending_delete_ids=sel_ids; st.rerun()

                    st.markdown("---")
                    st.markdown('<h4><i class="fa-solid fa-pen-to-square"></i> Edit Data</h4>', unsafe_allow_html=True)
                    opsi_edit=["—"]+[f"{r['Tanggal']} | {r['Lokasi']} | {r['Kegiatan']}" for _,r in df_grouped.iterrows()]
                    pilihan=st.selectbox("Pilih kegiatan", opsi_edit)
                    if pilihan!="—":
                        tp,lp,kp=pilihan.split(" | ")
                        matched=df_grouped[(df_grouped['Tanggal']==tp)&(df_grouped['Lokasi']==lp)&(df_grouped['Kegiatan']==kp)]
                        if not matched.empty:
                            eid=matched.iloc[0]['IDs'][0]
                            if st.button("Muat Data"):
                                rd=api_get(f"kegiatan/{eid}/", auth=True)
                                if rd.status_code==200:
                                    st.session_state.edit_data=rd.json(); st.session_state.edit_id=eid; st.rerun()
                    if st.session_state.edit_data and st.session_state.edit_id:
                        with st.form("edit_form"):
                            tgl_ed=st.date_input("Tanggal", value=pd.to_datetime(st.session_state.edit_data['tanggal']))
                            lok_ed=st.text_input("Lokasi", value=st.session_state.edit_data['lokasi'])
                            keg_ed=st.text_input("Nama Kegiatan", value=st.session_state.edit_data['kegiatan'])
                            peny_ed=st.text_area("Penyerta", value=st.session_state.edit_data['penyerta'])
                            if st.form_submit_button("Update"):
                                ru=api_put(f"kegiatan/{st.session_state.edit_id}/",
                                           {"tanggal":str(tgl_ed),"lokasi":lok_ed,"kegiatan":keg_ed,"penyerta":peny_ed})
                                if ru.status_code==200:
                                    st.session_state.notif="Data diperbarui!"; st.session_state.edit_data=None; st.session_state.edit_id=None; st.rerun()
                                else: show_notif(ru.text,"error")

                    st.markdown("---")
                    st.markdown('<h4><i class="fa-solid fa-calendar-xmark"></i> Hapus per Bulan/Tahun</h4>', unsafe_allow_html=True)
                    cm,cy,cb=st.columns([2,2,1])
                    with cm: bulan=st.selectbox("Bulan", range(1,13), index=datetime.now().month-1)
                    with cy: tahun=st.number_input("Tahun", value=datetime.now().year)
                    with cb:
                        if st.button("Hapus"):
                            rd=api_post("delete-by-date/",{"month":bulan,"year":tahun},auth=True)
                            if rd.status_code==200: st.session_state.notif=rd.json()['message']; st.rerun()
                            else: show_notif("Gagal","error")

                    st.markdown("---")
                    st.markdown('<h5>⬇ Download Data Kegiatan</h5>', unsafe_allow_html=True)
                    cd1,cd2=st.columns(2)
                    with cd1: generate_csv(data,"semua_kegiatan.csv")
                    with cd2:
                        pdf_buf=generate_jadwal_pdf(data)
                        st.download_button("⬇ Download PDF", data=pdf_buf, file_name="semua_kegiatan.pdf",
                                           mime="application/pdf", use_container_width=True)
                else: st.info("Belum ada data")
            else: show_notif("Gagal memuat data","error")
        except Exception as e: st.error(f"Error: {e}")

    # ── Tab 5: History ──
    with tab5:
        st.subheader("History Kegiatan")
        st.caption("Riwayat kegiatan yang sudah lewat dan akan datang")
        hf1,hf2,hf3=st.columns([2,2,1])
        with hf1: filter_status=st.selectbox("Status",["Semua","Sudah Lewat","Hari Ini","Akan Datang"],key="filter_status_history")
        with hf2: filter_bulan=st.selectbox("Bulan",["Semua"]+list(calendar.month_name)[1:],key="filter_bulan_history")
        with hf3:
            if st.button("Refresh", key="refresh_history"): st.rerun()

        try:
            resp=api_get("kegiatan/", auth=True)
            if resp.status_code==200:
                all_data=resp.json()
                if all_data:
                    today=date.today()
                    df=pd.DataFrame(all_data)
                    df['tanggal_date']=pd.to_datetime(df['tanggal']).dt.date
                    df=df.sort_values('tanggal_date', ascending=False)
                    if filter_status=="Sudah Lewat": df=df[df['tanggal_date']<today]
                    elif filter_status=="Hari Ini": df=df[df['tanggal_date']==today]
                    elif filter_status=="Akan Datang": df=df[df['tanggal_date']>today]
                    if filter_bulan!="Semua":
                        bnum=list(calendar.month_name).index(filter_bulan)
                        df=df[pd.to_datetime(df['tanggal']).dt.month==bnum]
                    filtered_data=df.to_dict('records')
                    if df.empty:
                        st.info("Tidak ada data sesuai filter.")
                    else:
                        items=""
                        for _,row in df.iterrows():
                            td=row['tanggal_date']
                            if td<today: sts="Sudah Lewat"; badge="status-past"
                            elif td==today: sts="HARI INI"; badge="status-today"
                            elif td==today+timedelta(days=1): sts="Besok"; badge="status-soon"
                            else: sts="Akan Datang"; badge="status-future"
                            tgl_fmt=pd.to_datetime(row['tanggal']).strftime('%A, %d %B %Y')
                            peny_list = parse_penyerta(str(row['penyerta']))
                            peny_disp = ''.join(f'<span>{p}</span>' for p in peny_list) if peny_list else f'<span>{str(row["penyerta"])[:120]}</span>'
                            items+=f"""<div class="receipt-item">
                                <div class="receipt-item-title">{row['kegiatan']} <span class="receipt-status-badge {badge}">{sts}</span></div>
                                <div class="receipt-item-row"><span class="receipt-item-label">Tanggal</span><span class="receipt-item-value">{tgl_fmt}</span></div>
                                <div class="receipt-item-row"><span class="receipt-item-label">Lokasi</span><span class="receipt-item-value">{row['lokasi']}</span></div>
                                <div class="receipt-item-row"><span class="receipt-item-label">Penyerta</span><div class="receipt-item-value"><div class="receipt-penyerta-list">{peny_disp}</div></div></div>
                            </div>"""
                        st.markdown(f"""<div class="receipt-box">
                            <div class="receipt-header"><h3>History Kegiatan</h3></div>
                            <div class="receipt-body">{items}</div>
                            <div class="receipt-footer">
                                <div class="receipt-barcode">|||||||||||||||||||||||</div>
                                {len(df)} kegiatan &bull; Puskesmas Sangkali
                            </div>
                        </div>""", unsafe_allow_html=True)
                        hd1,hd2=st.columns(2)
                        with hd1: generate_csv(filtered_data,"history_kegiatan.csv")
                        with hd2:
                            pdf_buf=generate_jadwal_pdf(filtered_data)
                            st.download_button("⬇ Download PDF", data=pdf_buf, file_name="history_kegiatan.pdf",
                                               mime="application/pdf", use_container_width=True)
                else: st.info("Belum ada data kegiatan.")
            else: show_notif("Gagal memuat data","error")
        except Exception as e: st.error(f"Error: {e}")

        # Hapus Massal
        st.markdown("---")
        st.subheader("Hapus Massal")
        if not st.session_state.confirm_hapus_massal:
            if st.button("Hapus Semua Kegiatan yang Sudah Lewat", key="btn_hapus_massal"):
                st.session_state.confirm_hapus_massal=True; st.rerun()
        else:
            st.warning("Yakin ingin menghapus **semua** kegiatan yang sudah lewat? Tindakan ini tidak dapat dibatalkan.")
            cy2,cn2,_=st.columns([1,1,2])
            with cy2:
                if st.button("Ya, Hapus Sekarang", key="confirm_ya_hapus", type="primary"):
                    with st.spinner("Menghapus..."):
                        try:
                            r=api_get("kegiatan/", auth=True)
                            if r.status_code==200:
                                today=date.today()
                                ids_del=[item['id'] for item in r.json()
                                         if datetime.strptime(item['tanggal'],'%Y-%m-%d').date()<today]
                                if ids_del:
                                    rd=api_post("kegiatan/bulk-delete/",{"ids":ids_del},auth=True)
                                    if rd.status_code==200:
                                        st.session_state.notif=f"Berhasil menghapus {len(ids_del)} kegiatan!"
                                        st.session_state.confirm_hapus_massal=False; st.rerun()
                                    else: st.error(f"Gagal menghapus. {rd.text}")
                                else: st.info("Tidak ada kegiatan yang sudah lewat."); st.session_state.confirm_hapus_massal=False
                            else: show_notif("Gagal mengambil data.","error")
                        except Exception as e: st.error(f"Error: {e}")
            with cn2:
                if st.button("Batal", key="confirm_batal_hapus"):
                    st.session_state.confirm_hapus_massal=False; st.rerun()

# ── FOOTER ──
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
        <div class="footer-section"></div>
    </div>
    <hr class="footer-divider">
    <div class="footer-bottom">&copy; 2026 UPTD Puskesmas Sangkali</div>
</div>
""", unsafe_allow_html=True)