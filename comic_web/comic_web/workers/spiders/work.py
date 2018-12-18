from members import models as MemberModels


def get_queryset():
    return MemberModels.Task.normal.filter(active=True, task_status=MemberModels.TASK_STATUS_DESC.WAIT)


def task():
    queryset = get_queryset()
    for task in queryset:
        if task.task_type == MemberModels.TASK_TYPE_DESC.BOOK_INSERT:
            # book
            pass
        elif task.task_type == MemberModels.TASK_TYPE_DESC.COMIC_INSERT:
            # comic
            pass
