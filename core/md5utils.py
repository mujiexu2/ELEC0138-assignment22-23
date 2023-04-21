import hashlib

def md5_encode(text):
    """使用 MD5 进行加密"""
    m = hashlib.md5()
    m.update(text.encode('utf-8'))
    return m.hexdigest()
