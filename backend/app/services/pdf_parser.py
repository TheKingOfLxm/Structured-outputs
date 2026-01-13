import json
import re
from typing import Dict, List, Optional
import PyPDF2
import pdfplumber


class PDFParser:
    """PDF解析器"""

    def __init__(self, filepath: str):
        self.filepath = filepath

    def parse(self) -> Dict:
        """
        解析PDF文件，提取元数据和内容

        Returns:
            Dict: 包含title, authors, abstract, keywords, sections等信息的字典
        """
        try:
            # 使用pdfplumber提取文本内容
            with pdfplumber.open(self.filepath) as pdf:
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() or ""

            # 提取元数据
            result = {
                'title': self._extract_title(full_text),
                'authors': self._extract_authors(full_text),
                'abstract': self._extract_abstract(full_text),
                'keywords': self._extract_keywords(full_text),
                'sections': self._extract_sections(full_text),
                'publish_date': self._extract_date(full_text),
                'source': self._extract_source(full_text)
            }

            return result

        except Exception as e:
            print(f"PDF解析错误: {str(e)}")
            return {
                'title': '',
                'authors': '',
                'abstract': '',
                'keywords': '',
                'sections': '',
                'publish_date': '',
                'source': ''
            }

    def _extract_title(self, text: str) -> str:
        """提取标题"""
        lines = text.split('\n')
        if lines:
            # 通常标题在前几行，取第一行非空内容
            for line in lines[:5]:
                line = line.strip()
                if line and len(line) > 5 and len(line) < 200:
                    # 排除明显不是标题的行
                    if not re.match(r'^\d+\s', line) and '@' not in line:
                        return line
        return "未命名论文"

    def _extract_authors(self, text: str) -> str:
        """提取作者"""
        authors = []

        # 查找包含@的行（通常是邮箱），提取前面的作者名
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if '@' in line:
                # 检查前面几行可能是作者信息
                for j in range(max(0, i - 3), i):
                    name = lines[j].strip()
                    if name and len(name) < 100 and '@' not in name:
                        authors.append(name)
                break

        return json.dumps(authors[:10], ensure_ascii=False)  # 最多返回10个作者

    def _extract_abstract(self, text: str) -> str:
        """提取摘要"""
        # 查找Abstract段落
        abstract_pattern = r'(?:Abstract|摘要|ABSTRACT)[:：]\s*(.*?)(?=\n\s*(?:Keywords?|关键词|1\.|Introduction|引言))'
        match = re.search(abstract_pattern, text, re.DOTALL | re.IGNORECASE)

        if match:
            abstract = match.group(1).strip()
            # 清理多余的空白
            abstract = re.sub(r'\s+', ' ', abstract)
            return abstract[:2000]  # 限制长度

        return ""

    def _extract_keywords(self, text: str) -> str:
        """提取关键词"""
        keywords = []

        # 查找Keywords段落
        keyword_pattern = r'(?:Keywords?|关键词)[:：]\s*(.*?)(?=\n\s*\d+\.|Introduction|引言|$)'
        match = re.search(keyword_pattern, text, re.DOTALL | re.IGNORECASE)

        if match:
            keyword_text = match.group(1).strip()
            # 分割关键词
            keywords = re.split(r'[,;，；、\n]', keyword_text)
            keywords = [k.strip() for k in keywords if k.strip() and len(k.strip()) > 1]

        return json.dumps(keywords[:20], ensure_ascii=False)  # 最多返回20个关键词

    def _extract_sections(self, text: str) -> str:
        """提取章节"""
        sections = []

        # 常见的章节标题模式
        section_patterns = [
            r'^(\d+)\.\s+(.+)$',  # 1. Introduction
            r'^([一二三四五六七八九十]+)[、.]\s*(.+)$',  # 一、引言
            r'^([A-Z][A-Z\s]+)$',  # INTRODUCTION
        ]

        lines = text.split('\n')
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检查是否是章节标题
            is_section = False
            for pattern in section_patterns:
                match = re.match(pattern, line)
                if match:
                    if current_section:
                        sections.append(current_section)

                    current_section = {
                        'title': line,
                        'content': ''
                    }
                    is_section = True
                    break

            if not is_section and current_section:
                # 累积章节内容
                if current_section['content']:
                    current_section['content'] += ' '
                current_section['content'] += line

                # 限制每个章节内容长度
                if len(current_section['content']) > 3000:
                    sections.append(current_section)
                    current_section = None

        if current_section:
            sections.append(current_section)

        # 只返回有内容的章节
        sections = [s for s in sections if len(s['content']) > 50]

        return json.dumps(sections[:20], ensure_ascii=False)  # 最多返回20个章节

    def _extract_date(self, text: str) -> str:
        """提取发布日期"""
        # 查找日期模式
        date_patterns = [
            r'\b(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日\b',
            r'\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b',
            r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        return ""

    def _extract_source(self, text: str) -> str:
        """提取来源（期刊/会议名称）"""
        # 查找常见的期刊/会议模式
        source_patterns = [
            r'Proceedings\s+of\s+([^,\n]+)',
            r'Published\s+in\s+([^,\n]+)',
            r'Journal\s+of\s+([^,\n]+)',
            r'([A-Z][A-Z\s]+Conference)',
        ]

        for pattern in source_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return ""
