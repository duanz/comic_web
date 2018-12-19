import asyncio
import aiohttp

from comic_admin.models import Comic, Author, Chapter, Image, IMAGE_TYPE_DESC, ChapterImage, CoverImage
from comic_web.utils import photo as photo_lib

from spiders.tools import base_logger
# for test
from spiders.comic_parser.SimpleParser import SimpleParser
from spiders.tools.utils import retry
from spiders.tools.aiohttp_proxy_connector import ProxyConnector
logger = base_logger.getLogger(__name__)


class Scheduler(object):
    download_total_number = 0
    download_complete_number = 0

    def __init__(self, url, output_path='.', max_connection_num=10, max_retry_num=5,
                 proxy=None, header=None, save_manifest_file=False, parser=SimpleParser(),
                 fetch_only=False, verify_ssl=True):

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
        self.comic_obj = None

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

        if not clist:
            logger.error('No chapter list found')
            return
        else:
            logger.info('Chapter number: %d', len(clist))

        logger.info('Fetch image url list')
        img_list = self._get_image_url_list(clist)
        logger.info('Total image number: %s', self.total_image_num)
        logger.info('Start download images')
        # self._start_download(img_list, info['name'])
        self._start_save_db(img_list, info)
        self._save_chapter_img_db(self.comic_obj, self.chapter_img_dict)

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
                ret_data = await resp.text()
                info = await self.parser.parse_info(ret_data)

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
            with (await self.sema):
                async with self.aiohttp_session.get(url) as ret:

                    ret_data = await ret.text()
                    parsed_data = await self.parser.parse_chapter(ret_data)

                    if self.parser.chapter_mode:
                        chapter_list.update(parsed_data[0])
                    else:
                        for i in parsed_data[0]:
                            chapter_list.setdefault(
                                '{}-{}'.format(page, parsed_data[0].index(i)), i)

                    if len(parsed_data) > 1 and not parsed_data[1] is None:
                        page += 1
                        await fetch(parsed_data[1], asyncio_loop, page)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.gather(fetch(base_url, loop)))

        return chapter_list

    def _get_image_url_list(self, chapter_list):

        image_url_list = {}

        # image_url_list = {
        #     'chapter_name': {
        #         'file_name': 'url'
        #     }
        #     # ...
        # }

        total_image_num = 0

        @retry(max_num=self.max_retry_num,
               on_retry=lambda err, args, retry_num: logger.warning(
                   'Failed to fetch image list "%s" (%s), retrying.', str(args[0]), str(err)),
               on_fail=lambda err, args, retry_num: logger.error(
                   'Failed to fetch image list "%s" (%s)', str(args[0]), str(err)),
               on_fail_exit=True)
        async def fetch(chapter_name, chapter_url):
            nonlocal total_image_num
            with (await self.sema):
                async with self.aiohttp_session.get(chapter_url, verify_ssl=self.verify_ssl) as resp:
                    image_list = await self.parser.parse_image_list(await resp.text())
                    total_image_num += len(image_list)
                    image_url_list.update({chapter_name: image_list})

        loop = asyncio.get_event_loop()
        future_list = []

        for k, v in chapter_list.items():
            future_list.append(fetch(k, v))

        loop.run_until_complete(asyncio.gather(*future_list))
        self.total_image_num = total_image_num
        return image_url_list

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

    def _start_save_db(self, image_url_list, info):

        async def download_images_with_db(image_url, name, chapter_id=0, comic_id=0, count=0, image_type="chapter_content"):
            with (await self.sema):
                logger.info('Start download: %s', self._generate_download_info(name, "default save path"))

                if self.fetch_only:
                    logger.warning(
                        'Fetch only mode is on, all downloading process will not run'
                    )
                    return

                async with self.aiohttp_session.get(
                        image_url, verify_ssl=self.verify_ssl) as resp:
                    resp_data = await resp.content.read()
                    if 'on_download_complete' in dir(self.parser):
                        resp_data = getattr(self.parser, 'on_download_complete')(resp_data)

                    photo_info = photo_lib.save_binary_photo(resp_data)
                    img = Image()
                    img.key = photo_info['id']
                    img.name = photo_info['name']

                    if image_type == "chapter_content":
                        img.img_type = IMAGE_TYPE_DESC.CHAPER_CONTENT
                        img.save()
                        ChapterImage(comic_id=comic_id, chapter_id=chapter_id, image_id=img.id, order=count).save()
                    elif image_type == "comic_cover":
                        img.img_type = IMAGE_TYPE_DESC.COMIC_COVER
                        img.save()
                        self._save_comic_cover(comic_id=comic_id, image_id=img.id)
                    return photo_info

        loop = asyncio.get_event_loop()
        # chapter imgs info
        future_list = []

        # save comic
        self.comic_obj = self._save_comic_db(info)

        chapter_count = 0
        for k, v in image_url_list.items():
            # save chapter
            chapter_obj = self._save_chapter_db(self.comic_obj, k, chapter_count)
            chapter_count += 1

            count = 0
            for name, url in v.items():
                future_list.append(download_images_with_db(image_url=url, name=name, chapter_id=chapter_obj.id, comic_id=self.comic_obj.id, count=count))
                count += 1
        future_list.append(download_images_with_db(image_url=info['cover'], name=self.comic_obj.title, comic_id=self.comic_obj.id, image_type="comic_cover"))

        loop.run_until_complete(asyncio.gather(*future_list))
        # return

    def _save_comic_db(self, info):
        comic = Comic.normal.filter(title=info['name']).first()
        if not comic:
            comic = Comic()
        comic.title = info.get('name')
        comic.author_id = self._save_or_get_author_db(info).id
        comic.desc = info.get('desc')
        comic.markeup = info.get('markeup')
        comic.title = info.get('name')
        comic.save()
        return comic

    def _save_comic_cover(self, comic_id, image_id):
        cover = CoverImage.normal.filter(comic_id=comic_id, image_id=image_id)
        if not cover:
            cover = CoverImage()
        cover.comic_id = comic_id
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

    def _save_chapter_db(self, comic, title, order):
        chapter = Chapter.normal.filter(comic_id=comic.id, title=title).first()
        if not chapter:
            chapter = Chapter()
        chapter.comic_id = comic.id
        chapter.title = title
        chapter.order = order
        chapter.save()
        return chapter

    def _save_chapter_img_db(self, comic_id, chapter_img_list):
        for chapter_id, img_list in chapter_img_list.items():
            count = 0
            for index, info in enumerate(img_list):
                img = Image(img_type=IMAGE_TYPE_DESC.CHAPER_CONTENT, order=index, key=info['id'], name=info['name']).save()
                ChapterImage(comic_id=comic_id, chapter_id=chapter_id, image_id=img.id, order=count).save()
                count += 1
