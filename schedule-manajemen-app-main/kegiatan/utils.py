import re

def capitalisasi_judul(teks):
    """Mengubah teks menjadi Title Case dengan pengecualian kata depan."""
    kata_kecil = {'di', 'ke', 'dari', 'pada', 'yang', 'dan', 'atau', 'untuk',
                  'dengan', 'dalam', 'itu', 'ini', 'tersebut'}
    kata_kapital_khusus = {'puskesmas', 'posyandu', 'lansia', 'imunisasi', 'penyuluhan',
                           'balai', 'desa', 'sd', 'sdn', 'smp', 'sma', 'tk'}  # bisa ditambah

    # Pisah berdasarkan spasi, tapi hormati koma dan lainnya
    kata = re.split(r'(\s+)', teks)
    hasil = []
    for i, k in enumerate(kata):
        if not k.strip():
            hasil.append(k)
            continue
        lower = k.lower()
        if i == 0:
            # Kata pertama selalu kapital
            if lower in kata_kapital_khusus:
                hasil.append(k.upper() if lower in ('sd','sdn','smp','sma','tk') else k.capitalize())
            else:
                hasil.append(k.capitalize())
        elif lower in kata_kecil:
            hasil.append(lower)
        elif lower in kata_kapital_khusus:
            hasil.append(k.upper() if lower in ('sd','sdn','smp','sma','tk') else k.capitalize())
        else:
            hasil.append(k.capitalize())
    return ''.join(hasil)