import os
import sys
import csv
import json

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

def pack_fantasian_json(original_json, input_csv, output_json=None):
    if not output_json:
        output_json = os.path.splitext(original_json)[0] + "_patched.json"

    print(f"Loading translations from {input_csv}...")
    translations = {}
    with open(input_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        id_col = csv_col(reader, "ID", "id")
        src_col = csv_col(reader, "Source", "original", "Original", "ต้นฉบับ")
        trans_col = csv_col(reader, "Translation", "translation", "คำแปล")
        if not id_col or not trans_col:
            print(f"Error: CSV header ไม่ถูกต้อง (ต้องมี ID และ Translation, พบ: {reader.fieldnames})")
            return False
        for row in reader:
            key = (row.get(id_col) or "").strip()
            translation = (row.get(trans_col) or "").strip()
            source = (row.get(src_col) or "").strip() if src_col else ""
            if key:
                translations[key] = translation if translation else source
                
    if not translations:
        print("Error: No translations found in CSV.", file=sys.stderr)
        return False

    print(f"Loading JSON bundle {original_json}...")
    with open(original_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    modified_count = 0
    
    if 'original_tree' in data and 'messageDictionary' in data['original_tree']:
        entries = data['original_tree']['messageDictionary'].get('entries', [])
        
        for entry in entries:
            key = entry.get('key', '')
            if key in translations:
                val_dict = entry.get('value', {})
                original_msg = val_dict.get('Message', '')
                new_msg = translations[key]
                
                if original_msg != new_msg:
                    entry['value']['Message'] = new_msg
                    modified_count += 1
    else:
        print("Error: Invalid JSON structure. Missing original_tree or messageDictionary.", file=sys.stderr)
        return False
                    
    if modified_count == 0:
        print("Warning: No strings were replaced. Did the IDs match?")
    else:
        print(f"Replaced {modified_count} strings.")
        print(f"Saving to {output_json}...")
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("Successfully saved!")
        
    return True

if __name__ == '__main__':
    print("--- Fantasian Packer (JSON Mode) ---")
    if len(sys.argv) < 3:
        print("Usage: python Fantasian_packer.py <original_meta.json> <translated.csv> [output_meta.json]", file=sys.stderr)
        sys.exit(1)

    original_json = sys.argv[1]
    input_csv = sys.argv[2]
    output_json = sys.argv[3] if len(sys.argv) > 3 else None

    if not os.path.exists(original_json):
        print(f"File not found: {original_json}", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(input_csv):
        print(f"File not found: {input_csv}", file=sys.stderr)
        sys.exit(1)

    sys.exit(0 if pack_fantasian_json(original_json, input_csv, output_json) else 1)
