import base64
import logging
import re
import sys
import time

import requests
from urllib3.exceptions import InsecureRequestWarning

from lib.config import get_config_val, REPO_USER, REPO_PWD
from lib.model import PyDevOpsError, is_not_blank

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class ArtifactDownloader(object):

    def __init__(self):
        object.__init__(self)

    @classmethod
    def download_artifact(cls, url, stream=False, file_path=None, artifact=None, use_auth=True) -> requests.Response:
        _headers = {
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        }
        if use_auth:
            _pwd = base64.b64decode(get_config_val(REPO_PWD).encode()).decode()
            _auth = base64.b64encode('{}:{}'.format(get_config_val(REPO_USER), _pwd).encode()).decode()
            _auth = 'Basic {}'.format(_auth)
            _headers['Authorization'] = _auth
            res = requests.get(url, headers=_headers, stream=stream)
        else:
            res = requests.get(url, stream=stream)

        if stream:
            logging.getLogger(__name__).info('Downloading artifact [{}]'.format(artifact))
            with open(file_path, 'wb') as ff:
                start = time.time()
                total = res.headers.get('content-length')
                if total is None:
                    ff.write(res.content)
                else:
                    downloaded = 0
                    total = int(total)
                    for data in res.iter_content(chunk_size=max(int(total / 1000), 1024 * 1024)):
                        downloaded += len(data)
                        ff.write(data)
                        done = int(50 * downloaded / total)

                        sys.stdout.write('\rDownloading ({}): [{}{}]'.format(
                            cls._get_download_spead(downloaded, start),
                            '#' * done, '.' * (50 - done)))
                        sys.stdout.flush()
            sys.stdout.write('\n')
        else:
            if res.status_code != 200:
                raise PyDevOpsError('Unable to perform request. Status code [{}]'.format(url))
        return res

    @classmethod
    def get_versioned_artifact_url(cls, url, version=None):
        if is_not_blank(version):
            version_path = version
        else:
            matches = re.findall(r'<a href=".*?">.+?</a>', str(cls.download_artifact('{}/'.format(url)).content))
            version_path = matches[-2].replace('</a>', '')
            version_path = re.sub(r'<a href=".*?">', '', version_path).replace('/', '')

        url = '{}/{}'.format(url, version_path)

        matches = re.findall(r'<a href=".*?">.+?</a>', str(cls.download_artifact('{}/'.format(url)).content))
        artifacts = list()
        for m in matches:
            m = re.sub(r'<a href=".*?">', '', m).replace('</a>', '')
            if m.endswith('.tar.gz'):
                artifacts.append(m)
        artifact_path = artifacts[-1]

        url = '{}/{}'.format(url, artifact_path)
        return url, artifact_path

    @classmethod
    def _get_download_spead(cls, downloaded, start):
        units = 'bps'
        speed = downloaded // (time.time() - start)
        if pow(10, 6) < speed:
            speed /= pow(10, 6)
            units = 'mbs'
        elif pow(10, 3) < speed:
            speed /= pow(10, 3)
            units = 'kbs'
        speed = '{:.2f} {}'.format(speed, units)
        return speed
