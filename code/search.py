import pandas as pd
from elasticsearch import Elasticsearch
from getpass import getpass
import hashlib
import json
import os
from datetime import datetime
from tqdm import tqdm
import sys

class User:
    def __init__(self, users_file='users.json'):
        self.users_file = users_file
        self.users = self.load_users()
        self.current_user = None
    
    def load_users(self):
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump({}, f)
        with open(self.users_file, 'r') as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                users = {}
        return users
    
    def save_users(self):
        with open(self.users_file, 'w') as f:
            json.dump(self.users, f)
    
    def hash_password(self, password, salt='random_salt'):
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def register(self):
        print("\n===== 注册 =====")
        while True:
            username = input("请输入用户名: ").strip()
            if username in self.users:
                print("用户名已存在，请选择其他用户名。")
            else:
                break
        while True:
            password = getpass("请输入密码: ")
            password_confirm = getpass("请确认密码: ")
            if password != password_confirm:
                print("密码不匹配，请重新输入。")
            elif not password:
                print("密码不能为空，请重新输入。")
            else:
                break
        hashed_password = self.hash_password(password)
        self.users[username] = hashed_password
        self.save_users()
        print(f"用户 '{username}' 注册成功！")
    
    def login(self):
        print("\n===== 登录 =====")
        username = input("请输入用户名: ").strip()
        if username not in self.users:
            print("用户名不存在。")
            return False
        password = getpass("请输入密码: ")
        hashed_password = self.hash_password(password)
        if hashed_password == self.users[username]:
            print(f"用户 '{username}' 登录成功！")
            self.current_user = username
            return True
        else:
            print("密码错误。")
            return False
    
    def logout(self):
        if self.current_user:
            print(f"用户 '{self.current_user}' 已登出。")
            self.current_user = None

class SearchEngine:
    def __init__(self, es_host='http://localhost:9200', index_name='xxjs'):
        self.es = Elasticsearch([es_host])
        self.index = index_name
        if not self.es.ping():
            print("无法连接到Elasticsearch。请检查ES_HOST配置。")
            exit(1)
        else:
            print("成功连接到Elasticsearch。")
    
    def search_phrase(self, phrase, user=None):
        query = {
            "query": {
                "match_phrase": {
                    "text": {
                        "query": phrase
                    }
                }
            }
        }
        return self.execute_query(query, user)
    
    def search_wildcard(self, wildcard_query, user=None):
        query = {
            "query": {
                "wildcard": {
                    "text": {
                        "value": wildcard_query.lower(),
                        "case_insensitive": True
                    }
                }
            }
        }
        return self.execute_query(query, user)
    
    def execute_query(self, query, user=None):
        # Incorporate pagerank with function_score
        function_score_query = {
            "query": {
                "function_score": {
                    "query": query["query"],
                    "functions": [
                        {
                            "field_value_factor": {
                                "field": "pagerank",
                                "factor": 1,
                                "modifier": "sqrt",
                                "missing": 1
                            }
                        }
                    ],
                    "boost_mode": "multiply"
                }
            }
        }
        if user:
            # Load user history to adjust scoring
            history_terms = self.load_user_history(user)
            if history_terms:
                # Boost documents containing these terms
                function_score_query["query"]["function_score"]["functions"].append({
                    "filter": {
                        "terms": {
                            "text": history_terms
                        }
                    },
                    "weight": 1.5
                })
        try:
            response = self.es.search(index=self.index, body=function_score_query, size=4)
            hits = response['hits']['hits']
            
            if not hits:
                return []
            
            # Extract scores and pagerank for normalization
            scores = [hit['_score'] for hit in hits]
            pageranks = [hit['_source'].get('pagerank', 0) for hit in hits]
            
            # Normalize scores and pageranks with handling of zero variance
            normalized_scores = self.normalize_values(scores)
            normalized_pageranks = self.normalize_values(pageranks)
            
            # Define weights
            TFIDF_WEIGHT = 0.7
            PAGERANK_WEIGHT = 0.3
            
            # Calculate the final score based on weighted normalization
            results = []
            for idx, hit in enumerate(hits):
                source = hit['_source']
                final_score = TFIDF_WEIGHT * normalized_scores[idx] + PAGERANK_WEIGHT * normalized_pageranks[idx]
                results.append({
                    'title': source.get('title', ''),
                    'url': source.get('url', ''),
                    'text': source.get('text', '')[:200],  # snippet
                    'pagerank': source.get('pagerank', 0),
                    'final_score': final_score
                })
            
            # Sort results by the final_score in descending order
            results.sort(key=lambda x: x['final_score'], reverse=True)
            
            return results
        except Exception as e:
            print(f"查询时发生错误: {e}")
            return []
    
    def normalize_values(self, values):
        min_val = min(values)
        max_val = max(values)
        if max_val == min_val:
            # Avoid division by zero; assign all normalized values as 1
            return [1.0 for _ in values]
        else:
            # Shift normalization to avoid zero: map min to 0.1 and max to 1.0
            return [0.1 + 0.9 * (v - min_val) / (max_val - min_val) for v in values]
    
    def load_user_history(self, user, history_file='history.txt'):
        # Read history.txt and extract terms from user's previous queries
        # Assuming history.txt stores lines in format: timestamp | username | query | title | url | snippet
        terms = []
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) >=3 and parts[1].strip() == user:
                        query = parts[2].strip()
                        terms += query.split()
        return list(set(terms))
    
    def log_query(self, user, query, results, history_file='history.txt'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(history_file, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} | {user} | {query}\n")
            for res in results:
                snippet = res['text'].replace('\n', ' ').replace('\r', ' ')[:100]
                f.write(f"{timestamp} | {user} | {res['title']} | {res['url']} | {snippet}\n")
    
    def wildcard_suggest(self, prefix):
        # 使用 Elasticsearch 的 completion suggester
        suggest = {
            "suggest": {
                "simple_phrase": {
                    "prefix": prefix,
                    "completion": {
                        "field": "suggest",
                        "fuzzy": {
                            "fuzziness": "AUTO"
                        },
                        "size": 5
                    }
                }
            }
        }
        try:
            response = self.es.search(index=self.index, body=suggest)
            suggestions = response.get('suggest', {}).get('simple_phrase', [])
            if suggestions:
                options = suggestions[0].get('options', [])
                return [sugg['text'] for sugg in options]
            return []
        except Exception as e:
            print(f"获取建议时发生错误: {e}")
            return []

def display_results(results):
    if not results:
        print("没有找到匹配的文档。")
        return
    print("\n===== 搜索结果 =====")
    for idx, res in enumerate(results, start=1):
        print(f"\nRank {idx}:")
        print(f"Title: {res['title']}")
        print(f"URL: {res['url']}")
        #print(f"Pagerank: {res['pagerank']:.4f}")
        print(f"Final Score: {res['final_score']:.6f}")
        print(f"Snippet: {res['text']}...")
    print("======================")

def main():
    # 配置Elasticsearch主机和索引名称
    ES_HOST = 'http://localhost:9200'   # 替换为你的Elasticsearch主机地址
    INDEX_NAME = 'xxjs'                  # 替换为你的Elasticsearch索引名称
    
    user_system = User()
    search_engine = SearchEngine(es_host=ES_HOST, index_name=INDEX_NAME)
    
    print("\n===== 欢迎使用南开大学搜索引擎 =====")
    while True:
        print("\n请选择操作:")
        print("1. 注册")
        print("2. 登录")
        print("3. 退出")
        choice = input("输入数字选择操作: ").strip()
        
        if choice == '1':
            user_system.register()
        elif choice == '2':
            if user_system.login():
                # 进入搜索循环
                while True:
                    print("\n===== 搜索引擎 =====")
                    print("选择查询类型:")
                    print("1. 短语查询")
                    print("2. 通配查询")
                    print("3. 联想关联（搜索建议）")
                    print("4. 查看查询历史")
                    print("5. 退出登录")
                    sub_choice = input("输入数字选择操作: ").strip()
                    
                    if sub_choice == '1':
                        phrase = input("请输入短语查询: ").strip()
                        if not phrase:
                            print("查询不能为空。")
                            continue
                        results = search_engine.search_phrase(phrase, user=user_system.current_user)
                        display_results(results)
                        search_engine.log_query(user_system.current_user, phrase, results)
                    elif sub_choice == '2':
                        wildcard = input("请输入通配符查询: ").strip()
                        if not wildcard:
                            print("查询不能为空。")
                            continue
                        results = search_engine.search_wildcard(wildcard, user=user_system.current_user)
                        display_results(results)
                        search_engine.log_query(user_system.current_user, wildcard, results)
                    elif sub_choice == '3':
                        prefix = input("请输入查询前缀：").strip()
                        if not prefix:
                            print("前缀不能为空。")
                            continue
                        suggestions = search_engine.wildcard_suggest(prefix)
                        if suggestions:
                            print("\n===== 联想关联（搜索建议） =====")
                            for s in suggestions:
                                print(s)
                            print("======================")
                        else:
                            print("没有找到相关的建议。")
                    elif sub_choice == '4':
                        print("\n===== 查询历史 =====")
                        history_file='history.txt'
                        if not os.path.exists(history_file):
                            print("查询历史为空。")
                        else:
                            with open(history_file, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                            user_history = [line.strip() for line in lines if len(line.strip().split('|'))>=3 and line.strip().split('|')[1].strip() == user_system.current_user]
                            if not user_history:
                                print("查询历史为空。")
                            else:
                                for entry in user_history:
                                    parts = entry.split('|')
                                    if len(parts) >=3:
                                        timestamp, user, query = parts[:3]
                                        if query.strip():
                                            print(f"{timestamp} | {query.strip()}")
                    elif sub_choice == '5':
                        user_system.logout()
                        break
                    else:
                        print("无效的选择，请重新输入。")
            else:
                continue
        elif choice == '3':
            print("退出程序。")
            break
        else:
            print("无效的选择，请重新输入。")

if __name__ == "__main__":
    main()
