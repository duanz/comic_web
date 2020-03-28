
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings
import logging
import os
import shutil
from comic_admin.models import Comic
from book_admin.models import Book

class SendKindleEmail:
    def __init__(self, content_id, content_type):
        self.content_id = content_id
        self.content_type = content_type
        self.email = ""
        self.attach_file = ""
    
    def run(self):
        # 初始化邮箱
        self.getEmail()
        logging.info("初始化邮箱完成")
        # 获取附件
        self.getAttachFile()
        logging.info("获取附件完成： {}".format(self.attach_file))
        # 添加附件
        if isinstance(self.attach_file, list):
            [self.email.attach_file(filepart) for filepart in self.attach_file]
        
        elif isinstance(self.attach_file, str):
            self.email.attach_file(self.attach_file)    
        # 发送
        self.email.send()
        logging.info("邮件发送完成")
    
    def getAttachFile(self):
        content_obj = ""
        if self.content_type == 'comic':
            content_obj = Comic.normal.filter(id=self.content_id).first()
        elif self.content_type == 'book':
            content_obj = Book.normal.filter(id=self.content_id).first()
        
        if not content_obj:
            raise Exception("没有找到要发送的内容： id:{}, type: {}".format(self.content_id, self.content_type))
        
        if self.content_type == 'comic':
            filename = []
            part = 1
            file_part = lambda part: os.path.join(settings.UPLOAD_SAVE_PATH, '{}__{}.docx'.format(content_obj.title, part))
            while os.path.exists(file_part(part)):
                filename.append(file_part(part))
                part += 1
        elif self.content_type == 'book':
            filename = os.path.join(settings.UPLOAD_SAVE_PATH, content_obj.title + '.txt')
        

        self.attach_file = filename

    def getEmail(self):
        host = os.getenv("EMAIL_HOST", "")
        port = os.getenv("EMAIL_PORT", "")
        username = os.getenv("EMAIL_HOST_USER", "")
        password = os.getenv("EMAIL_HOST_PASSWORD", "")
        from_email = os.getenv("EMAIL_FROM_EMAIL", "")
        to_email = os.getenv("EMAIL_TO_EMAIL", "").replace(" ", "").split(",")
        backend = EmailBackend(host=host, port=port, username=username, password=password)
        subject = "新书推送"
        email = EmailMultiAlternatives(subject=subject, body="", from_email=from_email, to=to_email, connection=backend)
        self.email = email
