from django.conf import settings

HAC_API_URL = getattr(settings, 'HAC_API_URL', "https://hac2.schwarz/api/v1/hanadatabases/")
HAC_USER = getattr(settings, 'HAC_USER', None)
HAC_PASS = getattr(settings, 'HAC_PASS', None)

HALM_USER = getattr(settings, 'HALM_USER', "TU_SAPACCESS")
HALM_PASS = getattr(settings, 'HALM_PASS', None)
HDBCLIENT_DIR = getattr(settings, 'HDBCLIENT_DIR', None)
