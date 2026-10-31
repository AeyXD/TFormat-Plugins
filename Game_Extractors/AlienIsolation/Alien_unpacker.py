import os
import sys
import csv
import re

# =====================================================================
# Alien_unpacker.py — แตกไฟล์ .TXT ของ Alien: Isolation (รูปแบบ [KEY]{VALUE})
# ออกเป็น CSV กลางของ TStudio — คู่กับ Alien_packer.py
# CLI: python Alien_unpacker.py <input.TXT> <output_csv>
# =====================================================================

def unpack_alien_isolation(input_txt, output_csv):
    # ตรวจ BOM เพื่อเลือก encoding (ไฟล์เกมจริงมักเป็น utf-16-le)
    with open(input_txt, 'rb') as f:
        raw_bytes = f.read(4)

    if raw_bytes.startswith(b'\xff\xfe'):
        encoding = 'utf-16-le'
    elif raw_bytes.startswith(b'\xfe\xff'):
        encoding = 'utf-16-be'
    else:
        encoding = 'utf-8-sig'

    with open(input_txt, 'r', encoding=encoding, errors='replace') as f:
        raw_text = f.read()

    keys = re.findall(r'\[(.*?)\]', raw_text)
    values = re.findall(r'\{(.*?)\}', raw_text, re.DOTALL)

    entries = []
    if len(keys) > 0 and len(keys) == len(values):
        for i in range(len(keys)):
            entries.append((keys[i].strip(), values[i].strip()))

    if not entries:
        print(f"Error: No valid Alien: Isolation texts found in {input_txt}", file=sys.stderr)
        return False

    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
        for key, value in entries:
            writer.writerow([key, value, "", ""])

    print(f"Successfully unpacked {len(entries)} strings to '{output_csv}'")
    return True


if __name__ == "__main__":
    print("--- Alien: Isolation Unpacker ---")
    if len(sys.argv) < 3:
        print("Usage: python Alien_unpacker.py <input.TXT> <output_csv>", file=sys.stderr)
        sys.exit(1)

    input_txt = sys.argv[1]
    output_csv = sys.argv[2]

    if not os.path.exists(input_txt):
        print(f"File not found: {input_txt}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0 if unpack_alien_isolation(input_txt, output_csv) else 1)
