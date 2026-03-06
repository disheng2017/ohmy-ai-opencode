# publisher.py
from wechatpy import WeChatClient
from wechatpy.exceptions import WeChatClientException

class WeChatPublisher:
    def __init__(self, appid, appsecret):
        self.client = WeChatClient(appid, appsecret)
    
    def publish_draft(self, article, cover_image_path=None):
        """发布到公众号草稿箱"""
        try:
            # 上传封面图
            if cover_image_path:
                with open(cover_image_path, 'rb') as f:
                    media = self.client.material.add("image", f)
                    thumb_media_id = media['media_id']
            else:
                thumb_media_id = "默认封面素材ID"
            
            # 创建草稿
            draft = self.client.draft.add({
                "articles": [{
                    "title": article['headlines'].split('\n')[0],  # 取第一个标题
                    "content": article['article'],
                    "author": "AI前沿观察",
                    "digest": self.generate_digest(article['article']),
                    "content_source_url": article['source'],
                    "thumb_media_id": thumb_media_id,
                    "need_open_comment": 1,
                    "only_fans_can_comment": 0
                }]
            })
            
            print(f"✅ 草稿创建成功，media_id: {draft['media_id']}")
            return draft
            
        except WeChatClientException as e:
            print(f"❌ 发布失败: {e}")
            return None
    
    def generate_digest(self, content):
        """生成摘要（显示在消息卡片）"""
        # 取前 54 字（微信限制）
        return content.replace('\n', '')[:54] + "..."
    
    def schedule_publish(self, draft_id, publish_time):
        """定时发布"""
        # 使用微信的定时发布接口
        pass

# 发布
publisher = WeChatPublisher('your-appid', 'your-appsecret')
publisher.publish_draft(article, '/path/to/cover.png')