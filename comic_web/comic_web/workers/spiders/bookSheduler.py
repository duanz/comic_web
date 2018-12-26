import asyncio
import aiohttp
from comic_admin.models import Author, Image, IMAGE_TYPE_DESC, CoverImage
from book_admin.models import Chapter, Book
from comic_web.utils import photo as photo_lib
import requests


from comic_web.workers.spiders.tools import base_logger
# for test
from comic_web.workers.spiders.book_parser.BiqudaoParser import BiqudaoParser
from comic_web.workers.spiders.tools.utils import retry
from comic_web.workers.spiders.tools.aiohttp_proxy_connector import ProxyConnector
logger = base_logger.getLogger(__name__)


class Scheduler(object):
    download_total_number = 0
    download_complete_number = 0

    def __init__(self, url, output_path='.', max_connection_num=10, max_retry_num=5,
                 proxy=None, header=None, save_manifest_file=False, parser=BiqudaoParser(),
                 fetch_only=False, verify_ssl=False):

        # usable config:
        # name: Scheduler instance name
        # url: url of target comic
        # downloader_max_connection_num: max connection number for downloading
        # downloader_max_retry_num: max retry number for downloading
        # proxy: proxy setting (e.g: http://127.0.0.1:1081)
        # header: http request header
        # save_manifest_file: (not complete)
        self.url = url
        self.output_path = output_path
        self.max_connection_num = max_connection_num
        self.max_retry_num = max_retry_num
        self.proxy = proxy
        self.header = None
        self.save_manifest_file = False
        self.fetch_only = fetch_only
        self.verify_ssl = verify_ssl

        self.chapter_img_dict = {}

        self.sema = asyncio.Semaphore(self.max_connection_num)

        self.parser = parser

        if 'request_header' in dir(self.parser):
            self.header = self.parser.request_header

        self.aiohttp_session = aiohttp.ClientSession(
            connector=ProxyConnector(proxy=proxy, verify_ssl=self.verify_ssl), headers=self.header, read_timeout=30)

    def run(self):
        logger.info('Using parser %s ..', type(self.parser).__name__)
        logger.info('Fetch information')
        info = self._get_info(self.url)

        if not info:
            logger.error('No comic infomation found.')
            return
        else:
            logger.info('Comic name: %s', info.get('name'))

        logger.info('Fetch chapter list')
        clist = self._get_chapter_list(base_url=self.url)

        logger.info('Fetch chapter list end {}'.format(clist))
        if not clist:
            logger.error('No chapter list found')
            return
        else:
            logger.info('Chapter number: %d', len(clist))

        self._start_save_db(clist, info)

        logger.info('Download comlpleted')

        self._close_request_session()

    def _get_info(self, base_url):
        info = {}

        logger.debug('Fetching target information')

        @retry(max_num=self.max_retry_num,
               on_retry=lambda err, args, retry_num: logger.warning(
                   'Failed to get info %s (%s), retrying.', args[0][0], str(err)),
               on_fail=lambda err, args, retry_num: logger.error(
                   'Failed to get info %s (%s)', args[0][0], str(err)),
               on_fail_exit=True)
        async def fetch(url):
            async with self.aiohttp_session.get(url, verify_ssl=self.verify_ssl) as resp:
                nonlocal info
                logger.info('Fetching target information start, url is: {}'.format(url))
                ret_data = await resp.text()
                info = await self.parser.parse_info(ret_data)
                logger.info('Fetching target information end, info is : {}'.format(info))

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(fetch(base_url)))

        return info

    def _get_chapter_list(self, base_url):
        logger.debug('Starting fetch chapter list')
        chapter_list = {}

        # chapter_list = {
        #     'chapter_name': 'url'
        # }

        @retry(max_num=self.max_retry_num,
               on_retry=lambda err, args, retry_num: logger.warning(
                   'Failed to fetch chapter list %s (%s), retrying.', args[0][0], str(err)),
               on_fail=lambda err, args, retry_num: logger.error(
                   'Failed to fetch chapter list %s (%s)', args[0][0], str(err)),
               on_fail_exit=True)
        async def fetch(url, asyncio_loop, page=1):
            # with (await self.sema):
            async with self.aiohttp_session.get(url) as ret:
                nonlocal chapter_list
                ret_data = await ret.text()
                parsed_data = await self.parser.parse_chapter(ret_data)
                logger.info('ssssssfffffffsssssss: {}'.format(parsed_data))

                chapter_list.update(parsed_data[0])

        logger.info('sssssssssssss')
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(fetch(base_url, loop)))

        return chapter_list[:5]

    def _generate_download_info(self, name, path):
        return name + ' => ' + path

    def _downloader_on_retry(self, err, args, retry_num):
        logger.warning('Download fail (%s) %s, retry number: %s', str(err),
                       self._generate_download_info(args[1]['name'], args[1]['save_path']), retry_num)

    def _close_request_session(self):
        asyncio.get_event_loop().run_until_complete(
            asyncio.gather(self.aiohttp_session.close()))

    def __del__(self):
        self._close_request_session()

    def _on_download_complete(self):
        pass

    def _call_parser_hook(self, hook_name):
        pass

    def update_chapter_db(self, chapter_url, name, chapter_id=0, book_id=0, count=0):
        async def download_chapter_with_db(chapter_url, name, chapter_id=0, book_id=0, count=0):
            with (await self.sema):
                logger.info('Start download: %s', self._generate_download_info(
                    name, "this is chapter update"))

                if self.fetch_only:
                    logger.warning('Fetch only mode is on, all downloading process will not run')
                    return

                async with self.aiohttp_session.get(chapter_url, verify_ssl=self.verify_ssl) as resp:
                    logger.info('chapter url: {}'.format(chapter_url))
                    resp_data = await resp.content.read()
                    logger.info('chapter content: {}'.format(resp_data))
                    chapter_content = await self.parser.parse_chapter_content(resp_data)
                    if chapter_id:
                        Chapter.normal.filter(id=chapter_id).update(content=chapter_content)
                    else:
                        Chapter.normal.filter(book_id=book_id, title=name).update(content=chapter_content, origin_addr=chapter_url)
        
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(download_chapter_with_db(self.url, name, chapter_id, book_id)))

    def _start_save_db(self, chapter_list, info):

        async def download_image_with_db(image_url, name, book_id=0, image_type="chapter_content"):
            with (await self.sema):
                logger.info('Start download images: %s', self._generate_download_info(name, "default save path aaaa"))

                if self.fetch_only:
                    logger.warning('Fetch only mode is on, all downloading process will not run')
                    return

                async with self.aiohttp_session.get(image_url, verify_ssl=self.verify_ssl) as resp:
                    resp_data = await resp.content.read()
                    if 'on_download_complete' in dir(self.parser):
                        resp_data = getattr(self.parser, 'on_download_complete')(resp_data)

                    photo_info = photo_lib.save_binary_photo(resp_data)
                    img = Image()
                    img.key = photo_info['id']
                    img.name = photo_info['name']

                    if image_type == "comic_cover":
                        img.img_type = IMAGE_TYPE_DESC.BOOK_COVER
                        img.save()
                        self._save_book_cover(book_id=book_id, image_id=img.id)
                    return photo_info

        async def download_chapter_with_db(chapter_url, name, chapter_id=0, book_id=0, count=0):
            with (await self.sema):
                logger.info('Start download: %s', self._generate_download_info(name, "this is chapter"))

                if self.fetch_only:
                    logger.warning('Fetch only mode is on, all downloading process will not run')
                    return

                async with self.aiohttp_session.get(chapter_url, verify_ssl=self.verify_ssl) as resp:
                    logger.info('chapter url: {}'.format(chapter_url))
                    resp_data = await resp.content.read()
                    logger.info('chapter content: {}'.format(resp_data))
                    chapter_content = await self.parser.parse_chapter_content(resp_data)
                    flag = True if chapter_content else False
                    Chapter.normal.filter(book_id=book_id, title=name).update(content=chapter_content, active=flag)

        loop = asyncio.get_event_loop()
        # chapter imgs info
        future_list = []

        # save book
        book_obj = self._save_book_db(info)
        self._save_all_chapter_db(book_obj, chapter_list)

        future_list.append(download_image_with_db(image_url=info['cover'], name=book_obj.title, book_id=book_obj.id, image_type="book_cover"))
        print(11111)
        # save chapter content
        for title, c_url in chapter_list.items():
            print(">>>>>>>>>>>:", title, c_url)
            future_list.append(download_chapter_with_db(chapter_url=c_url, name=title, book_id=book_obj.id))

        loop.run_until_complete(asyncio.gather(*future_list))
        # return

    def _save_book_db(self, info):
        book = Book.normal.filter(title=info['name']).first()
        if not book:
            book = Book()
        book.title = info.get('name')
        book.author_id = self._save_or_get_author_db(info).id
        book.desc = info.get('desc')
        book.markeup = info.get('markeup')
        book.latest_chapter = info.get('latest_chapter')
        book.origin_addr = self.url
        book.save()
        return book

    def _save_book_cover(self, book_id, image_id):
        cover = CoverImage.normal.filter(book_id=book_id, image_id=image_id)
        if not cover:
            cover = CoverImage()
            cover.book_id = book_id
            cover.image_id = image_id
            cover.save()
        return cover

    def _save_or_get_author_db(self, info):
        author = Author.normal.filter(name=info['author_name']).first()
        if not author:
            author = Author()
        author.name = info['author_name']
        author.save()
        return author

    def _save_all_chapter_db(self, book, chapter_dict):
        chapter_obj_list = []
        for index, chapter in enumerate(chapter_dict, 0):
            chapter_obj = Chapter.normal.filter(book_id=book.id, title=chapter).first()
            if not chapter_obj:
                chapter_obj = Chapter()
            chapter_obj.order = index
            chapter_obj.origin_addr = chapter_dict[chapter]
            chapter_obj_list.append(chapter_obj)

            # 防止一次写入太多卡死
            if len(chapter_obj_list) == 500:
                Chapter.normal.bulk_create(chapter_obj_list)
                chapter_obj_list = []

        Chapter.normal.bulk_create(chapter_obj_list)

    def run_chapter(self, name, chapter_id=0, book_id=0):
        logger.info('Using parser %s ..', type(self.parser).__name__)
        logger.info('Fetch Chapter information')
        self.update_chapter_db(self.url, name, chapter_id, book_id)


class newSheduler(object):
    def __init__(self, url, header=None, parser=BiqudaoParser(), fetch_only=False, verify_ssl=False):
        self.url = url
        self.header = header
        self.fetch_only = fetch_only
        self.verify_ssl = verify_ssl
        self.parser = parser

        if 'request_header' in dir(self.parser):
            self.header = self.parser.request_header

        s = requests.Session()
        # s.verify = False
        # s.headers = self.header

        self.session = s

    def run(self):
        logger.info('Using parser %s ..', type(self.parser).__name__)
        book_info = self.get_book_info()
        chapter_list = self.get_chapter_list()

        self.save_to_db(book_info, chapter_list[:5])
        logger.info('comlpleted')

    def get_book_info(self):
        logger.info('get_book_info')
        ret_data = self.session.get(self.url, timeout=5).text
        book_info = self.parser.new_parse_info(ret_data)
        return book_info

    def get_chapter_list(self):
        logger.info('get_chapter_list')
        ret_data = self.session.get(self.url, timeout=5).text
        chapter_list = self.parser.new_parse_chapter(ret_data)
        return chapter_list[0]

    def get_chapter_content(self, url):
        logger.info('get_chapter_content: {}'.format(url))
        ret_data = self.session.get(url, timeout=5).text
        content = self.parser.new_parse_chapter_content(ret_data)
        return content

    def _save_book_db(self, info):
        logger.info('_save_book_db')

        book = Book.normal.filter(title=info['name']).first()
        if not book:
            book = Book()
        book.title = info.get('name')
        book.author_id = self._save_or_get_author_db(info).id
        book.desc = info.get('desc')
        book.markeup = info.get('markeup')
        book.latest_chapter = info.get('latest_chapter')
        book.origin_addr = self.url
        book.save()
        return book

    def _save_book_cover(self, book_id, image_id):
        cover = CoverImage.normal.filter(book_id=book_id, image_id=image_id)
        if not cover:
            cover = CoverImage()
            cover.book_id = book_id
            cover.image_id = image_id
            cover.save()
        return cover

    def _save_or_get_author_db(self, info):
        author = Author.normal.filter(name=info['author_name']).first()
        if not author:
            author = Author()
        author.name = info['author_name']
        author.save()
        return author

    def _save_all_chapter_db(self, book, chapter_dict):
        logger.info('_save_all_chapter_db')

        chapter_obj_list = []
        for index, chapter in enumerate(chapter_dict, 0):
            logger.info('{}_ -cccchapter-__{}'.format(chapter, chapter_dict[chapter]))
            chapter_obj = Chapter.normal.filter(book_id=book.id, title=chapter).first()
            if not chapter_obj:
                chapter_obj = Chapter()
            chapter_obj.order = index
            chapter_obj.origin_addr = chapter_dict[chapter]
            chapter_obj_list.append(chapter_obj)

            # 防止一次写入太多卡死
            if len(chapter_obj_list) == 500:
                Chapter.normal.bulk_create(**chapter_obj_list)
                chapter_obj_list = []

        Chapter.normal.bulk_create(chapter_obj_list)

    def _update_chapter_content_db(self, book_id, chapter_id=None):
        logger.info('_update_chapter_content_db')

        if chapter_id:
            queryset = Chapter.normal.filter(book_id=book_id, id=chapter_id)
        else:
            queryset = Chapter.normal.filter(book_id=book_id)

        for obj in queryset:
            if obj.origin_addr:
                content = self.get_chapter_content(obj.origin_addr)
                obj.content = content
                obj.save()

    def save_to_db(self, book_info, chapter_list):
        logger.info('save_to_db')

        book_obj = self._save_book_db(book_info)
        self._save_all_chapter_db(book_obj, chapter_list)

        # self._update_chapter_content_db(book_obj.id)

        logger.info('save_to_db_end')
