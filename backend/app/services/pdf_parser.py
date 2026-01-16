import json
import re
import os
import sys
from typing import Dict, List, Optional, Tuple, Callable
import PyPDF2
import pdfplumber
from zhipuai import ZhipuAI


class PDFParser:
    """PDF解析器"""

    def __init__(self, filepath: str):
        self.filepath = filepath

    def _normalize_section_number(self, line: str) -> Tuple[Optional[str], str]:
        """
        规范化章节序号，提取序号和标题

        支持的序号格式：
        - 阿拉伯数字: 1., 1.1, 1.1.1, (1), [1]
        - 罗马数字: I., II., III., IV.
        - 中文数字: 一、二、三、
        - 字母: (a), (b), A., B.

        Args:
            line: 章节标题行

        Returns:
            Tuple[Optional[str], str]: (规范化序号, 纯标题文本)
                                      如果无法识别序号，返回 (None, 原始文本)
        """
        # 阿拉伯数字格式: 1. Introduction, 1.1 Background, 1.1.1 Details
        arabic_dot = r'^(\d+(?:\.\d+)*)\.\s+(.+)$'
        match = re.match(arabic_dot, line)
        if match:
            return match.group(1), match.group(2)

        # 括号阿拉伯数字: (1) Introduction, [1] Introduction
        arabic_paren = r'^[\(\[](\d+)[\]\)]\s*(.+)$'
        match = re.match(arabic_paren, line)
        if match:
            return match.group(1), match.group(2)

        # 罗马数字: I. Introduction, II. Background
        roman_pattern = r'^([IVXLCDM]+)\.\s+(.+)$'
        match = re.match(roman_pattern, line)
        if match:
            # 验证是否是有效的罗马数字
            roman_num = match.group(1)
            if self._is_valid_roman(roman_num):
                return roman_num, match.group(2)

        # 中文数字: 一、引言, 二、背景
        chinese_pattern = r'^([一二三四五六七八九十]+)[、.]\s*(.+)$'
        match = re.match(chinese_pattern, line)
        if match:
            # 转换为阿拉伯数字
            chinese_num = match.group(1)
            arabic_num = self._chinese_to_arabic(chinese_num)
            return str(arabic_num), match.group(2)

        # 全大写字母（可能是章节缩写）: INTRODUCTION, ABSTRACT
        uppercase = r'^([A-Z]{3,})\s*(?:[：:]?\s*(.+))?$'
        match = re.match(uppercase, line)
        if match:
            title = match.group(2) if match.group(2) else match.group(1)
            return match.group(1), title

        # 字母格式: (a) Point A, A. First point
        letter_pattern = r'^[\(\[]?([a-zA-Z])[\]\)]?\.\s*(.+)$'
        match = re.match(letter_pattern, line)
        if match:
            return match.group(1), match.group(2)

        # 无法识别序号格式
        return None, line

    def _is_valid_roman(self, s: str) -> bool:
        """验证是否是有效的罗马数字"""
        roman_numerals = {
            'I': 1, 'V': 5, 'X': 10, 'L': 50,
            'C': 100, 'D': 500, 'M': 1000
        }
        if not s:
            return False

        # 简单验证：只包含有效字符
        for char in s:
            if char not in roman_numerals:
                return False

        # 更严格的验证：检查是否遵循减法规则
        prev_value = 0
        for char in reversed(s):
            value = roman_numerals[char]
            if value < prev_value:
                # 减法情况，检查是否符合规则
                if prev_value > 10 * value:
                    return False
            prev_value = value

        return True

    def _chinese_to_arabic(self, chinese: str) -> int:
        """将中文数字转换为阿拉伯数字"""
        chinese_map = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
        }
        if chinese in chinese_map:
            return chinese_map[chinese]
        # 处理复杂情况如十一、十二等
        if chinese.startswith('十'):
            if len(chinese) == 1:
                return 10
            return 10 + chinese_map.get(chinese[1], 0)
        return 0

    def _detect_section_hierarchy(self, section_number: Optional[str]) -> int:
        """
        根据章节序号判断层级

        层级规则：
        - Level 1: 1, I, 一 (单个数字/罗马数字/中文数字)
        - Level 2: 1.1, 1.a (两个部分)
        - Level 3: 1.1.1, 1.1.a (三个部分)
        - Level 4+: 更多部分

        Args:
            section_number: 规范化后的章节序号

        Returns:
            int: 层级级别 (1-6)
        """
        if not section_number:
            return 1  # 无序号默认为一级

        # 检查是否是点分数字格式 (1, 1.1, 1.1.1)
        if '.' in section_number:
            parts = section_number.split('.')
            # 检查每个部分是否都是数字
            if all(part.isdigit() for part in parts):
                return len(parts)

        # 检查是否是单个数字
        if section_number.isdigit():
            return 1

        # 检查是否是罗马数字 (I, II, III)
        if self._is_valid_roman(section_number):
            return 1

        # 检查是否是单个字母 (a, b, c, A, B, C)
        if len(section_number) == 1 and section_number.isalpha():
            return 2

        # 检查是否是全大写单词 (INTRODUCTION, ABSTRACT)
        if section_number.isupper() and len(section_number) > 2:
            return 1

        # 默认为一级
        return 1

    def _assign_parent_relationships(self, sections: List[Dict]) -> List[Dict]:
        """
        为章节分配父子关系

        根据层级和序号前缀确定父章节

        Args:
            sections: 章节列表，每个包含 number 和 level 字段

        Returns:
            List[Dict]: 添加了 parent 字段的章节列表
        """
        for i, section in enumerate(sections):
            level = section.get('level', 1)
            number = section.get('number', '')

            # 从后向前查找可能的父章节
            parent_index = None
            for j in range(i - 1, -1, -1):
                prev_section = sections[j]
                prev_level = prev_section.get('level', 1)
                prev_number = prev_section.get('number', '')

                # 父章节的层级必须更小
                if prev_level < level:
                    # 对于数字序号，检查前缀匹配
                    if number and prev_number and '.' in number:
                        # 检查当前序号是否以父序号为前缀
                        if number.startswith(prev_number + '.'):
                            parent_index = j
                            break

                    # 如果没有前缀匹配，使用最近的更高层级章节
                    if parent_index is None:
                        parent_index = j
                        break

            section['parent'] = sections[parent_index]['number'] if parent_index is not None else None

        return sections

    def _clean_pdf_text(self, text: str) -> str:
        """
        清理PDF提取的文本，处理常见的编码问题

        Args:
            text: 原始文本

        Returns:
            str: 清理后的文本（保留换行符结构）
        """
        if not text:
            return ""

        # 移除PDF常见的乱码字符（\x00格式的控制字符）
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

        # 移除常见的PDF提取伪影（如连续的特殊字符）
        text = re.sub(r'[\n\r]+', ' ', text)

        # 规范化Unicode字符
        text = text.replace('\u3000', ' ')  # 全角空格转半角
        text = text.replace('\xa0', ' ')    # 不换行空格转普通空格

        # 标准化换行符（保留换行结构！）
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # 移除行首行尾空白，但保留行结构
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # 过滤掉只有特殊字符的行，但保留有内容的行
            if re.search(r'[a-zA-Z0-9\u4e00-\u9fff]', line):
                cleaned_lines.append(line)

        # 用换行符连接行，保留段落结构
        result = '\n'.join(cleaned_lines)

        return result

    def _clean_content(self, content: str) -> str:
        """
        清理章节内容

        功能：
        - 移除多余空白字符（连续空格、多余换行）
        - 规范化Unicode字符
        - 保留必要的格式（段落分隔）

        Args:
            content: 原始内容文本

        Returns:
            str: 清理后的内容
        """
        if not content:
            return ""

        # 规范化Unicode字符（全角转半角等）
        content = content.replace('\u3000', ' ')  # 全角空格转半角
        content = content.replace('\xa0', ' ')    # 不换行空格转普通空格

        # 移除控制字符（保留换行、制表符）
        import unicodedata
        cleaned_chars = []
        for char in content:
            if unicodedata.category(char)[0] != 'C' or char in '\n\t':
                cleaned_chars.append(char)
        content = ''.join(cleaned_chars)

        # 标准化换行符
        content = content.replace('\r\n', '\n').replace('\r', '\n')

        # 移除行首行尾空白
        lines = content.split('\n')
        lines = [line.strip() for line in lines]

        # 移除空行，但保留段落分隔（连续空行变成单个空行）
        cleaned_lines = []
        prev_empty = False
        for line in lines:
            if not line:
                if not prev_empty:
                    cleaned_lines.append('')
                prev_empty = True
            else:
                cleaned_lines.append(line)
                prev_empty = False

        # 重新组合内容，用单个空格连接段落内的行
        result_paragraphs = []
        current_paragraph = []

        for line in cleaned_lines:
            if not line:
                # 空行表示段落结束
                if current_paragraph:
                    result_paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
            else:
                current_paragraph.append(line)

        # 添加最后一个段落
        if current_paragraph:
            result_paragraphs.append(' '.join(current_paragraph))

        # 用双换行连接段落
        result = '\n\n'.join(result_paragraphs)

        # 移除开头和结尾的多余空白
        result = result.strip()

        # 限制内容长度，防止过长
        if len(result) > 5000:
            result = result[:5000] + '...'

        return result

    def parse(self, progress_callback: Optional[Callable[[int, int], None]] = None) -> Dict:
        """
        解析PDF文件，提取元数据和内容

        Args:
            progress_callback: 进度回调函数，参数为 (当前页数, 总页数)

        Returns:
            Dict: 包含title, authors, abstract, keywords, sections等信息的字典
        """
        print(f"[DEBUG] 开始解析PDF: {self.filepath}")
        try:
            # 检查文件大小
            file_size = os.path.getsize(self.filepath)
            max_file_size = 50 * 1024 * 1024  # 50MB

            if file_size > max_file_size:
                print(f"警告: PDF文件过大 ({file_size / 1024 / 1024:.2f}MB)，可能需要较长时间处理")

            # 检查内存使用
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            max_memory = 500 * 1024 * 1024  # 500MB

            if memory_info.rss > max_memory:
                raise MemoryError(f"内存使用过高: {memory_info.rss / 1024 / 1024:.2f}MB")

            # 使用pdfplumber提取文本内容，分批处理
            with pdfplumber.open(self.filepath) as pdf:
                total_pages = len(pdf.pages)
                full_text = ""

                # 分批处理页面
                batch_size = 10
                for i in range(0, total_pages, batch_size):
                    batch_end = min(i + batch_size, total_pages)
                    batch_text = ""

                    for j in range(i, batch_end):
                        page = pdf.pages[j]
                        page_text = page.extract_text()
                        if page_text:
                            # 清理PDF提取的文本，移除乱码字符
                            page_text = self._clean_pdf_text(page_text)
                            batch_text += page_text

                    full_text += batch_text

                    # 调用进度回调
                    if progress_callback:
                        progress_callback(batch_end, total_pages)

                    # 检查内存使用
                    memory_info = process.memory_info()
                    if memory_info.rss > max_memory:
                        raise MemoryError(f"内存使用过高: {memory_info.rss / 1024 / 1024:.2f}MB")

            # 使用AI提取元数据（快速提取，20秒内完成）
            print("[DEBUG] 使用AI快速提取论文信息")
            ai_result = self._extract_with_ai(full_text)

            # 构建结果，使用AI提取的数据
            result = {
                'title': ai_result.get('title', '未命名论文'),
                'authors': ai_result.get('authors', '[]'),
                'abstract': ai_result.get('abstract', ''),
                'keywords': ai_result.get('keywords', '[]'),
                'sections': '[]',  # 章节暂时留空，可后续异步提取或在生成时动态生成
                'publish_date': self._extract_date(full_text),
                'source': self._extract_source(full_text)
            }

            # 调试日志
            try:
                print(f"[DEBUG] PDF解析完成:")
                print(f"[DEBUG]   标题: {len(result.get('title', ''))} 字符")
                if result.get('title'):
                    print(f"[DEBUG]   标题内容: {result.get('title', '')[:50]}")
                print(f"[DEBUG]   作者: {len(result.get('authors', ''))} 字符")
                print(f"[DEBUG]   摘要: {len(result.get('abstract', ''))} 字符")
                print(f"[DEBUG]   关键词: {len(result.get('keywords', ''))} 字符")
                print(f"[DEBUG]   章节: 留空（后续异步提取）")
                print(f"[DEBUG]   原始文本长度: {len(full_text)} 字符")
            except Exception as log_error:
                print(f"[DEBUG] 日志输出错误: {log_error}")

            return result

        except MemoryError as e:
            print(f"PDF解析内存错误: {str(e)}")
            return {
                'title': '',
                'authors': '',
                'abstract': '',
                'keywords': '',
                'sections': '',
                'publish_date': '',
                'source': '',
                'error': f'内存不足: {str(e)}'
            }

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
        if not lines:
            return "未命名论文"

        # 标题通常在前10行，查找最可能是标题的行
        for i, line in enumerate(lines[:10]):
            line = line.strip()
            # 跳过太短或太长的行
            if len(line) < 5 or len(line) > 200:
                continue
            # 跳过明显不是标题的行
            if re.match(r'^\d+[\.\s]', line):  # 以数字开头（如 "1." 或 "1 "）
                continue
            if '@' in line:  # 包含邮箱
                continue
            if line.lower().startswith(('abstract', 'keywords', 'introduction', '摘要', '关键词', '引言')):
                continue
            # 跳过全是数字或特殊字符的行
            if re.match(r'^[\d\s\-+=@#$%^&*()]+$|^[a-zA-Z]{1,2}$', line):
                continue
            # 检查是否包含足够的中英文文字
            if not re.search(r'[a-zA-Z\u4e00-\u9fff]{3,}', line):
                continue
            # 找到合适的标题
            return line

        return "未命名论文"

    def _extract_authors(self, text: str) -> str:
        """提取作者"""
        authors = []
        lines = text.split('\n')

        # 方法1: 查找包含@的行（通常是邮箱），提取前面的作者名
        email_indices = []
        for i, line in enumerate(lines):
            if '@' in line and '.edu' in line:  # 优先查找.edu邮箱
                email_indices.append(i)

        if email_indices:
            # 从第一个邮箱往前查找作者
            for j in range(max(0, email_indices[0] - 5), email_indices[0]):
                line = lines[j].strip()
                if not line:
                    continue
                # 跳过明显不是作者的行
                if line.lower().startswith(('abstract', 'keywords', 'university', 'department')):
                    continue
                if '@' in line:
                    continue
                # 检查是否是合理的作者名（包含字母，长度合理）
                if re.search(r'[a-zA-Z\u4e00-\u9fff]{2,}', line) and len(line) < 100:
                    authors.append(line)

        # 方法2: 查找常见的作者模式
        # 匹配 "Author Name1, Author Name2, Author Name3" 格式
        author_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?[A-Z][a-z]+(?:\s*,\s*[A-Z][a-z]+(?:\s+[A-Z]\.?\s*)?[A-Z][a-z]+)*)',  # 英文名
            r'([\u4e00-\u9fff]{2,4}(?:\s*[,，]\s*[\u4e00-\u9fff]{2,4})*)',  # 中文名
        ]

        for pattern in author_patterns:
            matches = re.findall(pattern, text[:500])  # 只在前500字符中搜索
            for match in matches:
                if match and match not in authors:
                    # 分割作者列表
                    if ',' in match or '，' in match:
                        author_list = re.split(r'[,，]', match)
                        for author in author_list:
                            author = author.strip()
                            if len(author) > 1 and len(author) < 50 and author not in authors:
                                authors.append(author)
                    else:
                        if len(match) > 1 and len(match) < 50:
                            authors.append(match)

        # 去重并限制数量
        seen = set()
        unique_authors = []
        for author in authors:
            author = author.strip()
            if author and author not in seen:
                seen.add(author)
                unique_authors.append(author)
                if len(unique_authors) >= 10:
                    break

        return json.dumps(unique_authors, ensure_ascii=False)

    def _extract_abstract(self, text: str) -> str:
        """提取摘要"""
        # 多种摘要模式
        abstract_patterns = [
            r'(?:Abstract|ABSTRACT)[:：]\s*(.*?)(?=\n\s*(?:Keywords?|关键词|1\.|Introduction|引言|1\s+引言))',
            r'摘要[:：]\s*(.*?)(?=\n\s*(?:Keywords?|关键词|1\.|Introduction|引言|1\s+引言))',
            r'(?:Abstract|摘要|ABSTRACT)[:：]\s*(.*?)(?=\n\s*Keywords?|\n\s*关键词|\n\s*\d+\.|\n\s*Introduction|\n\s*引言)',
        ]

        for pattern in abstract_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                abstract = match.group(1).strip()
                # 清理多余的空白
                abstract = re.sub(r'\s+', ' ', abstract)
                # 移除引用标记如 [1], [2]
                abstract = re.sub(r'\[\d+\]', '', abstract)
                # 限制长度
                if len(abstract) > 50:  # 至少50个字符才算有效摘要
                    return abstract[:2000]

        # 如果没有找到标准格式的摘要，尝试查找包含"摘要"或"Abstract"标题后的段落
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line_lower = line.strip().lower()
            if 'abstract' in line_lower or '摘要' in line_lower:
                # 收集后续几行作为摘要内容
                abstract_lines = []
                for j in range(i + 1, min(i + 20, len(lines))):
                    next_line = lines[j].strip()
                    # 遇到新的章节标题时停止
                    if re.match(r'^\d+[\.\s]|^(Keywords?|关键词|Introduction|引言)', next_line, re.IGNORECASE):
                        break
                    if next_line:
                        abstract_lines.append(next_line)
                if abstract_lines:
                    abstract = ' '.join(abstract_lines)
                    abstract = re.sub(r'\s+', ' ', abstract)
                    if len(abstract) > 50:
                        return abstract[:2000]

        return ""

    def _extract_keywords(self, text: str) -> str:
        """提取关键词"""
        keywords = []

        # 查找Keywords段落 - 更严格的模式
        keyword_patterns = [
            r'(?:Keywords?|关键词)[:：]\s*([^\n]*?)(?=\n\s*\d+\.|\n\s*Introduction|\n\s*引言|$)',
            r'(?:Keywords?|关键词)[:：]\s*(.*?)(?=\n\s*\d+\.|Introduction|引言|$)',
        ]

        for pattern in keyword_patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                keyword_text = match.group(1).strip()
                # 分割关键词
                keywords = re.split(r'[,;，；、\n]', keyword_text)
                keywords = [k.strip() for k in keywords if k.strip() and len(k.strip()) > 1]
                # 过滤掉太长的关键词（可能是误识别的正文内容）
                keywords = [k for k in keywords if len(k) < 30]
                if keywords:
                    break

        # 去重并限制数量
        seen = set()
        unique_keywords = []
        for keyword in keywords:
            if keyword and keyword not in seen:
                seen.add(keyword)
                unique_keywords.append(keyword)
                if len(unique_keywords) >= 10:
                    break

        return json.dumps(unique_keywords, ensure_ascii=False)  # 最多返回10个关键词

    def _extract_sections(self, text: str) -> str:
        """
        提取章节

        集成序号规范化、层级检测和内容清理功能
        返回包含 number, title, content, level, parent 的结构化数据

        Args:
            text: PDF文本内容

        Returns:
            str: JSON格式的章节数组
        """
        sections = []

        # 扩展的章节标题模式 - 更宽松的匹配
        section_patterns = [
            r'^(\d+(?:\.\d+)*)\.\s+(.+)$',  # 1. Introduction, 1.1 Background
            r'^(\d+)\s+(.+)$',  # 1 Introduction (无点号)
            r'^([一二三四五六七八九十]+)[、.]\s*(.+)$',  # 一、引言
            r'^([IVXLCDM]+)\.\s+(.+)$',  # I. Introduction, II. Background
            r'^[\(\[](\d+)[\]\)]\s*(.+)$',  # (1) Introduction, [1] Introduction
            r'^[\(\[]?([a-zA-Z])[\]\)]?\.\s*(.+)$',  # (a) Point A, A. First point
            r'^([A-Z]{3,})\s*(?:[：:]?\s*(.+))?$',  # INTRODUCTION, ABSTRACT:
        ]

        lines = text.split('\n')
        current_section = None
        in_abstract = False

        print(f"[DEBUG] 开始章节提取，总行数: {len(lines)}")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 跳过摘要部分
            line_lower = line.lower()
            if 'abstract' in line_lower or '摘要' in line_lower:
                in_abstract = True
                continue
            if in_abstract:
                if 'keywords' in line_lower or '关键词' in line_lower or 'introduction' in line_lower or '引言' in line_lower:
                    in_abstract = False
                continue

            # 检查是否是章节标题
            is_section = False
            section_number = None
            section_title = None

            for pattern in section_patterns:
                match = re.match(pattern, line)
                if match:
                    # 使用规范化方法处理序号
                    if len(match.groups()) >= 2 and match.group(2):
                        section_number, section_title = self._normalize_section_number(line)
                    else:
                        section_number = match.group(1) if match.group(1) else None
                        section_title = match.group(1) if match.group(1) else line

                    # 验证章节标题是否合理（至少包含一些文字）
                    if section_title and len(section_title) >= 2:
                        is_section = True
                        print(f"[DEBUG] 找到章节: {section_number} {section_title}")
                        break

            if is_section:
                # 保存当前章节（如果有标题就保存，不过滤内容长度）
                if current_section and current_section.get('title'):
                    sections.append(current_section)
                    print(f"[DEBUG] 保存章节: {current_section.get('number')} {current_section.get('title')}, 内容长度: {len(current_section.get('content', ''))}")

                # 创建新章节
                current_section = {
                    'number': section_number,
                    'title': section_title,
                    'content': ''
                }
            elif current_section:
                # 累积章节内容
                if current_section['content']:
                    current_section['content'] += ' '
                current_section['content'] += line

                # 限制每个章节内容长度
                if len(current_section['content']) > 3000:
                    sections.append(current_section)
                    current_section = None

        # 添加最后一个章节（只要有标题就保存）
        if current_section and current_section.get('title'):
            sections.append(current_section)
            print(f"[DEBUG] 保存最后章节: {current_section.get('number')} {current_section.get('title')}, 内容长度: {len(current_section.get('content', ''))}")

        # 如果没有找到任何章节，尝试使用更宽松的方法
        if not sections:
            print("[DEBUG] 未找到标准格式的章节，尝试宽松匹配")
            # 查找所有以数字或中文数字开头的行
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                # 匹配简单的数字开头
                if re.match(r'^\d+[\s\.]', line):
                    parts = re.split(r'^(\d+)[\s\.]\s*', line, maxsplit=1)
                    if len(parts) >= 3:
                        sections.append({
                            'number': parts[1],
                            'title': parts[2],
                            'content': '',
                            'level': 1
                        })
                        print(f"[DEBUG] 宽松匹配章节: {parts[1]} {parts[2]}")

        print(f"[DEBUG] 章节提取完成，共找到 {len(sections)} 个章节")

        # 过滤无效章节：必须有标题
        sections = [s for s in sections if s.get('title') and len(s.get('title', '')) > 1]

        # 为每个章节添加层级和清理内容
        for section in sections:
            # 检测层级
            section['level'] = self._detect_section_hierarchy(section.get('number'))

            # 清理内容
            if 'content' in section:
                section['content'] = self._clean_content(section.get('content', ''))

        # 分配父子关系
        sections = self._assign_parent_relationships(sections)

        # 限制章节数量
        sections = sections[:20]

        print(f"[DEBUG] 最终章节数量: {len(sections)}")

        return json.dumps(sections, ensure_ascii=False)

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

    def _extract_with_ai(self, text: str) -> Dict:
        """
        使用AI快速提取论文元数据（分步提取，20秒内完成）

        策略：
        1. 快速提取标题和作者（只分析前1500字符，5秒内完成）
        2. 提取摘要和关键词（分析前3500字符，10秒内完成）
        3. 章节留空，后续异步提取或在生成时动态生成

        Args:
            text: PDF提取的文本内容

        Returns:
            Dict: 包含title, authors, abstract, keywords的字典
        """
        import time
        api_key = os.environ.get('ZHIPUAI_API_KEY', '')
        if not api_key:
            print("[DEBUG] 未设置ZHIPUAI_API_KEY，跳过AI提取")
            return {}

        client = ZhipuAI(api_key=api_key)
        cleaned_result = {}

        try:
            # ========== 第一步：快速提取标题和作者（5秒） ==========
            start_time = time.time()
            text_sample_1 = text[:1500] if len(text) > 1500 else text

            prompt_1 = f"""提取论文的标题和作者。

文本：
{text_sample_1}

返回JSON：{{"title":"标题","authors":["作者1","作者2"]}}"""

            response_1 = client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt_1}],
                temperature=0.2,
                max_tokens=300,
                timeout=15
            )

            result_1 = json.loads(self._clean_json_response(response_1.choices[0].message.content))

            # 标题
            title = result_1.get('title', '').strip()
            if title and len(title) > 5 and len(title) < 300:
                cleaned_result['title'] = title

            # 作者
            authors = result_1.get('authors', [])
            if isinstance(authors, list):
                valid_authors = []
                for author in authors:
                    author = str(author).strip()
                    if len(author) < 50 and not re.search(r'(Net|CNN|Transformer|ResNet|VGG|模型|算法)', author, re.IGNORECASE):
                        valid_authors.append(author)
                if valid_authors:
                    cleaned_result['authors'] = json.dumps(valid_authors[:10], ensure_ascii=False)

            elapsed_1 = time.time() - start_time
            print(f"[DEBUG] 第一步完成（标题+作者），耗时: {elapsed_1:.1f}秒")

            # ========== 第二步：提取摘要和关键词（10秒） ==========
            start_time = time.time()
            text_sample_2 = text[:3500] if len(text) > 3500 else text

            prompt_2 = f"""提取论文的摘要和关键词。

文本：
{text_sample_2}

返回JSON：{{"abstract":"摘要内容","keywords":["关键词1","关键词2"]}}"""

            response_2 = client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt_2}],
                temperature=0.2,
                max_tokens=800,
                timeout=15
            )

            result_2 = json.loads(self._clean_json_response(response_2.choices[0].message.content))

            # 摘要
            abstract = result_2.get('abstract', '').strip()
            if abstract and len(abstract) > 50:
                abstract = re.sub(r'\s+', ' ', abstract)
                cleaned_result['abstract'] = abstract[:3000]

            # 关键词
            keywords = result_2.get('keywords', [])
            if isinstance(keywords, list):
                valid_keywords = [kw.strip() for kw in keywords if isinstance(kw, str) and len(kw.strip()) < 30 and len(kw.strip()) > 1]
                if valid_keywords:
                    cleaned_result['keywords'] = json.dumps(valid_keywords[:10], ensure_ascii=False)

            elapsed_2 = time.time() - start_time
            print(f"[DEBUG] 第二步完成（摘要+关键词），耗时: {elapsed_2:.1f}秒")

            print(f"[DEBUG] AI快速提取完成，总耗时约: {elapsed_1 + elapsed_2:.1f}秒")
            return cleaned_result

        except Exception as e:
            print(f"[DEBUG] AI提取失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}

    def _clean_json_response(self, response_text: str) -> str:
        """清理AI响应，提取纯JSON"""
        if "```json" in response_text:
            return response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            return response_text.split("```")[1].split("```")[0].strip()
        return response_text.strip()
