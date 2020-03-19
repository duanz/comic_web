from comic_web.workers.spiders.book_parser.BaseParser import BaseParser
from pyquery import PyQuery as pq


class BiqugexParser(BaseParser):
    image_base_url = 'http://www.biquge.tv'
    page_base_url = 'http://www.biquge.tv'
    filename_extension = 'jpg'
    request_header = {
        'Accept': 'text/html,application/xhtml+xm…plication/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': 'www.biquge.tv',
        'Pragma': 'no-cache',
        'Upgrade-Insecure-Requests': 1,
        'referer': 'www.biquge.tv',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36  \
                        (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36'
    }

    def parse_info(self, data):
        if data and hasattr(data, "content"):
            data = data.content.decode("gbk")
        
        doc = pq(data)
        book_name = doc('meta[property="og:title"]').attr('content')
        book_desc = doc('meta[property="og:description"]').attr('content').replace("\xa0", '')
        latest_chapter_str = doc(
            'meta[property="og:novel:latest_chapter_name"]').attr('content')
        author_name = doc('meta[property="og:novel:author"]').attr('content')
        markeup = doc('meta[property="og:novel:category"]').attr('content')
        cover = doc('meta[property="og:image"]').attr('content')

        info = {
            'name': book_name,
            'latest_chapter': latest_chapter_str,
            'desc': book_desc,
            'author_name': author_name,
            'markeup': markeup,
            'cover': cover
        }
        return info

    def parse_chapter(self, data):
        if data and hasattr(data, "content"):
            data = data.content.decode("gbk")

        doc = pq(data)
        dl_dd = doc('#list dl').children()[1:]
        chapter_list = []

        flag = False
        for u in dl_dd:
            if flag:
                link = u.find('a').get('href')
                chapter_list.append(
                    {u.text_content():self.page_base_url + link})
            else:
                flag = u.tag == 'dt'

        return chapter_list

    def parse_chapter_content(self, data):
        if data and hasattr(data, "content"):
            data = data.content.decode("gbk")
        doc = pq(data)
        content = doc("#content").text()
        return content

    def parse_chapter_singal(self, data):
        if data and hasattr(data, "content"):
            data = data.content.decode("gbk")
        doc = pq(data)
        title = doc(".content h1").text()
        content = doc("#content").text()
        return {"title": title, "content": content}
