import asyncio
import aiohttp
from comic_admin.models import Author, Image, IMAGE_TYPE_DESC, CoverImage
from book_admin.models import Chapter, Book
from comic_web.utils import photo as photo_lib
import requests


from workers.comic_spiders import base_logger
# for test
from workers.comic_spiders.parser.SimpleParser import SimpleParser
from workers.comic_spiders.utils import retry
from workers.comic_spiders.aiohttp_proxy_connector import ProxyConnector
logger = base_logger.getLogger(__name__)


class Scheduler(object):
    download_total_number = 0
    download_complete_number = 0

    def __init__(self, url, output_path='.', name='Scheduler', max_connection_num=10, max_retry_num=5,
                 proxy=None, header=None, save_manifest_file=False, parser=SimpleParser(),
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
        self.name = name
        self.max_connection_num = max_connection_num
        self.max_retry_num = max_retry_num
        self.proxy = proxy
        self.header = None
        self.save_manifest_file = False
        self.fetch_only = fetch_only
        self.verify_ssl = verify_ssl

        self.chapter_img_dict = {}
        self.book_obj = None

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
        # return

        if not info:
            logger.error('No book infomation found.')
            return
        else:
            logger.info('Book name: %s', info.get('name'))

        logger.info('Fetch chapter list')
        clist = self._get_chapter_list(base_url=self.url)

        if not clist:
            logger.error('No chapter list found')
            return
        else:
            logger.info('Chapter number: %d', len(clist))

        logger.info('Start save databases')
        
        self._start_save_db(info, clist)
        self._save_chapter_db(self.book_obj, clist)

        logger.info('Download comlpleted')

        self._close_request_session()

    def _get_info(self, base_url):
        info = {}

        logger.debug('Fetching target information')

        async def fetch(url):
            res = requests.get(base_url)
            nonlocal info
            info = await self.parser.parse_info(res.text)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(fetch(base_url)))

        return info

    def _get_chapter_list(self, base_url):
        logger.debug('Starting fetch chapter list')
        chapter_list = {}

        async def fetch(url):
            res = requests.get(base_url)
            nonlocal chapter_list
            chapter_list = await self.parser.parse_chapter(res.text)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(fetch(base_url)))

        return chapter_list

    def _close_request_session(self):
        asyncio.get_event_loop().run_until_complete(
            asyncio.gather(self.aiohttp_session.close()))

    def __del__(self):
        self._close_request_session()

    def _start_save_db(self, info, chapter_list):
        # 解藕希望

        # @retry(max_num=self.max_retry_num,
        #        on_retry=lambda err, args, retry_num: logger.warning(
        #            'Failed to request url "%s" (%s), retrying.', args[1]['image_url'], str(err)),
        #        on_fail=lambda err, args, retry_num: logger.error('Failed to request target "%s" (%s)', args[1]['image_url'], str(err)))
        async def download_with_db(image_url, name, chapter_id=0, book_id=0, count=0, image_type="chapter_content"):
            with (await self.sema):
                # utils.mkdir('/'.join(save_path.split('/')[:-1]))
                # async with aiohttp.ClientSession(headers=self.header) as session:

                if self.fetch_only:
                    logger.warning(
                        'Fetch only mode is on, all downloading process will not run'
                    )
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
        
        async def download_with_db_chapter(chapter_url, name, chapter_id=0, book_id=0, count=0):
            with (await self.sema):
                logger.info('Start download: %s',
                            self._generate_download_info(name, "default save path"))
                # utils.mkdir('/'.join(save_path.split('/')[:-1]))
                # async with aiohttp.ClientSession(headers=self.header) as session:

                if self.fetch_only:
                    logger.warning(
                        'Fetch only mode is on, all downloading process will not run'
                    )
                    return

                async with self.aiohttp_session.get(chapter_url, verify_ssl=self.verify_ssl) as resp:
                    resp_data = await resp.content.read()
                    chapter_content = await self.parser.parse_chapter_content(resp_data)

                    Chapter.normal.filter(book_id=book_id, title=name).update(content=chapter_content)                 

        loop = asyncio.get_event_loop()
        # chapter imgs info
        future_list = []

        # save book
        self.book_obj = self._save_book_db(info)
        self._save_all_chapter_db(self.book_obj, chapter_list)

        future_list.append(download_with_db(
            image_url=info['cover'], name=self.book_obj.title, book_id=self.book_obj.id, image_type="book_cover"))
        
        # save chapter content
        for item in chapter_list:
            title = list(item)[0]
            future_list.append(download_with_db_chapter(
                chapter_url=item[title], name=title, book_id=self.book_obj.id))

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

    def _save_all_chapter_db(self, book, chapter_list):
        chapter_obj_list = []
        for index, chapter in enumerate(chapter_list, 0):
            title = list(chapter)[0]
            flag = Chapter.normal.filter(book_id=book.id, title=chapter[title]).exists()
            if not flag:
                chapter_obj = Chapter(book_id=book.id, title=title, order=index, origin_addr=chapter[title])
                chapter_obj_list.append(chapter_obj)
        
        Chapter.normal.bulk_create(chapter_obj_list)
