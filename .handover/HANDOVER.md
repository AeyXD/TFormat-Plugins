# HANDOVER — TFormat-Plugins

**snapshot:** 2026-10-31 · commit `docs:` เพิ่ม AGENTS.md + `.handover/` เข้า repo (fork-only)
พร้อมกฎใหม่ ⛔ ห้าม agent สร้าง/ส่ง/เตรียม PR กลับ upstream เอง — ต้องรอคำสั่งเจ้าของเท่านั้น
**สถานะ git:** `main` sync origin · ไม่มีงานโค้ดค้างใน working tree

## บริบท

- repo คลัง plugin ที่ TStudio ดึงใช้สดตอนรัน — สัญญา parser และกฎทั้งหมดดู `AGENTS.md` ประจำ repo
- commit ล่าสุด (โค้ด): Telltale `landb_parser` + Alien: Isolation TXT support
- `AGENTS.md` และ `.handover/` เป็นของ fork — **ห้ามรวมใน PR กลับ upstream**

## งานค้าง / แนวทาง

1. **แผนแก้ไข Phase 0–6** เสนอแล้วใน session 2026-10-31 (จัด repo+gitignore → normalize CSV
   header ให้เหลือสัญญาเดียว → ถอด pylocres จาก Boltgun → เอา path ฮาร์ดโค้ดออก →
   ปิดช่อง deploy-back ของ json_parser → ระบบทดสอบ unittest → เก็บรายละเอียดรอบคาบ)
   ยังไม่ได้เริ่มทำ — รอเจ้าของสั่งเริ่ม phase ใด
2. **merge กลับ upstream** จะทำให้ plugin ชุดใหม่ (Telltale / Alien: Isolation / Fantasian)
   ไปถึงมือผู้ใช้ TStudio จริง — แต่ต้องรอคำสั่งเจ้าของก่อนทำ PR เสมอ (กฎ ⛔ ใน AGENTS.md)
3. ถ้ามี session งาน parser ใหม่: ทำตามสัญญาใน `AGENTS.md` → ทดสอบแบบ `parent_widget=None`
   → commit → อัปเดตไฟล์นี้ตอนจบ session
