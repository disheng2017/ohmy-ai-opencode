# ai_news_pipeline.py
import requests
import feedparser
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List
import json

@dataclass
class NewsItem:
    title: str
    source: str
    url: str
    published: datetime
    content: str
    tags: List[str]
    hot_score: float = 0.0  # 热度评分

class AINewsAggregator:
    def __init__(self):
        self.sources = {
            'arxiv': self.fetch_arxiv,
            'github': self.fetch_github_trending,
            'twitter': self.fetch_twitter_list,
            'huggingface': self.fetch_hf_papers
        }
    
    def fetch_arxiv(self, categories=['cs.AI', 'cs.CL', 'cs.CV', 'cs.LG'], max_results=20):
        """抓取 arXiv 最新论文"""
        papers = []
        for cat in categories:
            url = f"http://export.arxiv.org/api/query?search_query=cat:{cat}&sortBy=submittedDate&max_results={max_results}"
            feed = feedparser.parse(url)
            
            for entry in feed.entries:
                paper = NewsItem(
                    title=entry.title,
                    source=f"arXiv-{cat}",
                    url=entry.link,
                    published=datetime.fromtimestamp(
                        entry.published_parsed.timestamp()
                    ),
                    content=entry.summary[:500],
                    tags=[cat, '论文'],
                    hot_score=self.calc_paper_score(entry)
                )
                papers.append(paper)
        return papers
    
    def fetch_github_trending(self, languages=['Python', 'Jupyter Notebook'], since='daily'):
        """抓取 GitHub Trending（需解析网页或使用第三方 API）"""
        # 使用 github-trending-api 或爬虫
        trending = []
        # 实现抓取逻辑...
        return trending
    
    def fetch_twitter_list(self, list_id='ai-researchers'):
        """抓取 Twitter List 时间线（需 Twitter API v2）"""
        # 使用 tweepy 库
        tweets = []
        # 实现抓取逻辑...
        return tweets
    
    def fetch_hf_papers(self):
        """抓取 Hugging Face Daily Papers"""
        url = "https://huggingface.co/api/daily_papers"
        response = requests.get(url)
        papers = []
        for item in response.json():
            paper = NewsItem(
                title=item['title'],
                source='HuggingFace',
                url=f"https://huggingface.co/papers/{item['paper']['id']}",
                published=datetime.now(),
                content=item.get('summary', ''),
                tags=['HuggingFace', '开源'],
                hot_score=item.get('upvotes', 0)
            )
            papers.append(paper)
        return papers
    
    def calc_paper_score(self, entry):
        """计算论文热度分（基于作者影响力、引用等）"""
        score = 0
        # 知名机构加分
        top_institutions = ['OpenAI', 'Google', 'DeepMind', 'Meta', 'Stanford', 'MIT', '清华', '北大']
        for inst in top_institutions:
            if inst in entry.get('author', ''):
                score += 10
        return score
    
    def aggregate(self, hours=24):
        """聚合所有源，筛选最近 N 小时的内容"""
        all_news = []
        for source_name, fetch_func in self.sources.items():
            try:
                news = fetch_func()
                # 筛选最近内容
                recent = [n for n in news if datetime.now() - n.published < timedelta(hours=hours)]
                all_news.extend(recent)
                print(f"✅ {source_name}: 获取 {len(recent)} 条")
            except Exception as e:
                print(f"❌ {source_name}: 失败 - {e}")
        
        # 按热度排序
        all_news.sort(key=lambda x: x.hot_score, reverse=True)
        return all_news[:10]  # 取 Top 10

# 运行抓取
aggregator = AINewsAggregator()
top_news = aggregator.aggregate(hours=24)