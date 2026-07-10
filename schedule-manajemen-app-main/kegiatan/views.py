from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, throttle_classes, action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.throttling import AnonRateThrottle
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from django.utils import timezone
from .models import Kegiatan, HariLibur
from .serializers import KegiatanSerializer, HariLiburSerializer
from .utils import capitalisasi_judul
import pandas as pd
import requests
import re
import traceback
from io import StringIO
from datetime import datetime


# Throttle khusus untuk login
class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'


# HELPER: AUTO SYNC HARI LIBUR
def auto_sync_hari_libur_if_needed(tahun):
    existing_count = HariLibur.objects.filter(tanggal__year=tahun).count()
    if existing_count > 0:
        return True, f"Hari libur tahun {tahun} sudah ada ({existing_count} data)"
    
    try:
        url = f"https://date.nager.at/api/v3/PublicHolidays/{tahun}/ID"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        holidays = response.json()
        created_count = 0
        
        for holiday in holidays:
            tanggal = holiday['date']
            nama_libur = holiday.get('localName', holiday.get('name', 'Hari Libur'))
            
            if HariLibur.objects.filter(tanggal=tanggal).exists():
                continue
            
            jenis = 'cuti_bersama' if 'Cuti Bersama' in nama_libur or 'Joint Holiday' in nama_libur else 'nasional'
            
            HariLibur.objects.create(
                tanggal=tanggal,
                keterangan=nama_libur,
                jenis=jenis
            )
            created_count += 1
        
        return True, f"Auto-sync berhasil: {created_count} hari libur tahun {tahun} ditambahkan"
    
    except Exception as e:
        return False, f"Auto-sync gagal: {str(e)}"


# ViewSet CRUD
@method_decorator(csrf_exempt, name='dispatch')
class KegiatanViewSet(viewsets.ModelViewSet):
    queryset = Kegiatan.objects.all().order_by('-tanggal')
    serializer_class = KegiatanSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        nama = serializer.validated_data.get('kegiatan', '')
        serializer.save(kegiatan=capitalisasi_judul(nama), source='manual')

    def perform_update(self, serializer):
        nama = serializer.validated_data.get('kegiatan', '')
        serializer.save(kegiatan=capitalisasi_judul(nama))

    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': 'ids diperlukan'}, status=400)
        deleted, _ = Kegiatan.objects.filter(id__in=ids).delete()
        return Response({'message': f'{deleted} data dihapus.'})


# Login & Logout (tidak berubah)
@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([LoginRateThrottle])
def login_view(request):
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    if not username or not password:
        return Response({'error': 'Username dan password wajib diisi'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(request, username=username, password=password)
    if user is not None:
        if not user.is_active:
            return Response({'error': 'Akun tidak aktif'}, status=status.HTTP_403_FORBIDDEN)
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'Login berhasil',
            'token': token.key,
            'username': user.username,
        })
    return Response({'error': 'Username atau password salah'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        request.user.auth_token.delete()
    except Exception:
        pass
    return Response({'message': 'Logout berhasil'})


# Helper Functions
BULAN_MAP = {
    'Januari': 1, 'Februari': 2, 'Maret': 3, 'April': 4,
    'Mei': 5, 'Juni': 6, 'Juli': 7, 'Agustus': 8,
    'September': 9, 'Oktober': 10, 'November': 11, 'Desember': 12
}

def parse_tanggal_indo(text):
    text = str(text).strip()
    text = re.sub(r'^(Senin|Selasa|Rabu|Kamis|Jumat|Sabtu|Minggu),?\s*', '', text, flags=re.IGNORECASE)
    match = re.match(r'(\d{1,2})\s+(\w+)\s+(\d{4})', text)
    if match:
        day = int(match.group(1))
        month_name = match.group(2)
        year = int(match.group(3))
        month = BULAN_MAP.get(month_name)
        if month:
            try:
                return datetime(year, month, day).strftime('%Y-%m-%d')
            except:
                pass
    return None


def split_names(text):
    if not text or str(text).strip().lower() in ['nan', 'none', '']:
        return []
    text = str(text).strip()
    if ';' in text:
        return [n.strip() for n in text.split(';') if n.strip()]
    if '\n' in text:
        return [n.strip() for n in text.split('\n') if n.strip()]
    text = re.sub(r'\s+', ' ', text).strip()
    pattern = r'((?:dr\.?|drg\.?)?\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s*,\s*)?(?:S\.Tr\.Keb|S\.Kep\.?\s*,?\s*Ners|AMK|SKM|A\.Md\.Keb|A\.Md\.KL|S\.Gz|A\.Md\.Gz|S\.Farm\.?\s*,?\s*Apt|S\.E|S\.T|AMd\.?\s*RMIK|S\.ST|S\.Tr\.Kes|A\.Md\.AK|A\.Md\.Farm|A\.Md\.Kep|Amd\.?\s*Kep|Am\.?\s*Keb|dr\.?|drg\.?)?)'
    matches = re.findall(pattern, text)
    if len(matches) > 1:
        return [m.strip() for m in matches if m.strip()]
    return [text] if text else []


# SYNC GOOGLE SHEETS - PERBAIKAN UTAMA
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_google_sheets(request):
    url = request.data.get('csv_url', '').strip()
    mode = request.data.get('mode', 'append')

    if not url:
        return Response({'error': 'Parameter csv_url diperlukan'}, status=400)

    try:
        if '/spreadsheets/d/e/' in url:
            csv_url = url.split('?')[0] + '?output=csv'
        elif '/spreadsheets/d/' in url:
            sheet_id = url.split('/d/')[1].split('/')[0]
            csv_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
        else:
            csv_url = url

        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(csv_url, headers=headers, timeout=15)
        resp.raise_for_status()

        df_check = pd.read_csv(StringIO(resp.text))
        df_check.columns = [c.lower().strip() for c in df_check.columns]
        
        is_flat_format = all(col in df_check.columns for col in ['tanggal', 'lokasi', 'kegiatan', 'penyerta'])
        
        if is_flat_format:
            return _process_flat_format(df_check, mode)
        else:
            df_pivot = pd.read_csv(StringIO(resp.text), header=None)
            return _process_pivot_format(df_pivot, mode)

    except Exception as e:
        return Response({'error': str(e)}, status=500)


def _process_flat_format(df, mode):
    """Proses format flat - TANGGAL SUDAH DIPERBAIKI"""
    df = df.dropna(subset=['tanggal', 'lokasi'])

    if mode == 'replace':
        Kegiatan.objects.filter(source='google_sheet').delete()
    
    created = 0
    skipped = 0
    errors = []
    
    for i, row in df.iterrows():
        try:
            tanggal_raw = str(row['tanggal']).strip()
            
            # PERBAIKAN KRITIS: Paksa format Indonesia (DD/MM/YYYY)
            if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', tanggal_raw):
                tgl = pd.to_datetime(tanggal_raw, dayfirst=True, errors='coerce').date()
            else:
                tgl = pd.to_datetime(tanggal_raw, errors='coerce').date()

            if pd.isna(tgl):
                errors.append(f'Baris {i+2}: Format tanggal tidak dikenali ({tanggal_raw})')
                continue

            lok = str(row['lokasi']).strip()
            keg = capitalisasi_judul(str(row['kegiatan']).strip())
            peny = str(row.get('penyerta', '')).strip()

            kat = str(row.get('kategori', 'luar_gedung')).strip().lower()
            if kat not in ['dalam_gedung', 'luar_gedung']:
                kat = 'luar_gedung'

            sub_kat = str(row.get('sub_kategori', 'lainnya')).strip().lower()
            valid_sub = ['posyandu', 'bok', 'sekolah', 'kunjungan_lapangan', 'inspeksi', 'rapat', 'lainnya']
            if sub_kat not in valid_sub:
                sub_kat = 'lainnya'

            if mode == 'append' and Kegiatan.objects.filter(tanggal=tgl, lokasi=lok, kegiatan=keg).exists():
                skipped += 1
                continue

            Kegiatan.objects.create(
                tanggal=tgl,
                lokasi=lok,
                kegiatan=keg,
                penyerta=peny,
                kategori=kat,
                sub_kategori=sub_kat,
                source='google_sheet'
            )
            created += 1
        except Exception as e:
            errors.append(f'Baris {i+2}: {str(e)} - Tanggal: {row.get("tanggal")}')

    msg = f'{created} data baru diimpor.'
    if mode == 'replace':
        msg = f'Data lama dihapus. {msg}'
    if skipped > 0:
        msg += f' {skipped} data sudah ada dan dilewati.'
    
    result = {'message': msg, 'format': 'flat'}
    if errors:
        result['peringatan'] = errors[:10]
    return Response(result)


# Fungsi _process_pivot_format dan endpoint lainnya tetap sama seperti sebelumnya
# (saya tidak ubah karena tidak berhubungan dengan bug tanggal flat format)