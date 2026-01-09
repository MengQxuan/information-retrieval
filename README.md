# 南开大学校内搜索引擎 (Nankai University Search Engine)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

一个基于 Elasticsearch 的智能搜索引擎系统，专门用于爬取和搜索南开大学网站内容。该项目实现了网页爬取、PageRank 算法、个性化搜索、用户管理等功能。

*An intelligent search engine system based on Elasticsearch, specifically designed for crawling and searching Nankai University website content. This project implements web crawling, PageRank algorithm, personalized search, user management, and more.*

## 📋 目录 (Table of Contents)

- [功能特性](#功能特性)
- [系统架构](#系统架构)
- [技术栈](#技术栈)
- [前置要求](#前置要求)
- [安装指南](#安装指南)
- [配置说明](#配置说明)
- [使用说明](#使用说明)
- [项目结构](#项目结构)
- [技术细节](#技术细节)
- [贡献指南](#贡献指南)
- [许可证](#许可证)

## ✨ 功能特性 (Features)

### 核心功能
- **🕷️ 智能网页爬虫**: 基于 Scrapy 的分布式网页爬虫，支持深度爬取和并发控制
- **🔍 多种查询方式**:
  - 短语查询 (Phrase Query)
  - 通配符查询 (Wildcard Query)
  - 联想搜索建议 (Auto-suggestion)
- **📊 PageRank 算法**: 基于网页链接关系计算页面重要性
- **👤 用户管理系统**: 支持用户注册、登录和个性化功能
- **📈 个性化搜索**: 基于用户历史记录优化搜索结果
- **💾 搜索历史记录**: 自动记录和管理用户搜索历史
- **⚡ 高性能索引**: 使用 Elasticsearch 实现快速全文检索

### 搜索算法优化
- TF-IDF 权重计算
- PageRank 网页排名
- 个性化结果排序（70% TF-IDF + 30% PageRank）
- 基于用户历史的结果增强

## 🏗️ 系统架构 (System Architecture)

```
┌─────────────────┐
│   用户界面      │
│  (CLI Interface)│
└────────┬────────┘
         │
┌────────▼────────┐
│  搜索引擎核心   │
│ (Search Engine) │
├─────────────────┤
│ • 用户管理      │
│ • 查询处理      │
│ • 结果排序      │
└────────┬────────┘
         │
┌────────▼────────┐
│  Elasticsearch  │
│   (索引存储)    │
└────────┬────────┘
         │
┌────────▼────────┐
│   数据处理层    │
├─────────────────┤
│ • 网页爬取      │
│ • PageRank 计算 │
│ • 数据上传      │
└─────────────────┘
```

## 🛠️ 技术栈 (Tech Stack)

- **Python 3.8+**: 主要编程语言
- **Elasticsearch 7.x+**: 全文检索引擎
- **Scrapy**: 网页爬虫框架
- **NetworkX**: 图论和 PageRank 计算
- **Pandas**: 数据处理和分析
- **其他依赖**: tqdm, hashlib, json

## 📦 前置要求 (Prerequisites)

在开始之前，请确保您的系统已安装以下软件：

### 必需软件
1. **Python 3.8 或更高版本**
   ```bash
   python --version  # 检查版本
   ```

2. **Elasticsearch 7.x 或更高版本**
   - 下载地址: https://www.elastic.co/downloads/elasticsearch
   - 确保 Elasticsearch 服务运行在 `http://localhost:9200`

### Python 依赖包
```bash
pip install elasticsearch
pip install scrapy
pip install pandas
pip install networkx
pip install tqdm
```

## 🚀 安装指南 (Installation)

### 1. 克隆仓库
```bash
git clone https://github.com/MengQxuan/information-retrieval.git
cd information-retrieval
```

### 2. 安装依赖
```bash
pip install elasticsearch scrapy pandas networkx tqdm
```

### 3. 启动 Elasticsearch
```bash
# 下载并解压 Elasticsearch
# 在 Elasticsearch 目录下运行:
./bin/elasticsearch  # Linux/Mac
# 或
bin\elasticsearch.bat  # Windows

# 验证 Elasticsearch 是否运行
curl http://localhost:9200
```

### 4. 验证安装
```bash
cd code
python search.py
```

## ⚙️ 配置说明 (Configuration)

### Elasticsearch 配置
在 `code/search.py` 中修改 Elasticsearch 配置：

```python
ES_HOST = 'http://localhost:9200'  # Elasticsearch 主机地址
INDEX_NAME = 'xxjs'                 # 索引名称
```

### 爬虫配置
在 `code/settings.py` 中调整爬虫参数：

```python
DOWNLOAD_DELAY = 0.15              # 下载延迟（秒）
DEPTH_LIMIT = 100                  # 爬取深度限制
CONCURRENT_REQUESTS = 32           # 最大并发请求数
CONCURRENT_REQUESTS_PER_DOMAIN = 16  # 单域并发限制
```

### PageRank 配置
在 `code/pagerank.py` 中修改输入文件：

```python
csv_file_path = "cleanednkuoutput.csv"  # 爬取数据文件路径
```

## 📖 使用说明 (Usage)

### 完整工作流程

#### 步骤 1: 爬取网页数据
```bash
cd code
scrapy crawl nku
# 这将生成 nku_output.csv 文件
```

#### 步骤 2: 计算 PageRank
```bash
python pagerank.py
# 输入: cleanednkuoutput.csv
# 输出: pangerankedData/pangerankedoutput.csv
```

#### 步骤 3: 生成搜索建议
```bash
python suggest.py
# 输入: pagerankedoutput.csv
# 输出: finaloutput.csv
```

#### 步骤 4: 上传数据到 Elasticsearch
```bash
python dataup.py
# 将 finaloutput.csv 上传到 Elasticsearch
```

#### 步骤 5: 使用搜索引擎
```bash
python search.py
```

### 搜索引擎功能

启动搜索引擎后，您可以：

1. **注册新用户**
   - 输入唯一的用户名
   - 设置并确认密码

2. **登录系统**
   - 使用已注册的用户名和密码

3. **执行搜索**
   - **短语查询**: 搜索精确匹配的短语
   - **通配符查询**: 使用 `*` 和 `?` 进行模糊搜索
   - **联想搜索**: 输入前缀获取搜索建议

4. **查看历史记录**
   - 查看个人搜索历史

5. **退出登录**

### 使用示例

```
===== 欢迎使用南开大学搜索引擎 =====
请选择操作:
1. 注册
2. 登录
3. 退出
输入数字选择操作: 2

===== 登录 =====
请输入用户名: testuser
请输入密码: ******
用户 'testuser' 登录成功！

===== 搜索引擎 =====
选择查询类型:
1. 短语查询
2. 通配查询
3. 联想关联（搜索建议）
4. 查看查询历史
5. 退出登录
输入数字选择操作: 1

请输入短语查询: 南开大学

===== 搜索结果 =====
Rank 1:
Title: 南开大学首页
URL: http://www.nankai.edu.cn/
Final Score: 0.856234
Snippet: 南开大学是国内学术底蕴深厚...
```

## 📁 项目结构 (Project Structure)

```
information-retrieval/
│
├── README.md                 # 项目说明文档
├── 说明文档.pdf              # 详细说明文档
│
└── code/                     # 源代码目录
    ├── nku_spider.py         # Scrapy 爬虫实现
    ├── settings.py           # Scrapy 配置文件
    ├── pagerank.py           # PageRank 算法实现
    ├── suggest.py            # 搜索建议生成
    ├── dataup.py             # 数据上传到 Elasticsearch
    ├── search.py             # 搜索引擎主程序
    ├── users.json            # 用户数据存储
    └── history.txt           # 搜索历史记录
```

### 主要模块说明

#### `nku_spider.py` - 网页爬虫
- 使用 Scrapy 框架爬取南开大学网站
- 提取标题、URL、正文内容和链接
- 输出 CSV 格式数据

#### `pagerank.py` - PageRank 计算
- 基于 NetworkX 构建网页链接图
- 计算每个页面的 PageRank 值
- 更新 CSV 数据添加 PageRank 字段

#### `suggest.py` - 搜索建议
- 基于页面标题生成搜索建议
- 为 Elasticsearch 的 completion suggester 准备数据

#### `dataup.py` - 数据上传
- 批量上传数据到 Elasticsearch
- 创建索引和映射
- 错误处理和进度显示

#### `search.py` - 搜索引擎核心
包含以下类和功能：

**User 类**:
- 用户注册和登录
- 密码哈希加密
- 用户状态管理

**SearchEngine 类**:
- 短语查询和通配符查询
- 结果排序（TF-IDF + PageRank）
- 个性化搜索优化
- 搜索历史记录
- 搜索建议功能

## 🔬 技术细节 (Technical Details)

### PageRank 算法
```python
# 使用 NetworkX 计算 PageRank
G = nx.DiGraph()
# 添加网页和链接边
pagerank = nx.pagerank(G, alpha=0.85)
```

### 搜索结果排序
```python
# 综合得分计算
final_score = 0.7 * normalized_tfidf + 0.3 * normalized_pagerank

# 个性化增强
if user_history:
    boost_weight = 1.5  # 历史相关结果提升权重
```

### Elasticsearch 映射
```json
{
  "mappings": {
    "properties": {
      "title": {"type": "text"},
      "url": {"type": "keyword"},
      "text": {"type": "text"},
      "pagerank": {"type": "float"},
      "suggest": {"type": "completion"}
    }
  }
}
```

### 安全性
- 密码使用 SHA-256 哈希加密
- 支持盐值 (salt) 增强安全性
- 用户数据本地存储

## 🤝 贡献指南 (Contributing)

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范
- 遵循 PEP 8 Python 代码规范
- 添加适当的注释和文档
- 确保代码通过测试

## 📝 许可证 (License)

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🔗 相关资源 (Related Resources)

- [Elasticsearch 官方文档](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Scrapy 文档](https://docs.scrapy.org/)
- [NetworkX 文档](https://networkx.org/documentation/stable/)
- [PageRank 算法介绍](https://en.wikipedia.org/wiki/PageRank)
