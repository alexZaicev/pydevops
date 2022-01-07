import logging

from pysftp import Connection, CnOpts

from lib.config import HOST, get_config_val, PORT


class SshClient(object):

    def __init__(self, user, pwd):
        object.__init__(self)
        self.user = user

        cn_opts = CnOpts()
        cn_opts.hostkeys = None
        self.client = Connection(host=get_config_val(HOST), port=get_config_val(PORT),
                                 username=user, password=pwd, cnopts=cn_opts)

    def execute_cmd(self, cmd):
        logging.getLogger(__name__).debug('Executing command [{}]'.format(cmd))
        out = self.client.execute('cd; source .bash_profile; {}'.format(cmd))
        s_out = None
        if out is not None:
            s_out = ''
            out = [bytes.decode(x, encoding='utf-8') for x in out]
            for s in out:
                s = s.replace('\n', '')
                logging.getLogger(__name__).debug(s)
                s_out = ''.join([s_out, s])
        return s_out

    def upload_file(self, local_path, remote_path):
        self.client.put(local_path, remote_path)

    def download_file(self, local_path, remote_path):
        self.client.get(remote_path, local_path)

    def close(self):
        self.client.close()
