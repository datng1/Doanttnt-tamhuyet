import os
import json
import module  # Đảm bảo module.py có các hàm được gọi

def run_pipeline(folder):
    folder_path = os.path.join("data", folder)
    raw_path = os.path.join(folder_path, f"{folder}_full.json")
    pre_path = os.path.join(folder_path, f"pre_process_{folder}.json")
    final_path = os.path.join(folder_path, f"data_{folder}.json")

    print(f"🚀 Starting pipeline for {folder}")
    try:
        # 1. Pre-process
        with open(raw_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        output_list = []
        for record in data:
            if record.get("abstract") == None:
                record["abstract"] = module.convert_todict(record['title'])
            else:
                record["abstract"] = module.convert_todict(record['title'] + record["abstract"])
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

        modified_data = [module.modify_paper(record, folder) for record in pre_data]

        with open(final_path, "w", encoding="utf-8") as f:
            json.dump(modified_data, f, indent=4)
        print("✅ Step 3: Modified data saved.")

        # 4. Normalisation
        module.normalisation(folder)
        print("✅ Step 4: Normalisation complete.")

        print(f"🎉 Pipeline completed for {folder}\n")
    except Exception as e:
        print(f"{e}")


# if __name__ == "__main__":
#     data_path = "data"
#     folders = [name for name in os.listdir(data_path) if os.path.isdir(os.path.join(data_path, name))]

#     for folder in folders:
#         run_pipeline(folder)
