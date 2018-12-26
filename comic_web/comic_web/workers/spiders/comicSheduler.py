import requests

from comic_admin.models import Comic, Author, Chapter, Image, IMAGE_TYPE_DESC, ChapterImage, CoverImage
from comic_web.utils import photo as photo_lib

from comic_web.workers.spiders.tools import base_logger
# for test
from comic_web.workers.spiders.comic_parser.SimpleParser import SimpleParser
logger = base_logger.getLogger(__name__)


class ComicSheduler(object):
    def __init__(self, url, header=None, parser=SimpleParser(), fetch_only=False, verify_ssl=False):
        self.url = url
        self.header = header
        self.fetch_only = fetch_only
        self.verify_ssl = verify_ssl
        self.parser = parser

        if 'request_header' in dir(self.parser):
            self.header = self.parser.request_header

        s = requests.Session()
        s.headers = self.header
        self.session = s

    def run(self):
        logger.info('Using parser %s ..', type(self.parser).__name__)
        book_info = self.get_book_info()
        chapter_list = self.get_chapter_list()

        self.save_to_db(book_info, chapter_list)
        logger.info('comlpleted')

    def get_book_info(self):
        logger.info('get_book_info start')
        ret_data = self.session.get(self.url, timeout=5).text
        book_info = self.parser.parse_info(ret_data)
        logger.info('get_book_info comlpleted')
        return book_info

    def get_chapter_list(self):
        logger.info('get_chapter_list start')
        ret_data = self.session.get(self.url, timeout=5).text
        chapter_list = self.parser.parse_chapter(ret_data)
        logger.info('get_chapter_list comlpleted: {}'.format(chapter_list[0]))
        return chapter_list[0]

    def get_chapter_content(self, url):
        logger.info('get_chapter_content: {} start'.format(url))
        ret_data = self.session.get(url, timeout=5).text
        image_list = self.parser.parse_image_list(ret_data)
        logger.info('get_chapter_content: {} comlpleted'.format(image_list))
        return image_list

    def _save_image_disk(self, url):
        logger.info('_save_image_disk: {}'.format(url))
        resp_data = self.session.get(url, timeout=5).content
        photo_info = photo_lib.save_binary_photo(resp_data)
        return photo_info

    def _save_or_get_author_db(self, info):
        logger.info('_save_or_get_author_db')
        author = Author.normal.filter(name=info['author_name']).first()
        if not author:
            author = Author()
        author.name = info['author_name']
        author.save()
        return author

    def _save_comic_db(self, info):
        logger.info('_save_comic_db')

        comic = Comic.normal.filter(title=info['name']).first()
        if not comic:
            comic = Comic()
        comic.title = info.get('name')
        comic.author_id = self._save_or_get_author_db(info).id
        comic.desc = info.get('desc')
        comic.markeup = info.get('markeup')
        comic.title = info.get('name')
        comic.origin_addr = self.url
        comic.save()
        if isinstance(info['cover'], list):
            logger.info('_save_comic_db run loop')
            for index, url in enumerate(info['cover'], 1):
                info = self._save_image_disk(url)
                img, flag = Image.normal.get_or_create(img_type=IMAGE_TYPE_DESC.COMIC_COVER, key=info['id'], name=info['name'])
                logger.info('_save_comic_db run loop,{}==={}==={}'.format(comic, info, img))
                self._save_comic_cover(comic.id, img.id)
        else:
            info = self._save_image_disk(info['cover'])
            # img = Image(img_type=IMAGE_TYPE_DESC.COMIC_COVER, key=info['id'], name=info['name']).save()
            img, flag = Image.normal.get_or_create(img_type=IMAGE_TYPE_DESC.COMIC_COVER, key=info['id'], name=info['name'])
            logger.info('_save_comic_db run singal,{}==={}==={}'.format(comic, info, img))
            self._save_comic_cover(comic.id, img.id)
        return comic

    def _save_comic_cover(self, comic_id, image_id):
        logger.info('_save_comic_cover')
        cover = CoverImage.normal.filter(comic_id=comic_id, image_id=image_id).first()
        if not cover:
            cover = CoverImage()
        cover.comic_id = comic_id
        cover.image_id = image_id
        cover.save()
        return cover

    def _save_all_chapter_db(self, comic, chapter_dict):
        logger.info('_save_all_chapter_db')

        for index, chapter in enumerate(chapter_dict, 0):
            logger.info('{}_ -cccchapter-__{}'.format(chapter, chapter_dict[chapter]))
            chapter_obj = Chapter.normal.filter(comic_id=comic.id, title=chapter).first()
            if not chapter_obj:
                chapter_obj = Chapter()
            chapter_obj.comic_id = comic.id
            chapter_obj.title = chapter
            chapter_obj.order = index
            chapter_obj.origin_addr = chapter_dict[chapter]
            chapter_obj.save()

    def _update_chapter_content_db(self, comic_id):
        logger.info('_update_chapter_content_db')

        queryset = Chapter.normal.filter(comic_id=comic_id)
        for obj in queryset:
            if obj.origin_addr:
                image_list = self.get_chapter_content(obj.origin_addr)
                for index, img in enumerate(image_list.values(), 1):
                    info = self._save_image_disk(img)
                    img, flag = Image.normal.get_or_create(img_type=IMAGE_TYPE_DESC.CHAPER_CONTENT, order=index, key=info['id'], name=info['name'])
                    ChapterImage(comic_id=comic_id, chapter_id=obj.id, image_id=img.id, order=index).save()

    def save_to_db(self, comic_info, chapter_list):
        logger.info('save_to_db start')

        comic_obj = self._save_comic_db(comic_info)
        self._save_all_chapter_db(comic_obj, chapter_list)
        self._update_chapter_content_db(comic_obj.id)

        logger.info('save_to_db_end')


class ComicChapterSheduler(object):
    def __init__(self, url, comic_id, chapter_id, header=None, parser=SimpleParser(), fetch_only=False, verify_ssl=False):
        self.url = url
        self.comic_id = comic_id
        self.chapter_id = chapter_id
        self.header = header
        self.fetch_only = fetch_only
        self.verify_ssl = verify_ssl
        self.parser = parser

        if 'request_header' in dir(self.parser):
            self.header = self.parser.request_header

        s = requests.Session()
        # s.verify = False
        s.headers = self.header

        self.session = s

    def run(self):
        logger.info('Using parser %s ..', type(self.parser).__name__)
        self.run_update_chapter()
        logger.info('comlpleted')

    def get_chapter_content(self, url):
        logger.info('get_chapter_content: {} start'.format(url))
        ret_data = self.session.get(url, timeout=5).text
        image_list = self.parser.parse_image_list(ret_data)
        logger.info('get_chapter_content: {} comlpleted'.format(url))
        return image_list

    def _save_image_disk(self, url):
        resp_data = self.session.get(url, timeout=5).content
        photo_info = photo_lib.save_binary_photo(resp_data)
        return photo_info

    def run_update_chapter(self):
        logger.info('update_chapter_content: {}'.format(self.url))

        image_list = self.get_chapter_content(self.url)
        for index, img in enumerate(image_list.values(), 1):
            info = self._save_image_disk(img)
            img, flag = Image.normal.get_or_create(img_type=IMAGE_TYPE_DESC.CHAPER_CONTENT, order=index, key=info['id'], name=info['name'])
            ChapterImage(comic_id=self.comic_id, chapter_id=self.chapter_id, image_id=img.id, order=index).save()
        Chapter.normal.filter(comic_id=self.comic_id, id=self.chapter_id).update(origin_addr=self.url)
