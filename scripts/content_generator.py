# content_generator.py
from openai import OpenAI
import os

class AIContentTeam:
    def __init__(self):
        self.client = OpenAI()
        self.agents = {
            'headline_expert': self.generate_headlines,
            'tech_translator': self.translate_tech,
            'analyst': self.add_analysis,
            'editor': self.polish_article
        }
    
    def generate_headlines(self, news_item):
        """智能体 1：标题专家 - 生成爆款标题"""
        prompt = f"""
        你是资深科技媒体编辑，擅长写吸引眼球的标题。
        
        新闻：{news_item.title}
        来源：{news_item.source}
        内容：{news_item.content[:300]}
        
        生成 5 个标题：
        1. 悬念式（引发好奇）
        2. 数字式（具体数据）
        3. 冲突式（颠覆认知）
        4. 蹭热点式（关联知名产品）
        5. 干货式（强调价值）
        
        每个标题 15-25 字，适合微信公众号。
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def translate_tech(self, news_item):
        """智能体 2：技术翻译官 - 把论文/技术转为易懂内容"""
        prompt = f"""
        你是 AI 技术布道者，擅长把复杂技术讲给大众听。
        
        原文：{news_item.title}
        摘要：{news_item.content}
        
        任务：
        1. 用 1 句话概括核心突破
        2. 解释技术原理（类比+图示描述）
        3. 说明为什么重要（行业影响）
        4. 预测未来应用（3 个场景）
        
        风格：像跟朋友聊天，避免术语，适当幽默。
        字数：800-1000 字。
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def add_analysis(self, tech_content, news_item):
        """智能体 3：分析师 - 加入商业/竞争视角"""
        prompt = f"""
        你是科技行业分析师，擅长商业洞察。
        
        技术内容：{tech_content[:500]}
        涉及公司/机构：从标题和来源提取
        
        补充分析：
        1. 这项技术对现有玩家的威胁/机会
        2. 国内是否有对标产品？差距如何？
        3. 投资机会（如果是创业公司）
        4. 潜在风险（技术伦理/监管）
        
        输出 300 字左右，有数据支撑更佳。
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def polish_article(self, headline, tech_part, analysis_part, news_item):
        """智能体 4：编辑 - 整合润色为完整文章"""
        prompt = f"""
        你是微信公众号主编，负责最终成稿。
        
        组件：
        - 标题选项：{headline}
        - 技术解读：{tech_part}
        - 商业分析：{analysis_part}
        
        整合要求：
        1. 选最佳标题作为主标题，其余作小标题
        2. 开头用 Hook（惊人数据/反常识观点/故事）
        3. 中间自然过渡，技术→商业→展望
        4. 结尾引导互动（提问/投票/关注）
        5. 插入 3-5 个 emoji 增加可读性
        6. 全文 1500-2000 字
        
        输出完整 Markdown 格式文章。
        """
        
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def create_article(self, news_item):
        """Sisyphus 调度：协调多智能体完成文章"""
        print(f"🎯 处理：{news_item.title[:50]}...")
        
        # Step 1: 标题
        headlines = self.generate_headlines(news_item)
        print("✅ 标题生成完成")
        
        # Step 2: 技术解读
        tech_content = self.translate_tech(news_item)
        print("✅ 技术解读完成")
        
        # Step 3: 商业分析
        analysis = self.add_analysis(tech_content, news_item)
        print("✅ 商业分析完成")
        
        # Step 4: 整合润色
        final_article = self.polish_article(headlines, tech_content, analysis, news_item)
        print("✅ 文章成稿")
        
        return {
            'headlines': headlines,
            'article': final_article,
            'source': news_item.url,
            'tags': news_item.tags
        }

# 生成文章
team = AIContentTeam()
article = team.create_article(top_news[0])