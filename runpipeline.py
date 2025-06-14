import os
import json
import module  # Đảm bảo module.py có các hàm được gọi
import traceback

def ensure_format(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        item.setdefault("abstract", "")
        item.setdefault("label", 0)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def run_pipeline(folder):
    folder_path = os.path.join("data", folder)
    raw_path = os.path.join(folder_path, f"{folder}_full.json")
    pre_path = os.path.join(folder_path, f"pre_process_{folder}.json")
    final_path = os.path.join(folder_path, f"data_{folder}.json")

    print(f"🚀 Starting pipeline for {folder}")
    try:
        # Đảm bảo file đầu vào đúng định dạng
        ensure_format(raw_path)

        # 1. Pre-process
        with open(raw_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        output_list = []
        for record in data:
            text = record.get("title", "")
            if record.get("abstract"):
                text += record["abstract"]
            record["abstract"] = module.convert_todict(text)
            output_list.append(record)

        with open(pre_path, "w", encoding="utf-8") as f:
            json.dump(output_list, f, indent=4)
        print("✅ Step 1: Pre-processing done.")

        # 2. TF-IDF
        module.toidfConfer(folder)
        print("✅ Step 2: TF-IDF generated.")

        # 3. Modify pre-processed data
        with open(pre_path, "r", encoding="utf-8") as f:
            pre_data = json.load(f)

        modified_data = [
            module.modify_paper(record, folder) for record in pre_data
        ]

        with open(final_path, "w", encoding="utf-8") as f:
            json.dump(modified_data, f, indent=4)
        print("✅ Step 3: Modified data saved.")

        # 4. Normalisation
        module.normalisation(folder)
        print("✅ Step 4: Normalisation complete.")

        print(f"🎉 Pipeline completed for {folder}\n")

    except Exception:
        print("❌ Lỗi khi chạy pipeline:")
        print(traceback.format_exc())

# if __name__ == "__main__":
#     data_path = "data"
#     folders = [name for name in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, name))]
#     for folder in folders:
#         run_pipeline(folder)
