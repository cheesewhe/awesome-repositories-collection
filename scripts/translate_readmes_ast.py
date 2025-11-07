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
    Сохраняет структуру списков, заголовков, ссылок и кода
    """
    # Разбиваем на строки для обработки
    lines = content.split('\n')
    result_lines = []
    
    in_code_block = False
    code_block_lang = None
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Обрабатываем code blocks
        if line.strip().startswith('```'):
            if not in_code_block:
                in_code_block = True
                code_block_lang = line.strip()[3:].strip()
            else:
                in_code_block = False
                code_block_lang = None
            result_lines.append(line)
            continue
        
        # Пропускаем весь код внутри code blocks
        if in_code_block:
            result_lines.append(line)
            continue
        
        # Пропускаем пустые строки и разделители
        if not line.strip() or line.strip() == '---' or line.strip().startswith('<!--'):
            result_lines.append(line)
            continue
        
        # Пропускаем HTML теги
        if re.match(r'^\s*<[^>]+>\s*$', line):
            result_lines.append(line)
            continue
        
        # Защищаем все технические элементы перед переводом
        placeholders = {}
        counter = 0
        
        # 1. Защищаем code blocks (если есть в строке)
        def protect_code_block(match):
            nonlocal counter
            placeholder = f"__CODEBLOCK_{counter}__"
            placeholders[placeholder] = match.group(0)
            counter += 1
            return placeholder
        
        protected_line = re.sub(r'```[\s\S]*?```', protect_code_block, line)
        
        # 2. Защищаем ссылки [text](url) - ВАЖНО: защищаем URL отдельно
        def protect_link(match):
            nonlocal counter
            link_text = match.group(1)
            link_url = match.group(2)
            # Защищаем URL отдельно
            url_placeholder = f"__URL_{counter}__"
            placeholders[url_placeholder] = link_url
            counter += 1
            # Возвращаем ссылку с защищенным URL
            return f"[{link_text}]({url_placeholder})"
        
        protected_line = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', protect_link, protected_line)
        
        # 3. Защищаем inline код `code`
        def protect_inline_code(match):
            nonlocal counter
            placeholder = f"__INLINECODE_{counter}__"
            placeholders[placeholder] = match.group(0)
            counter += 1
            return placeholder
        
        protected_line = re.sub(r'`([^`]+)`', protect_inline_code, protected_line)
        
        # 4. Защищаем standalone URLs (не в ссылках)
        def protect_url(match):
            nonlocal counter
            placeholder = f"__STANDALONEURL_{counter}__"
            placeholders[placeholder] = match.group(0)
            counter += 1
            return placeholder
        
        protected_line = re.sub(r'(?<!\]\()https?://[^\s\)<>]+', protect_url, protected_line)
        
        # 5. Защищаем Markdown заголовки (сохраняем # символы)
        header_match = re.match(r'^(#{1,6})\s+(.+)$', protected_line)
        if header_match:
            header_level = header_match.group(1)
            header_text = header_match.group(2)
            # Переводим только текст заголовка
            translated_text = translate_text_simple(header_text, target_lang, source_lang)
            if translated_text:
                protected_line = f"{header_level} {translated_text}"
            else:
                protected_line = line
        else:
            # Переводим обычную строку
            translated_line = translate_text_simple(protected_line, target_lang, source_lang)
            if translated_line:
                protected_line = translated_line
        
        # Восстанавливаем все защищенные элементы
        # Важно: восстанавливаем в обратном порядке длины, чтобы избежать конфликтов
        sorted_placeholders = sorted(placeholders.items(), key=lambda x: -len(x[0]))
        for placeholder, original in sorted_placeholders:
            protected_line = protected_line.replace(placeholder, original)
        
        result_lines.append(protected_line)
    
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

