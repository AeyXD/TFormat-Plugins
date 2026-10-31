import sys
import os
import csv
import struct

# =====================================================================
# Boltgun_packer.py — อัปเดตคำแปลจาก CSV กลับเข้าไฟล์ .locres ของ Boltgun
# ใช้ stdlib ล้วน (เดิมพึ่ง pylocres — ถอดออกแล้ว)
# โค้ดส่วนอ่าน locres จงใจก๊อปจาก Boltgun_unpacker.py เพราะทุกไฟล์ใน
# repo นี้ต้อง standalone ห้าม import ข้ามไฟล์ — ถ้าแก้ format ให้แก้ทั้งสองไฟล์
# =====================================================================

LOCRES_MAGIC = b'\x0E\x14\x74\x75\x67\x4A\x03\xFC\x4A\x15\x90\x9D\xC3\x37\x7F\x1B'


def _read_fstring(data, offset):
    """อ่าน FString (length-prefixed) ตาม serialization ของ UE:
    length > 0 = utf-8/ascii, length < 0 = utf-16le, 0 = ค่าว่าง
    คืน (text, offset ถัดไป)"""
    (length,) = struct.unpack_from('<i', data, offset)
    offset += 4
    if length > 0:
        raw = data[offset:offset + length]
        offset += length
        return raw.decode('utf-8', errors='replace').rstrip('\x00'), offset
    if length < 0:
        raw = data[offset:offset + length * -2]
        offset += length * -2
        return raw.decode('utf-16-le', errors='replace').rstrip('\x00'), offset
    return '', offset


def read_locres(filepath):
    """อ่านไฟล์ .locres คืน (version, namespaces)
    namespaces = [{'name', 'hash', 'entries': [{'key', 'key_hash',
    'source_hash', 'translation'}]}] ตามลำดับเดิมในไฟล์ — hash ทุกชนิด
    เก็บค่าจากไฟล์ต้นฉบับไว้เพื่อให้เขียนกลับได้แบบคงค่าเดิมโดยไม่ต้อง
    คำนวณ CRC/CityHash เอง"""
    with open(filepath, 'rb') as f:
        data = f.read()

    if data[:16] != LOCRES_MAGIC:
        raise ValueError(f"ไม่ใช่ไฟล์ .locres ที่รองรับ (magic ไม่ตรง): {filepath}")
    version = data[16]
    if version not in (1, 2, 3):
        raise ValueError(f"ไม่รองรับ locres version {version} (รองรับ 1–3): {filepath}")
    (strings_offset,) = struct.unpack_from('<Q', data, 17)

    strings = []
    offset = strings_offset
    (count,) = struct.unpack_from('<I', data, offset)
    offset += 4
    for _ in range(count):
        text, offset = _read_fstring(data, offset)
        if version >= 2:
            offset += 4  # refcount
        strings.append(text)

    offset = 25
    if version >= 2:
        offset += 4  # จำนวน entry รวมทุก namespace

    namespaces = []
    (ns_count,) = struct.unpack_from('<I', data, offset)
    offset += 4
    for _ in range(ns_count):
        ns_hash = 0
        if version >= 2:
            (ns_hash,) = struct.unpack_from('<I', data, offset)
            offset += 4
        name, offset = _read_fstring(data, offset)
        (key_count,) = struct.unpack_from('<I', data, offset)
        offset += 4
        entries = []
        for _ in range(key_count):
            key_hash = 0
            if version >= 2:
                (key_hash,) = struct.unpack_from('<I', data, offset)
                offset += 4
            key, offset = _read_fstring(data, offset)
            (source_hash,) = struct.unpack_from('<I', data, offset)
            offset += 4
            (string_index,) = struct.unpack_from('<I', data, offset)
            offset += 4
            translation = strings[string_index] if string_index < len(strings) else ''
            entries.append({'key': key, 'key_hash': key_hash,
                            'source_hash': source_hash, 'translation': translation})
        namespaces.append({'name': name, 'hash': ns_hash, 'entries': entries})

    return version, namespaces


def _write_fstring(buf, value):
    """เขียน FString ตาม serialization ของ UE: ascii ล้วน → positive length,
    มีอักขระอื่น (เช่น ไทย) → negative length + utf-16le"""
    value = value + '\x00'
    try:
        encoded = value.encode('ascii')
        buf += struct.pack('<i', len(encoded))
        buf += encoded
    except UnicodeEncodeError:
        encoded = value.encode('utf-16-le')
        buf += struct.pack('<i', -(len(encoded) // 2))
        buf += encoded


def write_locres(filepath, version, namespaces):
    """เขียน namespaces กลับเป็นไฟล์ .locres
    hash ของ namespace/key/source ใช้ค่าที่อ่านมาจากไฟล์เดิม (ไม่คำนวณใหม่)
    string table สร้างใหม่แบบ dedup ตามลำดับที่เจอครั้งแรก + refcount
    (โครงสร้างเดียวกับที่ UE/pylocres ใช้)"""
    out = bytearray()
    out += LOCRES_MAGIC
    out += struct.pack('<B', version)
    out += b'\x00' * 8  # string table offset — patch ทีหลังเมื่อรู้ตำแหน่งจริง

    strings = {}
    for ns in namespaces:
        for entry in ns['entries']:
            text = entry['translation']
            if text in strings:
                strings[text][0] += 1
            else:
                strings[text] = [1, len(strings)]
            entry['string_index'] = strings[text][1]

    total_keys = sum(len(ns['entries']) for ns in namespaces)
    if version >= 2:
        out += struct.pack('<I', total_keys)
    out += struct.pack('<I', len(namespaces))
    for ns in namespaces:
        if version >= 2:
            out += struct.pack('<I', ns['hash'])
        _write_fstring(out, ns['name'])
        out += struct.pack('<I', len(ns['entries']))
        for entry in ns['entries']:
            if version >= 2:
                out += struct.pack('<I', entry['key_hash'])
            _write_fstring(out, entry['key'])
            out += struct.pack('<I', entry['source_hash'])
            out += struct.pack('<I', entry['string_index'])

    struct.pack_into('<Q', out, 17, len(out))
    out += struct.pack('<I', len(strings))
    for text, (refcount, _index) in strings.items():
        _write_fstring(out, text)
        if version >= 2:
            out += struct.pack('<I', refcount)

    with open(filepath, 'wb') as f:
        f.write(out)


def csv_col(reader, *names):
    """คืนชื่อคอลัมน์จริงตัวแรกที่ตรงกับ names (case-insensitive, รองรับ header เก่า
    เช่น original/translation หรือ ต้นฉบับ/คำแปล)"""
    fields = reader.fieldnames or []
    lower = {str(x).lower().strip(): x for x in fields if x}
    for n in names:
        if n in fields:
            return n
        if n.lower() in lower:
            return lower[n.lower()]
    return None


def pack_locres(original_locres, translated_csv, output_locres):
    if not os.path.exists(original_locres):
        print(f"Error: Original locres file '{original_locres}' not found.")
        return
    if not os.path.exists(translated_csv):
        print(f"Error: Translated CSV file '{translated_csv}' not found.")
        return

    # 1. Read translated CSV
    print(f"Reading translations from {translated_csv}...")
    translations = {}
    try:
        with open(translated_csv, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.DictReader(f)
            id_col = csv_col(reader, "ID", "id")
            trans_col = csv_col(reader, "Translation", "translation", "คำแปล")
            if not id_col or not trans_col:
                print(f"Error: CSV header ไม่ถูกต้อง (ต้องมี ID และ Translation, พบ: {reader.fieldnames})")
                return
            for row in reader:
                row_id = (row.get(id_col) or "").strip()
                translated_text = row.get(trans_col) or ""
                # Only use translation if it is not empty
                if row_id and translated_text:
                    translations[row_id] = translated_text
    except Exception as e:
        print(f"Failed to read CSV: {e}")
        return

    print(f"Loaded {len(translations)} translated strings.")

    # 2. Load original Locres
    print(f"Loading original locres {original_locres}...")
    try:
        version, namespaces = read_locres(original_locres)
    except ValueError as e:
        print(f"Failed to read locres file: {e}")
        return

    # 3. Apply translations
    changed = 0
    for ns in namespaces:
        for entry in ns['entries']:
            row_id = f"{ns['name']}::{entry['key']}"
            if row_id in translations:
                entry['translation'] = translations[row_id]
                changed += 1

    # 4. Save new Locres
    os.makedirs(os.path.dirname(output_locres) if os.path.dirname(output_locres) else '.', exist_ok=True)
    try:
        write_locres(output_locres, version, namespaces)
        print(f"Successfully modified {changed} strings and saved to '{output_locres}'")
    except Exception as e:
        print(f"Failed to write output locres: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python Boltgun_packer.py <original.locres> <translated.csv> <output.locres>")
        sys.exit(1)

    pack_locres(sys.argv[1], sys.argv[2], sys.argv[3])
