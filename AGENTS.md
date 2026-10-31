# AGENTS.md — คู่มือสำหรับ AI agent ที่ทำงานใน repo นี้

> อ่านก่อนแตะโค้ดทุกครั้ง · สถานะงานล่าสุดดู `.handover/HANDOVER.md` · แผนที่ ecosystem ทั้งระบบดู `../docs/architecture.md` (workspace "THub Studio")

## repo นี้คืออะไร

คลัง plugin สาธารณะที่ **TStudio (ใน THub-Launcher) ดึงไปใช้สดตอนรัน** ผ่าน raw.githubusercontent —
การแก้ไฟล์ที่นี่มีผลต่อผู้ใช้ TStudio ทันทีที่ถูก merge ไป upstream (ดูข้อควรรู้ท้ายไฟล์)

- `*_parser.py` (root) — parser รูปแบบไฟล์ทั่วไป: `json` `lang` `landb` `srt` `txt` `vtt`
- `Game_Extractors/` — unpacker/packer เฉพาะเกม 8 เกม (AlienIsolation, Avowed, Boltgun, Fantasian,
  MetroExodus, OutpostInfinitySiege, Telltale, Wasteland2)

## กฎเหล็ก

1. **สัญญา parser** — ทุก parser ต้องมีฟังก์ชัน
   `convert_to_csv(filepath, parent_widget=None)` คืน **absolute path ของ CSV**
   schema `ID, Source, Translation, AI_Reference` (utf-8-sig) · ใช้ `ID` แบบ
   `namespace::key::hash` เพื่อ deploy กลับได้ · เรียกแบบ `parent_widget=None`
   ต้องทำงานได้ (ไม่มี UI ก็ต้องรัน)
2. **ไฟล์เดี่ยว standalone + stdlib เท่านั้น** — แต่ละ parser ถูกดาวน์โหลดแยกจาก cloud
   แล้วรันทันที จึงห้าม import ข้ามไฟล์ parser อื่น และห้ามเพิ่ม dependency ภายนอก
   (ตอนนี้ทั้ง repo ใช้แค่ `csv/json/os/re/struct`)
3. **อย่าทำลายความสามารถ deploy กลับ** — CSV ที่คืนมาต้องแปลงกลับเป็นฟอร์แมตเดิมได้
   (เก็บ meta ที่จำเป็นไว้คู่กัน เช่น `_meta.json` ตาม pattern ของ parser ที่มีอยู่)
4. **fork ↔ upstream** — push ได้เฉพาะ origin (`AeyXD/TFormat-Plugins`) · ส่งกลับ
   `memolyviza2012-max/TFormat-Plugins` ด้วย PR เท่านั้น หลังเจ้าของตัดสินใจ
5. **ขอบเขตการทำงาน** — แตะเฉพาะไฟล์ใน repo นี้ (เอกสาร workspace เป็นของ workspace task) ·
   จบ session ที่กระทบงาน → อัปเดต `.handover/HANDOVER.md` ของ repo นี้
6. **⛔ ส่ง PR กลับ upstream ต้องรอคำสั่งเจ้าของเท่านั้น** — ห้าม agent สร้าง/ส่ง/เตรียม PR
   เองไม่ว่ากรณีใด (สำหรับ GLQA: แม้ upstream จะตอบตกลงใน issue #1 ก็ยังต้องรอคำสั่งก่อนเริ่ม PR แรก)

## ⚠️ ข้อควรรู้ก่อนส่งมอบ

TStudio ดึง plugin จาก URL ของ **upstream** ไม่ใช่ fork — plugin ใหม่ที่ push มาที่นี่
**ยังไม่ถึงมือผู้ใช้ TStudio จนกว่าจะ merge กลับ upstream**

`AGENTS.md` และ `.handover/` เป็นของ **fork เท่านั้น** — ห้ามรวมสองรายการนี้
ใน PR กลับ upstream เด็ดขาด

## ทดสอบ (ไม่ต้องมี UI)

```bash
# parser ต้องรันได้แบบไม่มี parent_widget — ทดสอบด้วยไฟล์ตัวอย่างจริง
python3 -c "
from landb_parser import convert_to_csv
print(convert_to_csv('ตัวอย่าง.landb'))
"
```
