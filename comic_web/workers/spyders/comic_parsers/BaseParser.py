from abc import ABCMeta, abstractmethod


class BaseParser(metaclass=ABCMeta):

    @abstractmethod
    def parse_info(self, data):
        """ 获取初始基本信息

            Returns:
                {
                    'name': '...'
                }
        """

    @abstractmethod
    def parse_chapter(self, data, page):
        """ 获取章节地址列表.
            Returns:
                [url1, url2, ...]
        """

    @abstractmethod
    def parse_image_list(self, data):
        """ Parse image URL from received data.
            Args:
                data: data come from requesting specified URL.

            Returns:
                {
                    'file_name': 'url'
                }
        """

    def parse_downloaded_data(self, data):
        """ Process the downloaded data. (optional)
            You can do some action (such as decrypt, unzip, etc) in there
            Args:
                data: data come from requesting specified URL.

            Returns:
                processed data
        """
