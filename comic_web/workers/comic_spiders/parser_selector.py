import re
regular = {}

comic_regular = {
    'manhua.dmzj.com': 'DmzjParser',
    'e-hentai.org': 'EhentaiParser'
}

book_regular = {
    "biqudao.com": "BiqudaoParser",
}

regular.update(comic_regular)
regular.update(book_regular)


def get_parser(url):
    for (k, v) in regular.items():
        if re.search(k, url):
            if k in comic_regular:
                module = __import__(
                    'workers.comic_spiders.parser.' + v, fromlist=[v])
            elif k in book_regular:
                module = __import__(
                    'workers.book_spiders.parser.' + v, fromlist=[v])

            return getattr(module, v)()
