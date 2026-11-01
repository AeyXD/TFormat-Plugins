import os
import sys
import csv
import re

# =====================================================================
# srt_packer.py — รวม CSV กลับเป็นไฟล์ซับ .srt
# อ่านเวลาจาก ID (srt::<index>::<start_ms>::<end_ms>) ทั้งหมด — original
# จึงส่ง '-' ได้ (ไม่มีไฟล์ต้นฉบับ) และเขียนไฟล์ใหม่เสมอ ไม่แตะต้นฉบับ
# ข้อความใช้คอลัมน์ Translation ตรง ๆ (ว่างก็เขียนว่าง + เตือนใน stderr —
# ไม่ fallback ไปใช้ Source) · คง ZWSP ในข้อความตามที่ได้รับ
# CLI: python srt_packer.py <original.srt|-> <input_csv> <output.srt>
# =====================================================================

_ID_RE = re.compile(r'^srt::(\d+)::(\d+)::(\d+)$')


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


def _ms_to_ts(ms):
    """แปลงมิลลิวินาทีเป็น HH:MM:SS,mmm (ms ครบสามหลักเสมอ)"""
    ms = int(ms)
    h, rem = divmod(ms, 3600000)
    mi, rem = divmod(rem, 60000)
    sec, msec = divmod(rem, 1000)
    return f"{h:02d}:{mi:02d}:{sec:02d},{msec:03d}"


def pack_srt(original_srt, input_csv, output_srt):
    # original ไม่ถูกอ่านและไม่ถูกแตะ — เวลาทั้งหมดมาจาก ID ใน CSV
    # (รับไว้เพื่อให้ตรง convention packer <original> <csv> <output>)
    if original_srt != '-' and not os.path.exists(original_srt):
        print(f"คำเตือน: ไม่พบไฟล์ต้นฉบับ {original_srt} — ข้ามไปเลยเพราะ packer ไม่ได้ใช้ไฟล์นี้", file=sys.stderr)

    if not os.path.exists(input_csv):
        print(f"ไม่พบไฟล์ CSV: {input_csv}", file=sys.stderr)
        return False

    entries = []
    empty_count = 0
    skipped = 0
    try:
        with open(input_csv, 'r', encoding='utf-8-sig', errors='replace') as f:
            reader = csv.DictReader(f)
            id_col = csv_col(reader, "ID", "id")
            trans_col = csv_col(reader, "Translation", "translation", "คำแปล")
            if not id_col or not trans_col:
                print(f"CSV header ไม่ถูกต้อง (ต้องมี ID และ Translation, พบ: {reader.fieldnames})", file=sys.stderr)
                return False
            for row in reader:
                row_id = (row.get(id_col) or "").strip()
                text = row.get(trans_col) or ""
                if not text.strip():
                    empty_count += 1
                m = _ID_RE.match(row_id)
                if not m:
                    skipped += 1
                    continue
                # เวลาจาก ID · ข้อความจาก Translation ตรง ๆ (คง ZWSP ตามที่ได้รับ)
                entries.append((int(m.group(2)), int(m.group(3)), text))
    except Exception as e:
        print(f"อ่านไฟล์ CSV ไม่สำเร็จ: {e}", file=sys.stderr)
        return False

    if not entries:
        print(f"ไม่พบแถวที่ ID เป็น srt::<index>::<start_ms>::<end_ms> ใน {input_csv} "
              f"(skipped {skipped} แถว) — ใช้ srt_unpacker.py สร้าง CSV ก่อน", file=sys.stderr)
        return False

    if empty_count:
        print(f"คำเตือน: มี {empty_count} แถวที่คอลัมน์ Translation ว่าง — "
              f"เขียนตาม Translation ตรง ๆ (ไม่ fallback ไปใช้ Source)", file=sys.stderr)
    if skipped:
        print(f"คำเตือน: ข้าม {skipped} แถวที่ ID ไม่ใช่รูปแบบ srt::...", file=sys.stderr)

    # เรียงตามเวลาเริ่ม · เลขลำดับเขียนใหม่ 1..N
    entries.sort(key=lambda e: (e[0], e[1]))

    blocks = []
    for i, (start_ms, end_ms, text) in enumerate(entries, 1):
        blocks.append(f"{i}\r\n{_ms_to_ts(start_ms)} --> {_ms_to_ts(end_ms)}\r\n{text}\r\n")
    data = "\r\n".join(blocks)

    try:
        with open(output_srt, 'w', encoding='utf-8', newline='') as f:
            f.write(data)
    except Exception as e:
        print(f"เขียนไฟล์ SRT ไม่สำเร็จ: {e}", file=sys.stderr)
        return False

    print(f"Successfully packed {len(entries)} subtitle blocks to '{output_srt}'")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python srt_packer.py <original.srt|-> <input_csv> <output.srt>", file=sys.stderr)
        sys.exit(1)

    sys.exit(0 if pack_srt(sys.argv[1], sys.argv[2], sys.argv[3]) else 1)
