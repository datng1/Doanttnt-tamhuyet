import json
from collections import defaultdict
import os

def process_json_file(filepath):
    # Đọc dữ liệu từ file JSON
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Sắp xếp các bản ghi theo label tăng dần
    data.sort(key=lambda x: x['label'])

    # Tìm tất cả các label duy nhất và gán label mới bắt đầu từ 1
    label_map = {}
    new_label = 1
    for item in data:
        old_label = item['label']
        if old_label not in label_map:
            label_map[old_label] = new_label
            new_label += 1
        item['label'] = label_map[old_label]

    # Ghi dữ liệu đã xử lý lại vào file (ghi đè)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✔ Đã xử lý file: {filepath}. Số label mới: {len(label_map)}")

base_path = 'data'
for folder in os.listdir(base_path):
    folder_path = os.path.join(base_path, folder)
    if os.path.isdir(folder_path):
        filename = f"{folder}_full.json"
        full_path = os.path.join(folder_path, filename)
        if os.path.exists(full_path):
            process_json_file(full_path)
