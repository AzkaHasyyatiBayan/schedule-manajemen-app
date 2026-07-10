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
from io import StringIO
from datetime import datetime


class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'


# =============================================
# PERBAIKAN TANGGAL DI SINI
# =============================================
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
            
            # PERBAIKAN UTAMA
            if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', tanggal_raw):
                tgl = pd.to_datetime(tanggal_raw, dayfirst=True, errors='coerce').date()
            else:
                tgl = pd.to_datetime(tanggal_raw, errors='coerce').date()

            if pd.isna(tgl):
                errors.append(f'Baris {i+2}: Format tanggal salah ({tanggal_raw})')
                continue

            lok = str(row['lokasi']).strip()
            keg = capitalisasi_judul(str(row['kegiatan']).strip())
            peny = str(row.get('penyerta', '')).strip()

            kat = str(row.get('kategori', 'luar_gedung')).strip().lower()
            if kat not in ['dalam_gedung', 'luar_gedung']:
                kat = 'luar_gedung'

            sub_kat = str(row.get('sub_kategori', 'lainnya')).strip().lower()
            if sub_kat not in ['posyandu', 'bok', 'sekolah', 'kunjungan_lapangan', 'inspeksi', 'rapat', 'lainnya']:
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
            errors.append(f'Baris {i+2}: {str(e)}')

    msg = f'{created} data baru diimpor.'
    if mode == 'replace':
        msg = f'Data lama dihapus. {msg}'
    if skipped > 0:
        msg += f' {skipped} data sudah ada dan dilewati.'
    
    result = {'message': msg, 'format': 'flat'}
    if errors:
        result['peringatan'] = errors[:10]
    return Response(result)


# Sisanya (fungsi sync, pivot, search, dll) tetap
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_google_sheets(request):
    url = request.data.get('csv_url', '').strip()
    mode = request.data.get('mode', 'append')

    if not url:
        return Response({'error': 'Parameter csv_url diperlukan'}, status=400)

    try:
        if '/spreadsheets/d/' in url:
            if '/export?format=csv' not in url:
                sheet_id = url.split('/d/')[1].split('/')[0]
                csv_url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv'
            else:
                csv_url = url
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
        return Response({'error': f'Gagal mengambil data: {str(e)}'}, status=500)


# (Fungsi _process_pivot_format, search_user, dll bisa ditambahkan nanti)
# Untuk sekarang cukup dulu yang di atas.

@api_view(['GET'])
@permission_classes([AllowAny])
def search_user(request):
    qs = Kegiatan.objects.all()
    tgl = request.query_params.get('tanggal')
    nama = request.query_params.get('nama')

    if tgl:
        qs = qs.filter(tanggal=tgl)
    if nama:
        qs = qs.filter(penyerta__icontains=nama)

    data = [{
        'tanggal': str(k.tanggal),
        'lokasi': k.lokasi,
        'kegiatan': k.kegiatan,
        'penyerta': k.penyerta,
        'kategori': k.kategori,
        'sub_kategori': k.sub_kategori,
        'source': k.source,
    } for k in qs]
    return Response(data)