import hashlib
"""
辅助工具: 清洗、生成hash
"""

def clean_text(text):
    if not text:
        return ''
    return ' '.join(text.strip().split())

def get_hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()