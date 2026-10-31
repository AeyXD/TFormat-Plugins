import sys
import os
import csv
import struct

# =====================================================================
# Boltgun_unpacker.py — แตกไฟล์ .locres ของ W.A.S.P. Boltgun ออกเป็น CSV
# รองรับ locres version 1–3 (Compact/Optimized/CityHash, magic 16 bytes)
# ใช้ stdlib ล้วน (เดิมพึ่ง pylocres — ถอดออกแล้ว)
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
    เก็บค่าจากไฟล์ต้นฉบับไว้เพื่อให้ pack กลับได้แบบคงไบต์เดิม"""
    with open(filepath, 'rb') as f:
        data = f.read()

    if data[:16] != LOCRES_MAGIC:
        raise ValueError(f"ไม่ใช่ไฟล์ .locres ที่รองรับ (magic ไม่ตรง): {filepath}")
    version = data[16]
    if version not in (1, 2, 3):
        raise ValueError(f"ไม่รองรับ locres version {version} (รองรับ 1–3): {filepath}")
    (strings_offset,) = struct.unpack_from('<Q', data, 17)

    # string table (อยู่ท้ายไฟล์): count ตามด้วย [FString + refcount] เรียงกัน
    strings = []
    offset = strings_offset
    (count,) = struct.unpack_from('<I', data, offset)
    offset += 4
    for _ in range(count):
        text, offset = _read_fstring(data, offset)
        if version >= 2:
            offset += 4  # refcount — ใช้เฉพาะตอนเขียนกลับ
        strings.append(text)

    # keys เริ่มที่ offset 25 (magic 16 + version 1 + offset field 8)
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


def unpack_locres(input_file, output_csv):
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return

    print(f"Loading {input_file}...")
    try:
        _version, namespaces = read_locres(input_file)
    except ValueError as e:
        print(f"Failed to read locres file: {e}")
        return

    rows = []
    for ns in namespaces:
        for entry in ns['entries']:
            row_id = f"{ns['name']}::{entry['key']}"
            rows.append([row_id, entry['translation'], "", ""])

    os.makedirs(os.path.dirname(output_csv) if os.path.dirname(output_csv) else '.', exist_ok=True)

    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
        writer.writerows(rows)

    print(f"Successfully unpacked {len(rows)} strings to '{output_csv}'")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python Boltgun_unpacker.py <input.locres> <output.csv>")
        sys.exit(1)

    unpack_locres(sys.argv[1], sys.argv[2])
