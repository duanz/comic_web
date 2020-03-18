
from comic_web import celery_app as app
from comic_web.workers.spiders import work
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings
import os
import shutil
from kindlecomicconverter.comic2panel import main as kcc_c2p
from comic_admin.models import Comic, Chapter, ChapterImage
from comic_admin.serializers import CommonImageSerializer

@app.task(ignore_result=True)
def handle_book_and_comic_spider_tasks():
    """定时任务：执行Task表中状态为‘WAIT’的任务"""
    work.task()


def handle_send_email_to_kindle():
    '''
    TODO
    '''
    host = os.getenv("EMAIL_HOST", "")
    port = os.getenv("EMAIL_PORT", "")
    username = os.getenv("EMAIL_USERNAME", "")
    password = os.getenv("EMAIL_PASSWORD", "")
    use_tls = os.getenv("EMAIL_USE_TLS", False)
    from_email = os.getenv("EMAIL_FROM_EMAIL", "")
    to_email = os.getenv("EMAIL_TO_EMAIL", "").replace(" ", "").split(",")
    fail_silently = os.getenv("EMAIL_FAIL_SILENTLY", False)
    
    backend = EmailBackend(host=host, port=port, username=username, password=password, use_tls=use_tls, fail_silently=fail_silently)
    # 普通邮件
    # email = EmailMessage(subject='subj', body='body', from_email=from_email, to=to_email, connection=backend)
    email = EmailMultiAlternatives(subject="新书推送", body="", from_email=from_email, to=to_email, connection=backend)    
    # 添加附件（可选）
    email.attach_file('./twz.pdf')    
    # 发送
    email.send()
    pass


def handle_comic_mobi(comic_id):
    """打包成mobi格式文件"""
    '''
    TODO
    '''
    new_path, title = copy_comic_to_temp_floder(comic_id)
    height = 960
    folder = new_path
    argv = ["-y {height} -m {folder}".format(height, folder)]
    kcc_c2p(argv=argv)
    return new_path
    pass


def copy_comic_to_temp_floder(comic_id):
    comic = Comic.normal.filter(id=comic_id).first()
    new_path = os.path.join(settings.BASE_DIR, comic.title)

    if not os.path.exists(new_path):
        os.makedirs(new_path, 0o0755)

    chapters = Chapter.normal.filter(comic_id=comic.id).values("id")
    for cha in chapters:
        ser = CommonImageSerializer.to_representation(chapter_id=cha['id'], quality="title", only_url=False, only_path=True)
        for path in ser:
            shutil.copy(path, new_path)
    return new_path, comic.title