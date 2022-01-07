from abc import ABC, abstractmethod


class PyDevOpsError(Exception):
    pass


class DeployerError(PyDevOpsError):
    pass


class SwitchError(PyDevOpsError):
    pass


class UpgraderError(PyDevOpsError):
    pass


class TaskBase(ABC):

    def __init__(self):
        ABC.__init__(self)

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def close(self):
        pass


def is_blank(s):
    return s is None or len(s) == 0


def is_not_blank(s):
    return not is_blank(s)


def parse_version(version: str):
    if is_not_blank(version):
        if version.startswith('v'):
            return version[1:]
    return None
