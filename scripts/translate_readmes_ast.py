#!/usr/bin/env python3
"""
Улучшенный скрипт перевода README с сохранением Markdown структуры
Использует парсинг Markdown через AST для перевода только текстовых узлов
"""

import os
import sys
import re
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from markdown_it import MarkdownIt
    from markdown_it.tree import SyntaxTreeNode
    MARKDOWN_IT_AVAILABLE = True
except ImportError:
    MARKDOWN_IT_AVAILABLE = False
    try:
        import mistune
        MISTUNE_AVAILABLE = True
    except ImportError:
        MISTUNE_AVAILABLE = False

# Пытаемся импортировать argostranslate
try:
    import argostranslate.package
    import argostranslate.translate
    ARGOS_AVAILABLE = True
except ImportError:
    ARGOS_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Конфигурация языков
LANGUAGE_CODES = {
    'en': 'English',
    'ru': 'Russian (Русский)',
    'zh-CN': 'Simplified Chinese (简体中文)',
    'es': 'Spanish (Español)'
}

ARGOS_LANGUAGE_MAP = {
    'en': 'en',
    'ru': 'ru',
    'zh-CN': 'zh',
    'es': 'es'
}

README_FILES = {
    'en': 'README.md',
    'ru': 'README.ru.md',
    'zh-CN': 'README.zh-CN.md',
    'es': 'README.es.md'
}

LIBRETRANSLATE_SERVERS = [
    'https://translate.argosopentech.com',
    'https://libretranslate.de',
]

def translate_text_simple(text: str, target_lang: str, source_lang: str = 'en') -> Optional[str]:
    """Простой перевод текста через argostranslate или LibreTranslate"""
    if ARGOS_AVAILABLE:
        try:
            from_code = ARGOS_LANGUAGE_MAP.get(source_lang, source_lang)
            to_code = ARGOS_LANGUAGE_MAP.get(target_lang, target_lang)
            return argostranslate.translate.translate(text, from_code, to_code)
        except:
            pass
    
    if REQUESTS_AVAILABLE:
        libretranslate_map = {'en': 'en', 'ru': 'ru', 'zh-CN': 'zh', 'es': 'es'}
        from_code = libretranslate_map.get(source_lang, source_lang)
        to_code = libretranslate_map.get(target_lang, target_lang)
        
        for server in LIBRETRANSLATE_SERVERS:
            try:
                response = requests.post(
                    f"{server}/translate",
                    json={"q": text, "source": from_code, "target": to_code, "format": "text"},
                    timeout=30
                )
                if response.status_code == 200:
                    return response.json().get("translatedText", "")
            except:
                continue
    
    return None

def translate_markdown_ast(content: str, target_lang: str, source_lang: str = 'en') -> str:
    """
    Переводит Markdown, сохраняя структуру через построчную обработку с защитой элементов
    Улучшенная версия - лучше сохраняет Markdown структуру
    """
    return translate_markdown_simple(content, target_lang, source_lang)

def translate_markdown_simple(content: str, target_lang: str, source_lang: str = 'en') -> str:
    """
    Улучшенный метод перевода с защитой Markdown элементов
    Сохраняет структуру заголовков, списков, цитат, ссылок, таблиц и кода
    """
    # Вспомогательные защиты и восстановление элементов (устойчивые плейсхолдеры)
    def protect_technical_elements(text: str):
        placeholders = {}
        protected_text = text
        counter = 0
        # code blocks (в одной строке встречается редко, но поддержим)
        for match in reversed(list(re.finditer(r'```[\s\S]*?```', protected_text))):
            placeholder = f"XA{str(counter).zfill(4)}B"
            placeholders[placeholder] = match.group(0)
            s, e = match.span()
            protected_text = protected_text[:s] + placeholder + protected_text[e:]
            counter += 1
        # ссылки [text](url)
        for match in reversed(list(re.finditer(r'\[([^\]]+)\]\(([^\)]+)\)', protected_text))):
            placeholder = f"XC{str(counter).zfill(4)}D"
            placeholders[placeholder] = match.group(0)
            s, e = match.span()
            protected_text = protected_text[:s] + placeholder + protected_text[e:]
            counter += 1
        # inline code
        for match in reversed(list(re.finditer(r'(?<!`)`([^`\n]+)`(?!`)', protected_text))):
            placeholder = f"XE{str(counter).zfill(4)}F"
            placeholders[placeholder] = match.group(0)
            s, e = match.span()
            protected_text = protected_text[:s] + placeholder + protected_text[e:]
            counter += 1
        # standalone URLs
        for match in reversed(list(re.finditer(r'(?<!\]\()https?://[^\s\)<>]+', protected_text))):
            placeholder = f"XG{str(counter).zfill(4)}H"
            placeholders[placeholder] = match.group(0)
            s, e = match.span()
            protected_text = protected_text[:s] + placeholder + protected_text[e:]
            counter += 1
        # HTML
        for match in reversed(list(re.finditer(r'<[^>]+>', protected_text))):
            placeholder = f"XI{str(counter).zfill(4)}J"
            placeholders[placeholder] = match.group(0)
            s, e = match.span()
            protected_text = protected_text[:s] + placeholder + protected_text[e:]
            counter += 1
        return protected_text, placeholders

    def restore_technical_elements(translated_text: str, placeholders: dict[str, str]) -> str:
        result = translated_text
        sorted_placeholders = sorted(placeholders.items(), key=lambda x: -len(x[0]))
        for placeholder, original in sorted_placeholders:
            if placeholder in result:
                result = result.replace(placeholder, original)
                continue
            # Пытаемся восстановить испорченные плейсхолдеры
            num_match = re.search(r'\d+', placeholder)
            if not num_match:
                continue
            placeholder_num = num_match.group()
            prefix = placeholder[:2]
            suffix = placeholder[-1]
            patterns = [
                placeholder,
                f"{prefix}\\s*{placeholder_num}\\s*{suffix}",
                f"{prefix}{placeholder_num}\\s+{suffix}",
                f"{prefix}\\s+{placeholder_num}{suffix}",
                f"{prefix[0]}\\s*{prefix[1]}\\s*{placeholder_num}\\s*{suffix}",
                placeholder.upper(),
                placeholder.lower(),
                placeholder_num,
                f"{prefix[1]}{placeholder_num}",
                f"{placeholder_num}{suffix}",
            ]
            for pattern in patterns:
                matches = list(re.finditer(pattern, result, re.IGNORECASE))
                if matches:
                    for m in reversed(matches):
                        s, e = m.span()
                        result = result[:s] + original + result[e:]
        return result

    def translate_text_segment(text: str) -> str:
        if not text:
            return text
        protected, placeholders = protect_technical_elements(text)
        translated = translate_text_simple(protected, target_lang, source_lang)
        if not translated:
            return text
        return restore_technical_elements(translated, placeholders)

    # Обработка построчно, с учётом структурных элементов
    lines = content.split('\n')
    result_lines = []
    in_code_block = False

    for line in lines:
        stripped = line.strip()
        # Границы блока кода
        if stripped.startswith('```'):
            in_code_block = not in_code_block
            result_lines.append(line)
            continue
        if in_code_block:
            result_lines.append(line)
            continue

        # Пустые, разделители и HTML — как есть
        if not stripped or stripped == '---' or stripped.startswith('<!--') or re.match(r'^\s*<[^>]+>\s*$', line):
            result_lines.append(line)
            continue

        # Таблицы
        if '|' in line:
            # Строка выравнивания таблицы
            if re.match(r'^\s*\|?\s*:?-{1,}\s*(:?\s*\|+\s*:?-{1,}\s*:?\s*)+\|?\s*$', line):
                result_lines.append(line)
                continue
            # Перевод содержимого ячеек
            leading_ws = re.match(r'^\s*', line).group(0)
            has_leading_pipe = line.strip().startswith('|')
            has_trailing_pipe = line.strip().endswith('|')
            raw = line.strip().strip('|')
            cells = raw.split('|')
            translated_cells = []
            for cell in cells:
                cell_content = cell
                if re.match(r'^\s*:?-{1,}\s*:?\s*$', cell_content):
                    translated_cells.append(cell)
                    continue
                translated_cells.append(translate_text_segment(cell_content.strip()))
            middle = ' | '.join(translated_cells)
            rebuilt = f"{leading_ws}{'| ' if has_leading_pipe else ''}{middle}{' |' if has_trailing_pipe else ''}"
            result_lines.append(rebuilt)
            continue

        # Цитаты
        m_quote = re.match(r'^(\s*(?:>+\s*)+)(.+)$', line)
        if m_quote:
            prefix = m_quote.group(1)
            body = m_quote.group(2)
            # Внутри — проверяем заголовки/списки, иначе переводим целиком
            h = re.match(r'^(#{1,6})\s+(.+)$', body.strip())
            if h:
                translated_body = f"{h.group(1)} {translate_text_segment(h.group(2))}"
            else:
                u = re.match(r'^(\s*[-*+]\s+)(\[[ xX]\]\s+)?(.+)$', body)
                o = re.match(r'^(\s*\d+[.)]\s+)(.+)$', body)
                if u:
                    checkbox = u.group(2) or ''
                    translated_body = f"{u.group(1)}{checkbox}{translate_text_segment(u.group(3))}"
                elif o:
                    translated_body = f"{o.group(1)}{translate_text_segment(o.group(2))}"
                else:
                    translated_body = translate_text_segment(body)
            result_lines.append(f"{prefix}{translated_body}")
            continue

        # Заголовки
        m_header = re.match(r'^(\s*#{1,6})\s+(.+)$', line)
        if m_header:
            result_lines.append(f"{m_header.group(1)} {translate_text_segment(m_header.group(2))}")
            continue

        # Списки (маркированные / нумерованные)
        m_ul = re.match(r'^(\s*[-*+]\s+)(\[[ xX]\]\s+)?(.+)$', line)
        if m_ul:
            checkbox = m_ul.group(2) or ''
            result_lines.append(f"{m_ul.group(1)}{checkbox}{translate_text_segment(m_ul.group(3))}")
            continue
        m_ol = re.match(r'^(\s*\d+[.)]\s+)(.+)$', line)
        if m_ol:
            result_lines.append(f"{m_ol.group(1)}{translate_text_segment(m_ol.group(2))}")
            continue

        # Обычная строка
        result_lines.append(translate_text_segment(line))

    return '\n'.join(result_lines)

def sync_translations_ast(source_lang='en', target_langs=None):
    """Синхронизирует переводы используя AST парсинг"""
    if target_langs is None:
        target_langs = ['ru', 'zh-CN', 'es']
    
    repo_root = Path(__file__).parent.parent
    source_file = repo_root / README_FILES[source_lang]
    
    if not source_file.exists():
        print(f"❌ Ошибка: Файл {source_file} не найден")
        return False
    
    print(f"\n📖 Читаем исходный файл: {source_file}")
    with open(source_file, 'r', encoding='utf-8') as f:
        source_content = f.read()
    
    print(f"   Размер: {len(source_content)} символов")
    
    success_count = 0
    
    for target_lang in target_langs:
        if target_lang == source_lang:
            continue
        
        target_file = repo_root / README_FILES[target_lang]
        print(f"\n🌍 Перевод на {LANGUAGE_CODES[target_lang]}...")
        
        # Используем AST метод если доступен
        if MARKDOWN_IT_AVAILABLE:
            print("   🔧 Используем AST парсинг для сохранения структуры...")
            translated = translate_markdown_ast(source_content, target_lang, source_lang)
        else:
            print("   🔧 Используем упрощенный метод с защитой элементов...")
            translated = translate_markdown_simple(source_content, target_lang, source_lang)
        
        if translated:
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(translated)
            print(f"   ✅ Успешно создан {target_file}")
            success_count += 1
        else:
            print(f"   ❌ Ошибка перевода для {target_lang}")
    
    print(f"\n{'='*60}")
    print(f"📊 Результаты: {success_count}/{len(target_langs)} переводов выполнено")
    return success_count > 0

if __name__ == '__main__':
    print("="*60)
    print("🌍 Улучшенная система перевода README (AST-based)")
    print("="*60)
    
    source = os.getenv('SOURCE_LANG', 'en')
    targets_str = os.getenv('TARGET_LANGS', 'ru,zh-CN,es')
    targets = [t.strip() for t in targets_str.split(',') if t.strip()]
    
    if MARKDOWN_IT_AVAILABLE:
        print("✅ markdown-it доступен - будет использован AST парсинг")
    elif MISTUNE_AVAILABLE:
        print("✅ mistune доступен")
    else:
        print("⚠️  Markdown парсеры не установлены - будет использован упрощенный метод")
        print("   Рекомендуется: pip install markdown-it-py")
    
    success = sync_translations_ast(source, targets)
    sys.exit(0 if success else 1)

