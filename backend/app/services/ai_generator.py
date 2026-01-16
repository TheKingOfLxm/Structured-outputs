import json
import os
import time
from typing import Dict, List, Optional, Any
from zhipuai import ZhipuAI


class AIGenerator:
    """AI内容生成器 - 使用智谱AI"""

    def __init__(self):
        self.api_key = os.environ.get('ZHIPUAI_API_KEY', '')
        print(f"[DEBUG] 智谱AI API Key: {'已设置' if self.api_key else '未设置'}")
        if self.api_key:
            self.client = ZhipuAI(api_key=self.api_key)
            print(f"[DEBUG] 智谱AI客户端已初始化")
        else:
            self.client = None
            print("警告: 未设置ZHIPUAI_API_KEY环境变量，将使用mock数据")

    def _call_api_with_retry(
        self,
        messages: List[Dict],
        model: str = "glm-4-flash",
        max_retries: int = 3,
        timeout: int = 30
    ) -> str:
        """
        调用智谱AI API，带重试和超时机制

        Args:
            messages: 消息列表
            model: 模型名称
            max_retries: 最大重试次数（默认3次）
            timeout: 超时时间（秒，默认30秒）

        Returns:
            str: API响应内容

        Raises:
            TimeoutError: 超时且重试失败
            ValueError: API调用失败且重试失败
        """
        if not self.client:
            print("[DEBUG] 使用mock数据（client未初始化）")
            # 返回模拟数据用于测试
            return self._get_mock_response(messages)

        print(f"[DEBUG] 调用智谱AI API，模型: {model}")
        last_error = None
        for attempt in range(max_retries):
            try:
                start_time = time.time()

                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2000,
                    timeout=timeout
                )

                elapsed = time.time() - start_time
                print(f"[DEBUG] API调用成功，耗时: {elapsed:.2f}秒")

                return response.choices[0].message.content

            except TimeoutError as e:
                last_error = e
                print(f"[DEBUG] API调用超时 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)  # 等待1秒后重试

            except Exception as e:
                last_error = e
                print(f"[DEBUG] API调用错误 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(1)  # 等待1秒后重试

        # 所有重试都失败，抛出异常或返回mock数据
        if isinstance(last_error, TimeoutError):
            raise TimeoutError(f"API调用超时，已重试{max_retries}次")
        else:
            print(f"[DEBUG] API调用失败，返回mock数据: {str(last_error)}")
            return self._get_mock_response(messages)

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

    def _parse_json_response(self, response: str) -> Any:
        """
        解析JSON响应，处理markdown代码块格式

        Args:
            response: API返回的原始响应

        Returns:
            解析后的Python对象
        """
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0].strip()
        elif "```" in response:
            response = response.split("```")[1].split("```")[0].strip()

        return json.loads(response)

    def _validate_response(self, data: Any, required_fields: List[str]) -> bool:
        """
        验证响应格式是否正确

        Args:
            data: 要验证的数据
            required_fields: 必需字段列表

        Returns:
            bool: 验证是否通过
        """
        if not isinstance(data, dict):
            return False

        for field in required_fields:
            if field not in data:
                return False

        return True

    def _validate_timeline_response(self, data: List[Dict]) -> List[Dict]:
        """
        验证时间线响应格式

        Args:
            data: 时间线数据

        Returns:
            List[Dict]: 验证后的时间线数据
        """
        if not isinstance(data, list):
            return []

        validated = []
        for item in data:
            if isinstance(item, dict):
                # 确保必需字段存在
                validated_item = {
                    "time": item.get("time", ""),
                    "title": item.get("title", ""),
                    "description": item.get("description", ""),
                    "keywords": item.get("keywords", [])
                }
                # 只添加有title的项
                if validated_item["title"]:
                    validated.append(validated_item)

        return validated

    def _validate_mindmap_response(self, data: Dict) -> Dict:
        """
        验证思维导图响应格式

        Args:
            data: 思维导图数据

        Returns:
            Dict: 验证后的思维导图数据
        """
        if not isinstance(data, dict) or "name" not in data:
            return {"name": "论文", "children": []}

        # 确保有children字段
        if "children" not in data:
            data["children"] = []

        return data

    def _validate_graph_response(self, data: Dict, paper_info: Dict) -> Dict:
        """
        验证概念图谱响应格式

        Args:
            data: 概念图谱数据
            paper_info: 论文信息（用于构建默认节点）

        Returns:
            Dict: 验证后的概念图谱数据
        """
        if not isinstance(data, dict):
            return self._build_default_graph(paper_info)

        # 确保必需字段存在
        if "nodes" not in data or not isinstance(data["nodes"], list):
            return self._build_default_graph(paper_info)

        if "links" not in data:
            data["links"] = []

        if "categories" not in data or not isinstance(data["categories"], list):
            data["categories"] = [{"name": "概念"}]

        # 验证和修复节点
        validated_nodes = []
        valid_ids = set()
        for node in data["nodes"]:
            if isinstance(node, dict) and "id" in node and "name" in node:
                node_id = str(node["id"])
                node["id"] = node_id
                valid_ids.add(node_id)

                # 确保有必需字段
                if "category" not in node:
                    node["category"] = 0
                if "symbolSize" not in node:
                    node["symbolSize"] = 50

                validated_nodes.append(node)

        data["nodes"] = validated_nodes

        # 验证和修复链接
        validated_links = []
        for link in data.get("links", []):
            if isinstance(link, dict):
                source = str(link.get("source", ""))
                target = str(link.get("target", ""))

                # 只添加有效的链接
                if source in valid_ids and target in valid_ids:
                    validated_links.append({"source": source, "target": target})

        data["links"] = validated_links

        # 确保至少有一个节点
        if not data["nodes"]:
            return self._build_default_graph(paper_info)

        return data

    def generate_mindmap(self, paper_info: Dict) -> Dict:
        """
        生成思维导图 - 基于章节结构

        Args:
            paper_info: 包含title, abstract, sections等字段的论文信息

        Returns:
            Dict: 思维导图结构，格式为 {"name": "根节点", "children": [...]}
        """
        # 构建包含章节结构的prompt
        prompt = f"""请基于以下论文的完整信息，生成一个思维导图结构的JSON数据。

论文标题: {paper_info.get('title', '')}
作者: {paper_info.get('authors', '')}
摘要: {paper_info.get('abstract', '')}
关键词: {paper_info.get('keywords', '')}
"""

        # 添加章节结构信息
        sections = paper_info.get('sections', '')
        if sections:
            try:
                sections_list = json.loads(sections) if isinstance(sections, str) else sections
                if sections_list:
                    prompt += "\n论文章节结构（请直接使用这些章节作为主要节点）：\n"

                    # 按层级组织章节
                    for section in sections_list:
                        section_title = section.get('title', '')
                        section_number = section.get('number', '')
                        section_level = section.get('level', 1)
                        section_content = section.get('content', '')[:150]

                        # 根据层级添加缩进
                        indent = "  " * (section_level - 1)
                        if section_number:
                            prompt += f"{indent}- {section_number} {section_title}\n"
                        else:
                            prompt += f"{indent}- {section_title}\n"
            except:
                pass

        prompt += """
要求：
1. 返回标准JSON格式
2. 结构为：{"name": "根节点", "children": [{"name": "子节点1", "children": [...]}]}
3. **重点：请基于论文的实际章节结构构建思维导图，保持章节的层级关系**
4. 一级章节作为根节点的直接子节点
5. 二级、三级章节作为对应父章节的子节点
6. 对于每个章节，可以基于其内容提取2-4个关键概念作为子节点
7. 层级深度不超过4层
8. 只返回JSON数据，不要其他说明文字

思维导图数据："""

        messages = [{"role": "user", "content": prompt}]
        response = self._call_api_with_retry(messages)

        try:
            result = self._parse_json_response(response)
            if isinstance(result, dict):
                # 验证思维导图格式
                validated = self._validate_mindmap_response(result)
                return validated
            # 如果解析失败，基于章节构建默认结构
            return self._build_default_mindmap(paper_info)
        except:
            return self._build_default_mindmap(paper_info)

    def _build_default_mindmap(self, paper_info: Dict) -> Dict:
        """基于论文章节构建默认思维导图结构"""
        root_name = paper_info.get('title', '论文')
        if len(root_name) > 30:
            root_name = root_name[:30] + '...'

        children = []
        sections = paper_info.get('sections', '')
        if sections:
            try:
                sections_list = json.loads(sections) if isinstance(sections, str) else sections
                # 按层级和序号排序
                sections_list = sorted(sections_list, key=lambda x: (x.get('level', 1), x.get('number', '')))

                for section in sections_list[:10]:  # 限制数量
                    section_title = section.get('title', '')
                    section_number = section.get('number', '')
                    section_level = section.get('level', 1)

                    # 只显示一级和二级章节
                    if section_level <= 2:
                        display_name = f"{section_number} {section_title}" if section_number else section_title
                        children.append({"name": display_name[:50]})
            except:
                pass

        # 如果没有章节，使用默认结构
        if not children:
            children = [
                {"name": "引言"},
                {"name": "相关工作"},
                {"name": "方法"},
                {"name": "实验"},
                {"name": "结论"}
            ]

        return {"name": root_name, "children": children}

    def generate_timeline(self, paper_info: Dict) -> List[Dict]:
        """
        生成时间线 - 基于论文实际章节内容

        Args:
            paper_info: 包含title, abstract, sections等字段的论文信息

        Returns:
            List[Dict]: 时间线节点列表，每个节点包含time, title, description, keywords
        """
        # 构建包含章节内容的详细prompt
        prompt = f"""请基于以下论文的完整信息，生成一个研究发展时间线的JSON数据。

论文标题: {paper_info.get('title', '')}
作者: {paper_info.get('authors', '')}
摘要: {paper_info.get('abstract', '')}
关键词: {paper_info.get('keywords', '')}

"""

        # 添加章节信息
        sections = paper_info.get('sections', '')
        if sections:
            try:
                sections_list = json.loads(sections) if isinstance(sections, str) else sections
                if sections_list:
                    prompt += "\n论文章节结构：\n"
                    for section in sections_list:
                        section_title = section.get('title', '')
                        section_number = section.get('number', '')
                        section_content = section.get('content', '')[:200]  # 限制长度
                        if section_number:
                            prompt += f"- {section_number} {section_title}: {section_content}\n"
                        else:
                            prompt += f"- {section_title}: {section_content}\n"
            except:
                pass

        prompt += """
要求：
1. 返回标准JSON数组格式
2. 每个节点包含：time（时间，如"2018"或"2020年3月"）, title（标题）, description（描述）, keywords（关键词数组）
3. 时间从早到晚排列
4. **重点：请仔细分析论文的实际内容，特别是相关工作、方法演进等章节，提取论文中提到的真实时间信息和研究发展阶段**
5. 展示该领域的研究发展脉络，包括论文提到的相关工作时间点
6. 只返回JSON数据，不要其他说明文字

时间线数据："""

        messages = [{"role": "user", "content": prompt}]
        response = self._call_api_with_retry(messages)

        try:
            result = self._parse_json_response(response)
            if isinstance(result, list):
                # 验证时间线格式
                validated = self._validate_timeline_response(result)
                return validated
            return []
        except:
            return []

    def generate_graph(self, paper_info: Dict) -> Dict:
        """
        生成概念图谱 - 从章节内容中提取核心概念

        Args:
            paper_info: 包含title, abstract, sections, keywords等字段的论文信息

        Returns:
            Dict: 概念图谱，包含nodes（节点）、links（关系）、categories（类别）
        """
        # 构建包含章节内容的详细prompt
        prompt = f"""请基于以下论文的完整信息，生成一个概念关系图谱的JSON数据。

论文标题: {paper_info.get('title', '')}
作者: {paper_info.get('authors', '')}
摘要: {paper_info.get('abstract', '')}
关键词: {paper_info.get('keywords', '')}
"""

        # 添加章节内容，帮助AI提取核心概念
        sections = paper_info.get('sections', '')
        if sections:
            try:
                sections_list = json.loads(sections) if isinstance(sections, str) else sections
                if sections_list:
                    prompt += "\n主要章节内容：\n"
                    for section in sections_list[:8]:  # 限制数量
                        section_title = section.get('title', '')
                        section_content = section.get('content', '')[:300]
                        prompt += f"- {section_title}: {section_content}\n"
            except:
                pass

        prompt += """
要求：
1. 返回标准JSON格式
2. 包含nodes（节点数组）和links（关系数组）和categories（类别数组）
3. 每个节点必须包含：id（字符串类型，如"0", "1", "2"）, name（节点名称）, category（整数类别编号）, symbolSize（可选，节点大小）
4. 每条关系必须包含：source（字符串类型的源节点id，如"0"）, target（字符串类型的目标节点id，如"1"）
5. categories数组包含各个类别，每个类别有name字段
6. **重点：从论文的实际内容中提取核心概念、方法、技术术语作为节点**
7. 核心概念（如论文主题、主要方法）使用category=0，相关概念使用category=1，细节概念使用category=2
8. 节点数量控制在8-15个之间
9. 只返回JSON数据，不要其他说明文字

示例格式：
{
  "nodes": [{"id": "0", "name": "核心概念", "category": 0, "symbolSize": 70}, {"id": "1", "name": "子概念", "category": 1, "symbolSize": 50}],
  "links": [{"source": "0", "target": "1"}],
  "categories": [{"name": "核心"}, {"name": "相关"}]
}

请生成概念图谱JSON："""

        messages = [{"role": "user", "content": prompt}]
        response = self._call_api_with_retry(messages)

        try:
            result = self._parse_json_response(response)
            if isinstance(result, dict):
                # 验证概念图谱格式
                validated = self._validate_graph_response(result, paper_info)
                return validated
            # 如果解析失败，返回默认结构
            return self._build_default_graph(paper_info)
        except:
            return self._build_default_graph(paper_info)

    def _build_default_graph(self, paper_info: Dict) -> Dict:
        """基于论文信息构建默认概念图谱结构"""
        title = paper_info.get('title', '核心概念')
        if len(title) > 20:
            title = title[:20]

        # 从关键词提取节点
        nodes = [{"id": "0", "name": title, "category": 0, "symbolSize": 70}]
        links = []

        keywords = paper_info.get('keywords', '')
        if keywords:
            try:
                keywords_list = json.loads(keywords) if isinstance(keywords, str) else keywords
                idx = 1
                for kw in keywords_list[:8]:  # 限制数量
                    if isinstance(kw, str) and len(kw) > 1:
                        nodes.append({"id": str(idx), "name": kw[:20], "category": 1, "symbolSize": 40})
                        links.append({"source": "0", "target": str(idx)})
                        idx += 1
            except:
                pass

        # 添加默认节点
        if len(nodes) < 4:
            default_nodes = [
                {"name": "研究方法", "category": 1},
                {"name": "实验结果", "category": 1},
                {"name": "主要贡献", "category": 1}
            ]
            for node_info in default_nodes:
                new_id = str(len(nodes))
                nodes.append({"id": new_id, **node_info, "symbolSize": 40})
                links.append({"source": "0", "target": new_id})

        return {
            "nodes": nodes,
            "links": links,
            "categories": [
                {"name": "核心"},
                {"name": "相关"}
            ]
        }

    def generate_summary(self, paper_info: Dict) -> Dict:
        """生成论文阅读报告（八元组）"""
        prompt = f"""请基于以下论文信息，生成一个结构化的论文阅读报告，必须返回标准JSON格式，包含以下八个字段：

论文标题: {paper_info.get('title', '')}
作者: {paper_info.get('authors', '')}
摘要: {paper_info.get('abstract', '')}

要求输出JSON格式（只返回JSON，不要其他说明）：
{{
  "abstract": "论文摘要概括",
  "keywords": "关键词，用逗号分隔",
  "researchQuestion": "研究问题",
  "method": "研究方法",
  "results": "主要研究结果",
  "discussion": "讨论与分析",
  "innovation": "创新点",
  "technicalIssues": "技术问题或局限性"
}}

请生成论文阅读报告JSON："""

        messages = [{"role": "user", "content": prompt}]
        response = self._call_api_with_retry(messages)

        try:
            # 尝试解析JSON
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            result = json.loads(response)
            # 确保所有字段都存在
            required_fields = ['abstract', 'keywords', 'researchQuestion', 'method', 'results', 'discussion', 'innovation', 'technicalIssues']
            for field in required_fields:
                if field not in result:
                    result[field] = ""
            return result
        except:
            # 如果解析失败，返回默认结构
            return {
                "abstract": paper_info.get('abstract', '')[:200] + "...",
                "keywords": "",
                "researchQuestion": "",
                "method": "",
                "results": "",
                "discussion": "",
                "innovation": "",
                "technicalIssues": ""
            }

    def generate_review(self, paper_info: Dict) -> Dict:
        """
        生成论文评审报告（基于学术要素完整性评分）

        Args:
            paper_info: 包含title, authors, abstract, keywords的论文信息

        Returns:
            Dict: 评审报告，包含各要素的评分和评语
        """
        prompt = f"""请对以下论文进行学术评审，对各个学术要素进行完整性评分（满分10分）。

【论文信息】
标题：{paper_info.get('title', '')}
作者：{paper_info.get('authors', '')}
摘要：{paper_info.get('abstract', '')}
关键词：{paper_info.get('keywords', '')}

【评审要求】
请对以下8个学术要素进行评分和评语（每项0-10分）：
1. title_quality: 标题质量（准确性、简洁性、吸引力）
2. abstract_quality: 摘要质量（完整性、结构化、信息量）
3. keywords_quality: 关键词质量（相关性、覆盖面、专业性）
4. research_clarity: 研究问题清晰度
5. method_rigor: 方法严谨性
6. experiment_validity: 实验有效性
7. result_reliability: 结果可靠性
8. innovation_level: 创新水平

返回JSON格式（只返回JSON）：
{{
  "title_quality": {{"score": 8, "comment": "标题准确描述研究内容"}},
  "abstract_quality": {{"score": 7, "comment": "摘要较完整但缺少具体数据"}},
  "keywords_quality": {{"score": 9, "comment": "关键词覆盖全面"}},
  "research_clarity": {{"score": 8, "comment": "研究问题明确"}},
  "method_rigor": {{"score": 7, "comment": "方法描述较清晰"}},
  "experiment_validity": {{"score": 8, "comment": "实验设计合理"}},
  "result_reliability": {{"score": 7, "comment": "结果可信度较高"}},
  "innovation_level": {{"score": 8, "comment": "具有一定创新性"}},
  "overall_score": 7.6,
  "overall_comment": "论文整体质量较好，建议补充实验细节",
  "suggestions": ["建议增加对比实验", "建议补充消融实验"]
}}

请生成评审报告JSON："""

        messages = [{"role": "user", "content": prompt}]

        print("[DEBUG] 开始生成评审报告...")
        response = self._call_api_with_retry(messages, timeout=30)

        try:
            result = self._parse_json_response(response)

            if isinstance(result, dict):
                # 确保所有必需字段存在
                required_fields = [
                    'title_quality', 'abstract_quality', 'keywords_quality',
                    'research_clarity', 'method_rigor', 'experiment_validity',
                    'result_reliability', 'innovation_level'
                ]

                for field in required_fields:
                    if field not in result or not isinstance(result[field], dict):
                        result[field] = {'score': 5, 'comment': '未能评估'}
                    elif 'score' not in result[field]:
                        result[field]['score'] = 5
                    elif 'comment' not in result[field]:
                        result[field]['comment'] = ''

                if 'overall_score' not in result:
                    # 计算平均分
                    scores = [result[f]['score'] for f in required_fields]
                    result['overall_score'] = round(sum(scores) / len(scores), 1)

                if 'overall_comment' not in result:
                    result['overall_comment'] = ''

                if 'suggestions' not in result or not isinstance(result['suggestions'], list):
                    result['suggestions'] = []

                print(f"[DEBUG] 评审报告生成完成，总分: {result['overall_score']}")
                return result

            # 返回默认格式
            return {
                'title_quality': {'score': 5, 'comment': '未能评估'},
                'abstract_quality': {'score': 5, 'comment': '未能评估'},
                'keywords_quality': {'score': 5, 'comment': '未能评估'},
                'research_clarity': {'score': 5, 'comment': '未能评估'},
                'method_rigor': {'score': 5, 'comment': '未能评估'},
                'experiment_validity': {'score': 5, 'comment': '未能评估'},
                'result_reliability': {'score': 5, 'comment': '未能评估'},
                'innovation_level': {'score': 5, 'comment': '未能评估'},
                'overall_score': 5.0,
                'overall_comment': '信息不足，无法完整评估',
                'suggestions': []
            }

        except Exception as e:
            print(f"[DEBUG] 解析评审报告失败: {str(e)}")
            # 返回默认格式
            return {
                'title_quality': {'score': 5, 'comment': '评估失败'},
                'abstract_quality': {'score': 5, 'comment': '评估失败'},
                'keywords_quality': {'score': 5, 'comment': '评估失败'},
                'research_clarity': {'score': 5, 'comment': '评估失败'},
                'method_rigor': {'score': 5, 'comment': '评估失败'},
                'experiment_validity': {'score': 5, 'comment': '评估失败'},
                'result_reliability': {'score': 5, 'comment': '评估失败'},
                'innovation_level': {'score': 5, 'comment': '评估失败'},
                'overall_score': 5.0,
                'overall_comment': '评审失败，请稍后重试',
                'suggestions': []
            }

