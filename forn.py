from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from runpipeline import run_pipeline
from skmean import process_directory  # dùng đúng hàm gốc, không thêm hàm mới
from skmean import process_folder

os.makedirs("data", exist_ok=True)
app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    return send_from_directory('.', 'frontend.html')

@app.route("/api/cluster", methods=["POST"])
def cluster():
    file = request.files.get("file")
    raw_n = request.form.get("n_clusters")
    print(f"🧐 raw_n_clusters from form = {raw_n}")
    n_clusters = int(raw_n) if raw_n else 3

    if not file:
        return jsonify({"error": "Không nhận được file"}), 400

    try:
        filename = file.filename
        if not filename.endswith("_full.json"):
            return jsonify({"error": "Tên file phải kết thúc bằng _full.json"}), 400

        folder = filename.replace("_full.json", "")
        folder_path = os.path.join("data", folder)
        os.makedirs(folder_path, exist_ok=True)

        file_path = os.path.join(folder_path, filename)
        file.save(file_path)

        run_pipeline(folder)

        # Monkey patch: tạm ghi số cụm vào file cấu hình
        n_path = os.path.join(folder_path, "n_clusters.txt")
        with open(n_path, "w") as f:
            f.write(str(n_clusters))
        print(f"📦 Đã ghi số cụm vào {n_path}: {n_clusters}")

        process_folder(folder_path)
        
        result_txt = os.path.join(folder_path, "results.txt")
        if not os.path.exists(result_txt):
            return jsonify({"error": "Không tìm thấy kết quả phân cụm"}), 500

        clusters = {}
        with open(result_txt, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("Title:"):
                    parts = line.strip().split(",")
                    title = parts[0].replace("Title: ", "").strip()
                    cluster_str = [p for p in parts if "Cluster:" in p]
                    if cluster_str:
                        cluster_id = int(cluster_str[0].replace("Cluster:", "").strip())
                        clusters.setdefault(cluster_id, []).append({"title": title})

        cluster_list = [clusters[k] for k in sorted(clusters.keys())]
        excel_path = os.path.join(folder_path, f"{folder}.xlsx")

        return jsonify({
            "message": f"✅ Phân cụm thành công ({len(cluster_list)} cụm)",
            "clusters": cluster_list,
            "excel": f"/download/{folder}/{folder}.xlsx"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/download/<folder>/<filename>")
def download_result(folder, filename):
    return send_from_directory(os.path.join("data", folder), filename)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)