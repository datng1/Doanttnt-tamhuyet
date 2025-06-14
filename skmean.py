import os
import json
import numpy as np
import pandas as pd

def load_data_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def prepare_data_nolabel(data):
    vectors = []
    metadata = []
    for item in data:
        last_point = np.array(list(item['vector'].values()))
        norm = np.linalg.norm(last_point)
        point = last_point / norm if norm > 0 else last_point
        vectors.append(point)
        metadata.append({"title": item["title"]})
    return np.array(vectors), metadata

def run_kmeans(data, n_clusters, n_seed=20, max_iters=300):
    best_inertia = np.inf
    best_clusters = None
    best_centroids = None
    for seed in range(n_seed):
        np.random.seed(seed)
        centroids = data[np.random.choice(len(data), n_clusters, replace=False)]

        for _ in range(max_iters):
            # Tính khoảng cách từ từng điểm tới từng centroid
            distances = np.linalg.norm(data[:, None, :] - centroids[None, :, :], axis=2)
            clusters = np.argmin(distances, axis=1)

            # Đảm bảo không có cụm nào bị rỗng
            for i in range(n_clusters):
                if not np.any(clusters == i):
                    # Gán một điểm ngẫu nhiên vào cụm này
                    rand_idx = np.random.choice(len(data))
                    clusters[rand_idx] = i

            # Cập nhật centroid
            new_centroids = np.array([
                data[clusters == i].mean(axis=0) for i in range(n_clusters)
            ])

            if np.allclose(centroids, new_centroids):
                break
            centroids = new_centroids

        inertia = np.sum((data - centroids[clusters]) ** 2)

        if inertia < best_inertia:
            best_inertia = inertia
            best_clusters = clusters.copy()
            best_centroids = centroids.copy()
        
    return best_clusters, best_centroids


def process_directory(base_dir):
    for folder in os.listdir(base_dir):
        try:
            sub_dir = os.path.join(base_dir, folder)
            if not os.path.isdir(sub_dir):
                continue

            file_path = os.path.join(sub_dir, 'Normalisation.json')
            if not os.path.exists(file_path):
                continue

            print(f"Processing {file_path}...")
            raw_data = load_data_from_json(file_path)
            data, metadata = prepare_data_nolabel(raw_data)

            # Đọc số cụm từ file nếu có
            n_path = os.path.join(sub_dir, "n_clusters.txt")
            if os.path.exists(n_path):
                with open(n_path, "r") as f:
                    n_clusters = int(f.read().strip())
            else:
                n_clusters = 3  # mặc định

            pred_labels, centers = run_kmeans(data, n_clusters)

            # Ghi kết quả ra results.txt
            result_path = os.path.join(sub_dir, 'results.txt')
            with open(result_path, 'w', encoding='utf-8') as f:
                f.write(f"Clusters: {n_clusters}\n\n")
                for cluster_id in range(n_clusters):
                    f.write(f"--- Cluster {cluster_id} ---\n")
                    for meta, label in zip(metadata, pred_labels):
                        if label == cluster_id:
                            f.write(f"Title: {meta['title']}, Cluster: {label}\n")
                f.write("\n")

            rows = []
            for meta, label in zip(metadata, pred_labels):
                rows.append({
                    "Num of Clusters": n_clusters,
                    "Cluster": int(label),
                    "Title": meta['title'],
                })

            df_main = pd.DataFrame(rows)
            excel_path = os.path.join(sub_dir, f'{folder}.xlsx')
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df_main.to_excel(writer, index=False, startrow=0)

            print(f"Excel saved to {excel_path}")
        except Exception as e:
            print(f"Error processing {folder}: {e}")

def process_folder(folder_path):
    try:
        if not os.path.isdir(folder_path):
            print(f"{folder_path} is not a valid directory.")
            return

        file_path = os.path.join(folder_path, 'Normalisation.json')
        if not os.path.exists(file_path):
            print(f"{file_path} not found.")
            return

        print(f"Processing {file_path}...")
        raw_data = load_data_from_json(file_path)
        data, metadata = prepare_data_nolabel(raw_data)

        n_path = os.path.join(folder_path, "n_clusters.txt")
        if os.path.exists(n_path):
            with open(n_path, "r") as f:
                n_clusters = int(f.read().strip())
        else:
            n_clusters = 2

        pred_labels, centers = run_kmeans(data, n_clusters)
        print(f"🧩 Số cụm yêu cầu: {n_clusters}, số cụm không rỗng: {len(set(pred_labels))}")


        result_path = os.path.join(folder_path, 'results.txt')
        with open(result_path, 'w', encoding='utf-8') as f:
            f.write(f"Clusters: {n_clusters}\n\n")
            for cluster_id in range(n_clusters):
                f.write(f"--- Cluster {cluster_id} ---\n")
                for meta, label in zip(metadata, pred_labels):
                    if label == cluster_id:
                        f.write(f"Title: {meta['title']}, Cluster: {label}\n")
            f.write("\n")

        rows = [{
            "Num of Clusters": n_clusters,
            "Cluster": int(label),
            "Title": meta['title']
        } for meta, label in zip(metadata, pred_labels)]

        df_main = pd.DataFrame(rows)
        folder = os.path.basename(folder_path)
        excel_path = os.path.join(folder_path, f'{folder}.xlsx')
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df_main.to_excel(writer, index=False)

        print(f"Excel saved to {excel_path}")
    except Exception as e:
        print(f"Error processing {folder_path}: {e}")
