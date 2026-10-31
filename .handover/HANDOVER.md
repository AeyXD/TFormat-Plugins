# HANDOVER — TFormat-Plugins

**snapshot:** 2026-10-31 · commit `docs:` เพิ่ม AGENTS.md + `.handover/` เข้า repo (fork-only)
พร้อมกฎใหม่ ⛔ ห้าม agent สร้าง/ส่ง/เตรียม PR กลับ upstream เอง — ต้องรอคำสั่งเจ้าของเท่านั้น
**สถานะ git:** `main` sync origin · ไม่มีงานโค้ดค้างใน working tree

## บริบท

- repo คลัง plugin ที่ TStudio ดึงใช้สดตอนรัน — สัญญา parser และกฎทั้งหมดดู `AGENTS.md` ประจำ repo
- commit ล่าสุด (โค้ด): Telltale `landb_parser` + Alien: Isolation TXT support
- `AGENTS.md` และ `.handover/` เป็นของ fork — **ห้ามรวมใน PR กลับ upstream**

## งานค้าง / แนวทาง

1. **แผนแก้ไข Phase 0–6** เสนอและเริ่มทำแล้วใน session 2026-10-31:
   - ✅ **Phase 0 เสร็จ** — เพิ่ม `.gitignore`, ย้ายตัวอย่างทดสอบไป `tests/fixtures/`
     (MetroExodus: stable_us.lng + CSV 4 ไฟล์, Boltgun: test.csv, Outpost: TStudio_Input.csv),
     ลบ `__pycache__/` ทั้ง 5 โฟลเดอร์ + Test_Output.pak + output_sdk.csv,
     smoke test import ผ่าน 18 โมดูล + lng_tool round-trip ผ่าน (188,559 entries)
   - ✅ **Phase 1 เสร็จ (2026-10-31)** — CSV header ทั้ง repo เป็นมาตรฐานเดียว
     `ID, Source, Translation, AI_Reference`: แก้ writer 4 ไฟล์ (json_parser เดิมใช้ header ไทย,
     Avowed_unpacker, MetroExodus_unpacker, lng_tool.to_csv เดิมใช้ lowercase 3 คอลัมน์)
     + reader 7 ไฟล์ให้ tolerant ต่อ header เก่าผ่าน helper `csv_col` (ยอมรับ
     original/translation/ต้นฉบับ/คำแปล) ป้องกัน silent no-op เวลาเจอ CSV เก่าในมือนักแปล —
     ตรวจแล้วว่า TStudio (`is_standard_csv` ใน tstudio_core) ผ่านด่านแบบไม่เด้ง
     SmartImportDialog หลังแก้ · ทดสอบ 24 checks ผ่าน (parser 6 ตัว + lng pack ทั้ง 3 ฟอร์แมต
     + SDK pair + tolerance Thai-header + Telltale patch + migrate) · Boltgun_packer ตรวจด้วย
     py_compile เท่าที่ทำได้บน macOS (pylocres ยังติดตั้งไม่ได้ — จะหมดเรื่องใน Phase 2)
     · เพิ่ม fixture `tests/fixtures/MetroExodus/main_menu_standard.csv` (เก็บ fixture
     ฟอร์แมตเก่าไว้ทดสอบ path tolerance) · พบระหว่างทำ: THub-Launcher สำเนาในเครื่องดึง
     plugin จาก fork (AeyXD) ตรง ๆ และ cache ท้องถิ่นชนะ cloud — rollout ไม่ใช่ทันทีทั้งหมด
   - ⏳ เหลือ Phase 2–6 (ถอด pylocres → path ฮาร์ดโค้ด →
     json deploy-back → ระบบทดสอบ unittest → เก็บรายละเอียดรอบคาบ) — รอเจ้าของสั่งเริ่มต่อ phase ใด
2. **merge กลับ upstream** จะทำให้ plugin ชุดใหม่ (Telltale / Alien: Isolation / Fantasian)
   ไปถึงมือผู้ใช้ TStudio จริง — แต่ต้องรอคำสั่งเจ้าของก่อนทำ PR เสมอ (กฎ ⛔ ใน AGENTS.md)
3. ถ้ามี session งาน parser ใหม่: ทำตามสัญญาใน `AGENTS.md` → ทดสอบแบบ `parent_widget=None`
   → commit → อัปเดตไฟล์นี้ตอนจบ session
