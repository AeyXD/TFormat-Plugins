# HANDOVER — TFormat-Plugins

**snapshot:** 2026-11-01 · เสร็จ: docs commit · Phase 0–2 (แผนเดิม) · Phase A (game-tool
contract — manifest 8/8 เกม) · Phase A2 (ฟิลด์ `line_break` ใน contract — omit ทั้งหมด) ·
**Phase S1 (Game Tool "Subtitles" ตาม `../docs/spec-vox-whisper.md` — manifest ครบ 9/9
โฟลเดอร์: 8 เกม + Subtitles)** · รายละเอียดงานเก่าดูใน git log
**สถานะ git:** `main` sync origin · กฎ ⛔ ห้าม agent ทำ PR กลับ upstream เอง (ดู AGENTS.md ข้อ 6)

## บริบท

- repo คลัง plugin ที่ TStudio ดึงใช้สดตอนรัน — สัญญา parser และกฎทั้งหมดดู `AGENTS.md` ประจำ repo
- commit ล่าสุด (โค้ด): Telltale `landb_parser` + Alien: Isolation TXT support
- `AGENTS.md` และ `.handover/` เป็นของ fork — **ห้ามรวมใน PR กลับ upstream**

## งานค้าง / แนวทาง

1. **Phase A (game-tool contract) ตาม `../docs/spec-game-tools.md` เสร็จแล้ว (2026-10-31,
   commit ถัดไปจาก snapshot นี้) — แจ้ง workspace task: manifest ครบ 8/8 เกม**
   (`pack_cmd: null` = 0 เกม — ทุกเกม pack ได้จริง แต่ 3 เกมต้องมีเครื่องมือ .exe บน
   Windows ตาม `notes_th`):
   - **CLI convention ครบทุกเกม** `<input> <output_csv>` / `<original> <csv> <output>`:
     สลับลำดับ arg packer 5 ตัว (Alien/Avowed/Fantasian/Wasteland2/Telltale —
     **breaking change** กับคำสั่งเดิมที่ csv มาก่อน original) · เพิ่ม positional mode
     ให้ lng_tool (คง subcommand เดิม) และ outpost_unpacker/packer (คง flag เดิม,
     `--thai-font` กลายเป็น optional) · สร้าง `Alien_unpacker.py` ใหม่ (โฟลเดอร์
     AlienIsolation เดิมมีแต่ packer) · exit code 0/≥1 + เหตุผลออก stderr ครบทุกตัว
   - **manifest `Game_Extractors/<Game>/tool.json` 8 ไฟล์** — placeholder ใช้เฉพาะชุด
     {input} {output_csv} {original} {csv} {output} · จุดที่ Phase B/C ต้องระวัง (ระบุ
     ใน notes_th แล้ว): Telltale unpack_cmd ใช้ `{output}` เป็น**โฟลเดอร์**ผลแตกไฟล์
     ไม่ใช่ CSV (แล้วเปิด .landb ต่อด้วย landb_parser), Outpost unpack_cmd `{input}`
     เป็น**โฟลเดอร์** en/*.locres
   - **ทดสอบผ่าน 33/33**: manifest validate 8 เกม · round-trip จริงผ่าน CLI 5 เกม
     (Boltgun, Wasteland2, Alien, Fantasian, MetroExodus — แปลไทย 1 แถวแล้ว unpack
     ซ้ำเห็นค่าใหม่, utf-16 คงเดิม) · graceful-failure 3 เกม exe-based (Avowed,
     Outpost, Telltale — rc≠1... rc≥1 + ข้อความ stderr ถูกต้อง; Telltale pack แบบ
     ไม่มี exe ยัง patch .landb ไว้ใน `_patch_tmp` ให้แล้ว exit 1)
   - fixtures ใหม่: `tests/fixtures/{AlienIsolation/sample.TXT (utf-16-le),
     Fantasian/sample_meta.json, Wasteland2/sample.txt (utf-16)}`
   - หมายเหตุ: MetroExodus manifest ชี้ lng_tool (เส้นทาง bypass SDK) —
     MetroExodus_unpacker/packer.py เป็นเส้นทาง SDK เก่า เก็บไว้เพื่ออ้างอิง
1b. **Phase A2 เสร็จ (2026-11-01)** — เพิ่มหัวข้อ "Game Tool contract" ลง AGENTS.md ของ repo:
   คีย์หลักของ `tool.json` + CLI convention + **ฟิลด์ optional `line_break`
   (`zwsp|hairspace|space`)** สำหรับ Thai Wrap โหมด auto ฝั่ง THL (resolution ชั้นแรก)
   พร้อมกติกา ⛔ "เติมเฉพาะค่าที่พิสูจน์จากเกมจริง — ยังไม่พิสูจน์ = omit ห้ามเดาใส่,
   ยืนยันแล้วแก้ commit เดียวจบ" · **tool.json ทั้ง 8 ไฟล์ไม่ถูกแตะ (omit ครบ)** ·
   ตรวจ 33/33 ผ่าน: JSON valid 8 ไฟล์ + ไม่มี line_break หลุดเข้า + manifest structure
   + root parser header + Boltgun round-trip ยังผ่าน · **THL เริ่ม Phase B2 ได้**
   (ย้ำ: ทุกเกมตอนนี้ resolve ไป fallback ตารางนามสกุล — ยังไม่มีค่าจาก manifest เลย)
1c. **Phase S1 เสร็จ (2026-11-01)** — Game Tool "Subtitles" ตาม
   `../docs/spec-vox-whisper.md` · **manifest ครบ 9/9 โฟลเดอร์ (8 เกม + Subtitles)**
   — THL เริ่ม Phase S2 (Whisper ใน TVox) ได้:
   - `Game_Extractors/Subtitles/srt_unpacker.py` — SRT → CSV กลาง · **ID ฝังเวลาครบ
     `srt::<index>::<start_ms>::<end_ms>`** (self-contained deploy กลับได้ ไม่ต้องมี
     _meta.json — แก้จุดอ่อนของ root srt_parser ที่ pack กลับไม่ได้) · หลายบรรทัดรวม
     ด้วยช่องว่าง · รับ CRLF/LF · timestamp ยอมรับทั้ง `,` และ `.`
   - `srt_packer.py` — CSV → SRT: เรียงเลขลำดับใหม่ 1..N ตามเวลาเริ่ม · เวลาเดิมเป๊ะ ms
     · ใช้คอลัมน์ Translation ตรง ๆ (ว่าง = เขียนว่าง + เตือน stderr **ไม่ fallback ไป
     Source**) · รับ `-` แทน original (packer ไม่อ่านต้นฉบับ — เตือนแต่ไม่พังถ้า path
     ไม่มี) · คง ZWSP · เขียน CRLF · ไม่แตะไฟล์ต้นฉบับ
   - `tool.json`: game "Subtitles" · `.srt` · **line_break omit ตามกติกา ⛔**
     · notes_th ระบุชนกับ root srt_parser (ID คนละระบบ) ให้ใช้ผ่านเมนู Game Tool
   - fixture `tests/fixtures/Subtitles/sample.srt` (CRLF · ไทย+อังกฤษ+หลายบรรทัด+
     เวลาข้ามชั่วโมง) · AGENTS.md อัปเดตรายการโฟลเดอร์ (9) + สถานะ line_break
   - ทดสอบ 36/36 ผ่าน: round-trip เวลาตรงทุก ms + เลขใหม่ + ไทยครบ + ZWSP 4 จุด
     คงอยู่ + `-` ได้ + Translation ว่างไม่ fallback + SRT พัง exit≥1 (stderr ไทย) +
     LF-only ได้ + manifest 9/9 + regression (root parser headers + Boltgun round-trip)
2. **แผนแก้ไข Phase 0–6 เดิม**: ✅ 0 ✅ 1 ✅ 2 · ⏳ เหลือ 3–6 (path ฮาร์ดโค้ด (Avowed/
   Outpost manifest ระบุใน notes_th ว่า path ยังฮาร์ดโค้ด — Phase 3 ยังจำเป็น) →
   json deploy-back → ระบบทดสอบ unittest (ควรยกชุดทดสอบ Phase A เข้าไปด้วย) →
   เก็บรายละเอียดรอบคาบ)
3. **merge กลับ upstream** จะทำให้ plugin ชุดใหม่ (Telltale / Alien: Isolation / Fantasian)
   ไปถึงมือผู้ใช้ TStudio จริง — แต่ต้องรอคำสั่งเจ้าของก่อนทำ PR เสมอ (กฎ ⛔ ใน AGENTS.md)
4. ถ้ามี session งาน parser ใหม่: ทำตามสัญญาใน `AGENTS.md` → ทดสอบแบบ `parent_widget=None`
   → commit → อัปเดตไฟล์นี้ตอนจบ session
