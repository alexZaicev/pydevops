# import base64

# from requests import get

# _auth = base64.b64encode('{}:{}'.format('alza', 'Mandarinai@123').encode()).decode()

# 'https://repo.rdswiss.ch/artifactory/gmp-snapshots/ch/bbp/fms/workbench.tm/'
# 'https://repo.rdswiss.ch/artifactory/gmp-snapshots/ch/bbp/fms/workbench.tm/900.0.9-SNAPSHOT/'
# 'https://repo.rdswiss.ch/artifactory/gmp-snapshots/ch/bbp/fms/workbench.tm/900.0.9-SNAPSHOT/workbench.tm-900.0.9-20211012.230027-165.tar.gz/'
# url = 'https://repo.rdswiss.ch/artifactory/gmp-snapshots/ch/bbp/fms/workbench.ingres/900.0.5-SNAPSHOT/workbench.ingres-900.0.5-20211012.230015-156.tar.gz/'
# _headers = {
#             'Authorization': 'Basic {}'.format(_auth),
#             'Accept-Encoding': 'gzip, deflate, br',
#             'Connection': 'keep-alive',
#             'Cache-Control': 'no-cache'
#         }

# res = get(url, headers=_headers, stream=True)
# if res.status_code != 200:
#     raise Exception()

