import logging

from lib.config import init, show_notification
from lib.task_runner import TaskRunner


def _print_status(status=False):
    if status:
        status = 'SUCCESS'
    else:
        status = 'FAILED'
    logging.getLogger(__name__).info(
        """\n
        XSD2XML {}
        """.format(status))
    _show_notification(status)


def _show_notification(status=None):
    show_notification("XSD2XML finished {}".format(status))


def _main():
    init()

    _runner = TaskRunner()
    status = _runner.run(task_type=TaskRunner.TP_XSD_2_XML)
    _print_status(status)


if __name__ == '__main__':
    _main()
