import re

regular = {
    'manhua.dmzj.com': 'DmzjParser',
    'e-hentai.org': 'EhentaiParser'
}

def get_parser(url):
    for (k, v) in regular.items():
        if re.search(k, url):
            module = __import__('workers.comic_spiders.parser.' + v, fromlist=[v])
            
            return getattr(module, v)()