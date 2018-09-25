import os
import uuid
from django.conf import settings


def build_excel_path(file_name, excel_type, ext='xls'):
    _exts = ('.xls', '.xlsx')
    _base_path = os.path.join(settings.UPLOAD_SAVE_PATH , 'excel', excel_type)
    if file_name.endswith(_exts):
        return os.path.join(_base_path, file_name)
    if '.' in ext:
        ext = ext.rsplit('.', 1)[-1]
    return os.path.join(_base_path, '{}.{}'.format(file_name, ext))


def build_excel_url(file_name, excel_type, ext='xls'):
    _exts = ('.xls', '.xlsx')
    _base_path = os.path.join(settings.UPLOAD_STATIC_URL, 'excel', excel_type)
    if file_name.endswith(_exts):
        return settings.APP_HOST + os.path.join(_base_path, file_name)
    if '.' in ext:
        ext = ext.rsplit('.', 1)[-1]
    return settings.APP_HOST + os.path.join(_base_path, '{}.{}'.format(file_name, ext))


def save(_type, data=None, extension='xls'):
    valid_type = [
        'export_invite_stat',
    ]
    if _type not in valid_type:
        raise ValueError('save excel fail, check the excel type |%s|' % _type)

    file_key = str(uuid.uuid4()).replace('-', '')
    file_name = '{0}.{1}'.format(file_key, extension)
    file_dir = os.path.join(settings.UPLOAD_SAVE_PATH, 'excel', _type)
    if not os.path.isdir(file_dir):
        os.makedirs(file_dir)
    file_path = os.path.join(file_dir, file_name)

    # 导入保存
    if _type.startswith('import_'):
        with open(file_path, 'w') as f:
            f.write(data)
    # 导出保存(创建空文件)
    else:
        open(file_path, 'w').close()

    return {
        'path': file_path,
        'name': file_name,
        'key': file_key,
    }
