import os
import csv
import networkx as nx

# 增加字段大小限制
csv.field_size_limit(204857600)  # 1MB，或者更大


# 第一步：计算 PageRank
def compute_pagerank(csv_file_path):
    G = nx.DiGraph()    # 创建有向图

    # 读取 CSV 数据
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            url = row['url']
            links = row['linksurl'].split(';')  # 链接是以分号分隔的
            # 将每个网页与其链接添加到图中
            for link in links:
                link = link.strip()
                if link:  # 确保链接不为空
                    G.add_edge(url, link)

    pagerank = nx.pagerank(G, alpha=0.85)   # 计算 PageRank 值
    return pagerank


# 第二步：更新 CSV 文件
def update_csv_with_pagerank(csv_file_path, pagerank_data):
    updated_rows = []

    # 读取原 CSV 数据并添加 PageRank 列
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames + ['pagerank']  # 添加 PageRank 字段

        for row in reader:
            url = row['url']
            # 获取该 URL 对应的 PageRank 值，若没有该值则设为 0.0
            pr_value = pagerank_data.get(url, 0.0)
            row['pagerank'] = pr_value
            updated_rows.append(row)

    # 确保目录存在
    output_dir = 'pangerankedData'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 定义更新后的文件路径
    updated_csv_file_path = os.path.join(output_dir, 'pangerankedoutput.csv')

    # 将更新后的数据写回到新的 CSV 文件
    with open(updated_csv_file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)

    return updated_csv_file_path


# 第三步：执行完整流程
if __name__ == "__main__":
    # 计算 PageRank
    csv_file_path = "cleanednkuoutput.csv"  # 你的原始 CSV 文件路径
    pagerank_data = compute_pagerank(csv_file_path)

    # 更新 CSV 文件，将 PageRank 数据添加到文件中
    updated_csv_file_path = update_csv_with_pagerank(csv_file_path, pagerank_data)
    print(f"Updated CSV saved at: {updated_csv_file_path}")
