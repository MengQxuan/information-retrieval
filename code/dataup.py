import pandas as pd
from elasticsearch import Elasticsearch, helpers, exceptions
import os
from tqdm import tqdm
import json

# 配置参数
CSV_FILE_PATH = 'finaloutput.csv'  # CSV文件路径
ES_HOST = 'http://localhost:9200'      # Elasticsearch主机
INDEX_NAME = 'xxjs'                     # Elasticsearch索引名称
CHUNK_SIZE = 1000                       # 每批处理的行数，根据实际情况调整

# 连接Elasticsearch
es = Elasticsearch([ES_HOST])

# 检查Elasticsearch连接
if not es.ping():
    raise ValueError("无法连接到Elasticsearch，请检查ES_HOST配置。")
else:
    print("成功连接到Elasticsearch。")

# 确保索引存在
mapping = {
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "url": {"type": "keyword"},
            "text": {"type": "text"},
            "linksurl": {"type": "keyword"},
            "pagerank": {"type": "float"},
            "suggest": {"type": "completion"}
        }
    }
}

if not es.indices.exists(index=INDEX_NAME):
    es.indices.create(index=INDEX_NAME, body=mapping)
    print(f"索引 '{INDEX_NAME}' 创建成功。")
else:
    print(f"索引 '{INDEX_NAME}' 已存在。")

# 计算总行数以显示进度条
with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
    total_lines = sum(1 for _ in f) - 1  # 减去表头
print(f"总共有 {total_lines} 条数据需要上传。")

# 初始化失败文档列表
failed_documents = []

# 读取CSV并分批上传
chunks = pd.read_csv(CSV_FILE_PATH, chunksize=CHUNK_SIZE, encoding='utf-8')

for chunk in tqdm(chunks, total=total_lines//CHUNK_SIZE + 1, desc="上传进度"):
    # 构建批量操作
    actions = []
    for _, row in chunk.iterrows():
        action = {
            "_index": INDEX_NAME,
            "_source": {
                "title": row.get('title', ''),
                "url": row.get('url', ''),
                "text": row.get('text', ''),
                "linksurl": row.get('linksurl', ''),
                "pagerank": row.get('pagerank', ''),
                "suggest": row.get('suggest', '')
            }
        }
        actions.append(action)
    
    try:
        # 执行批量上传，设置 raise_on_error=False 以捕获错误而不中断
        success, errors = helpers.bulk(es, actions, raise_on_error=False, request_timeout=60)
        
        if errors:
            for error in errors:
                # 提取错误信息
                error_info = error.get('index', {}).get('error', {})
                reason = error_info.get('reason', 'Unknown error')
                failed_doc = error.get('index', {}).get('_source', {})
                failed_documents.append({
                    'document': failed_doc,
                    'error': reason
                })
                print(f"文档上传失败: {reason}")
    
    except exceptions.BulkIndexError as bulk_error:
        # 捕获BulkIndexError并记录详细信息
        for error in bulk_error.errors:
            error_info = error.get('index', {}).get('error', {})
            reason = error_info.get('reason', 'Unknown error')
            failed_doc = error.get('index', {}).get('_source', {})
            failed_documents.append({
                'document': failed_doc,
                'error': reason
            })
            print(f"文档上传失败: {reason}")
    except Exception as e:
        # 捕获其他异常
        print(f"发生异常: {e}")
        continue

# 上传完成后输出结果
print("所有数据已尝试上传到Elasticsearch。")

if failed_documents:
    print(f"共有 {len(failed_documents)} 条文档上传失败。")
    # 将失败的文档及错误原因保存到JSON文件中，便于后续分析
    with open('failed_documents.json', 'w', encoding='utf-8') as f:
        json.dump(failed_documents, f, ensure_ascii=False, indent=2)
    print("失败的文档及错误原因已保存到 'failed_documents.json' 文件中。")
else:
    print("所有文档均成功上传。")
