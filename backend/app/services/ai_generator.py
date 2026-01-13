import json
import os
from typing import Dict, List
from zhipuai import ZhipuAI


class AIGenerator:
    """AI内容生成器 - 使用智谱AI"""

    def __init__(self):
        self.api_key = os.environ.get('ZHIPUAI_API_KEY', '')
        if self.api_key:
            self.client = ZhipuAI(api_key=self.api_key)
        else:
            self.client = None
            print("警告: 未设置ZHIPUAI_API_KEY环境变量")

    def _call_api(self, messages: List[Dict], model: str = "glm-4-flash") -> str:
        """调用智谱AI API"""
        if not self.client:
            # 返回模拟数据用于测试
            return self._get_mock_response(messages)

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"AI API调用错误: {str(e)}")
            return self._get_mock_response(messages)

    def _get_mock_response(self, messages: List[Dict]) -> str:
        """获取模拟响应（用于测试）"""
        user_message = messages[-1].get('content', '')

        if '思维导图' in user_message or 'mindmap' in user_message.lower():
            return json.dumps({
                "name": "论文中心",
                "children": [
                    {
                        "name": "引言",
                        "children": [
                            {"name": "研究背景"},
                            {"name": "研究目的"},
                            {"name": "研究意义"}
                        ]
                    },
                    {
                        "name": "相关工作",
                        "children": [
                            {"name": "传统方法"},
                            {"name": "深度学习方法"},
                            {"name": "本文方法"}
                        ]
                    },
                    {
                        "name": "方法",
                        "children": [
                            {"name": "模型架构"},
                            {"name": "训练策略"},
                            {"name": "优化目标"}
                        ]
                    },
                    {
                        "name": "实验",
                        "children": [
                            {"name": "数据集"},
                            {"name": "评估指标"},
                            {"name": "实验结果"}
                        ]
                    },
                    {
                        "name": "结论",
                        "children": [
                            {"name": "主要贡献"},
                            {"name": "未来工作"}
                        ]
                    }
                ]
            }, ensure_ascii=False)

        elif '时间线' in user_message or 'timeline' in user_message.lower():
            return json.dumps([
                {
                    "time": "2018",
                    "title": "研究起步",
                    "description": "相关领域的初步研究开始",
                    "keywords": ["基础研究", "理论框架"]
                },
                {
                    "time": "2020",
                    "title": "方法突破",
                    "description": "提出新的方法论",
                    "keywords": ["创新方法", "技术突破"]
                },
                {
                    "time": "2022",
                    "title": "应用扩展",
                    "description": "方法在多个领域的应用",
                    "keywords": ["实际应用", "效果验证"]
                },
                {
                    "time": "2024",
                    "title": "最新进展",
                    "description": "本文的最新研究成果",
                    "keywords": ["最新成果", "性能提升"]
                }
            ], ensure_ascii=False)

        elif '概念图谱' in user_message or 'graph' in user_message.lower():
            return json.dumps({
                "nodes": [
                    {"id": "0", "name": "核心概念", "category": 0, "symbolSize": 70},
                    {"id": "1", "name": "理论基础", "category": 1, "symbolSize": 50},
                    {"id": "2", "name": "方法论", "category": 1, "symbolSize": 50},
                    {"id": "3", "name": "实验设计", "category": 1, "symbolSize": 50},
                    {"id": "4", "name": "结果分析", "category": 1, "symbolSize": 50},
                    {"id": "5", "name": "深度学习", "category": 2, "symbolSize": 40},
                    {"id": "6", "name": "数据增强", "category": 2, "symbolSize": 40},
                    {"id": "7", "name": "模型优化", "category": 2, "symbolSize": 40}
                ],
                "links": [
                    {"source": "0", "target": "1"},
                    {"source": "0", "target": "2"},
                    {"source": "0", "target": "3"},
                    {"source": "0", "target": "4"},
                    {"source": "1", "target": "5"},
                    {"source": "2", "target": "6"},
                    {"source": "2", "target": "7"},
                    {"source": "3", "target": "6"},
                    {"source": "4", "target": "7"}
                ],
                "categories": [
                    {"name": "核心"},
                    {"name": "主要"},
                    {"name": "相关"}
                ]
            }, ensure_ascii=False)

        elif '核心观点' in user_message or 'summary' in user_message.lower():
            return """本文的主要贡献和核心观点如下：

1. 研究创新
- 提出了一种新的方法框架
- 解决了现有方法的关键问题
- 在多个任务上取得了性能提升

2. 方法优势
- 计算效率更高
- 泛化能力更强
- 实际应用价值显著

3. 实验验证
- 在标准数据集上进行了充分实验
- 与多种基线方法进行了对比
- 证明了方法的有效性

4. 未来展望
- 可以进一步优化模型结构
- 有望扩展到更多应用场景
- 为后续研究提供了新思路"""

        return "AI生成内容"

    def generate_mindmap(self, paper_info: Dict) -> Dict:
        """生成思维导图"""
        prompt = f"""请基于以下论文信息，生成一个思维导图结构的JSON数据。

论文标题: {paper_info.get('title', '')}
作者: {paper_info.get('authors', '')}
摘要: {paper_info.get('abstract', '')}
关键词: {paper_info.get('keywords', '')}

要求：
1. 返回标准JSON格式
2. 结构为：{{"name": "根节点", "children": [{{"name": "子节点1", "children": [...]}}]}}
3. 根据论文内容提取主要章节和核心概念
4. 层级深度不超过4层
5. 只返回JSON数据，不要其他说明文字

思维导图数据："""

        messages = [{"role": "user", "content": prompt}]
        response = self._call_api(messages)

        try:
            # 尝试解析JSON
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            return json.loads(response)
        except:
            # 如果解析失败，返回默认结构
            return {
                "name": paper_info.get('title', '论文'),
                "children": [
                    {"name": "引言"},
                    {"name": "相关工作"},
                    {"name": "方法"},
                    {"name": "实验"},
                    {"name": "结论"}
                ]
            }

    def generate_timeline(self, paper_info: Dict) -> List[Dict]:
        """生成时间线"""
        prompt = f"""请基于以下论文信息，生成一个研究发展时间线的JSON数据。

论文标题: {paper_info.get('title', '')}
摘要: {paper_info.get('abstract', '')}

要求：
1. 返回标准JSON数组格式
2. 每个节点包含：time（时间）, title（标题）, description（描述）, keywords（关键词数组）
3. 时间从早到晚排列
4. 展示该领域的研究发展脉络
5. 只返回JSON数据，不要其他说明文字

时间线数据："""

        messages = [{"role": "user", "content": prompt}]
        response = self._call_api(messages)

        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            return json.loads(response)
        except:
            return []

    def generate_graph(self, paper_info: Dict) -> Dict:
        """生成概念图谱"""
        prompt = f"""请基于以下论文信息，生成一个概念关系图谱的JSON数据。

论文标题: {paper_info.get('title', '')}
摘要: {paper_info.get('abstract', '')}
关键词: {paper_info.get('keywords', '')}

要求：
1. 返回标准JSON格式
2. 包含nodes（节点数组）和links（关系数组）
3. 每个节点包含：id, name, category（类别编号）
4. 每条关系包含：source（源节点id）, target（目标节点id）
5. 展示论文中的核心概念及其关系
6. 只返回JSON数据，不要其他说明文字

图谱数据："""

        messages = [{"role": "user", "content": prompt}]
        response = self._call_api(messages)

        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            return json.loads(response)
        except:
            return {
                "nodes": [
                    {"id": "0", "name": "核心概念", "category": 0},
                    {"id": "1", "name": "相关概念1", "category": 1},
                    {"id": "2", "name": "相关概念2", "category": 1}
                ],
                "links": [
                    {"source": "0", "target": "1"},
                    {"source": "0", "target": "2"}
                ],
                "categories": [
                    {"name": "核心"},
                    {"name": "相关"}
                ]
            }

    def generate_summary(self, paper_info: Dict) -> str:
        """生成核心观点总结"""
        prompt = f"""请基于以下论文信息，生成一个核心观点总结。

论文标题: {paper_info.get('title', '')}
作者: {paper_info.get('authors', '')}
摘要: {paper_info.get('abstract', '')}

要求：
1. 总结论文的主要贡献和创新点
2. 提炼核心观点
3. 条理清晰，分点说明
4. 字数控制在500字以内

核心观点总结："""

        messages = [{"role": "user", "content": prompt}]
        return self._call_api(messages)
