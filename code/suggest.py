import csv
import sys

# 设置最大字段大小
csv.field_size_limit(2**31 - 1)

# 定义生成联想建议的函数
def generate_suggestion(title):
    # 示例：简单的建议生成方法，基于标题返回一部分关键词或与之相关的词
    words = title.split()
    if len(words) > 1:
        return ' '.join(words[:2]) + "..."
    else:
        return words[0] + "..."

# 读取 pagerankedoutput.csv 文件并添加 suggestion 字段
input_file = 'pagerankedoutput.csv'
output_file = 'finaloutput.csv'

# 打开输入文件进行读取，输出文件进行写入
with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    # 清理列名中的 BOM 标记
    reader.fieldnames = [field.replace('\ufeff', '') for field in reader.fieldnames]
    fieldnames = reader.fieldnames + ['suggest']  # 增加新的字段
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)

    writer.writeheader()

    for row in reader:
        # 为每一行数据生成联想建议
        row['suggest'] = generate_suggestion(row['title'])
        writer.writerow(row)

print(f"新的CSV文件已经保存为: {output_file}")
