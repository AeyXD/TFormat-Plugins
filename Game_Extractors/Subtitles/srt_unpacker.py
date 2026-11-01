import os
import sys
import csv
import re

# =====================================================================
# srt_unpacker.py — แตกไฟล์ซับ .srt ออกเป็น CSV กลางของ TStudio
# ID ฝังเวลาครบ srt::<index>::<start_ms>::<end_ms> (ตาม convention
# namespace::key::hash) จึง deploy กลับจาก CSV เดียวได้โดยไม่ต้องมี
# _meta.json — ต่างจาก root srt_parser ที่เก็บเวลาแยกไฟล์ (ไม่ได้แตะตัวนั้น)
# CLI: python srt_unpacker.py <input.srt> <output_csv>
# =====================================================================

_TS_RE = re.compile(r'(\d+):(\d{1,2}):(\d{1,2})[.,](\d{1,3})')


def _ts_to_ms(text):
    """แปลง HH:MM:SS,mmm (หรือจุดแทนลูกน้ำ) เป็นมิลลิวินาที คืน None ถ้าไม่ใช่เวลา"""
    m = _TS_RE.search(text)
    if not m:
        return None
    h, mi, sec = int(m.group(1)), int(m.group(2)), int(m.group(3))
    ms = int(m.group(4).ljust(3, '0'))
    return ((h * 60 + mi) * 60 + sec) * 1000 + ms


def parse_srt_entries(raw):
    """แตก SRT เป็นรายการ (index, start_ms, end_ms, text)
    รับทั้ง CRLF/LF · ข้อความหลายบรรทัดรวมเป็นบรรทัดเดียวด้วยช่องว่าง"""
    entries = []
    blocks = re.split(r'\r?\n\s*\r?\n', raw.strip())
    for block in blocks:
        lines = [l.strip() for l in re.split(r'\r?\n', block) if l.strip()]
        if not lines:
            continue

        # บรรทัดแรกเป็นเลขลำดับ (ถ้ามี) — บรรทัดที่มี --> คือบรรทัดเวลา
        ts_line = 0
        if '-->' not in lines[0]:
            if len(lines) < 2 or '-->' not in lines[1]:
                continue  # ไม่มีบรรทัดเวลา = ไม่ใช่บล็อกซับ
            ts_line = 1

        arrow = lines[ts_line].split('-->')
        if len(arrow) != 2:
            continue
        start_ms = _ts_to_ms(arrow[0])
        end_ms = _ts_to_ms(arrow[1])
        if start_ms is None or end_ms is None:
            continue

        if ts_line == 1 and lines[0].isdigit():
            index = lines[0]
        else:
            index = str(len(entries) + 1)

        text = ' '.join(lines[ts_line + 1:]).strip()
        entries.append((index, start_ms, end_ms, text))

    return entries


def unpack_srt(input_srt, output_csv):
    with open(input_srt, 'r', encoding='utf-8-sig', errors='replace') as f:
        raw = f.read()

    entries = parse_srt_entries(raw)
    if not entries:
        print(f"ไม่พบบล็อกซับที่ถูกต้องใน {input_srt} — ต้องมีบรรทัดเวลาแบบ "
              f"HH:MM:SS,mmm --> HH:MM:SS,mmm อย่างน้อยหนึ่งบล็อก", file=sys.stderr)
        return False

    with open(output_csv, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Source", "Translation", "AI_Reference"])
        for index, start_ms, end_ms, text in entries:
            writer.writerow([f"srt::{index}::{start_ms}::{end_ms}", text, "", ""])

    print(f"Successfully unpacked {len(entries)} subtitle blocks to '{output_csv}'")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python srt_unpacker.py <input.srt> <output_csv>", file=sys.stderr)
        sys.exit(1)

    input_srt = sys.argv[1]
    output_csv = sys.argv[2]

    if not os.path.exists(input_srt):
        print(f"ไม่พบไฟล์: {input_srt}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0 if unpack_srt(input_srt, output_csv) else 1)
