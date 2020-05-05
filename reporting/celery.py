from __future__ import absolute_import

from os.path import abspath, dirname, join
import os, sys

from django.conf import settings

from celery import Celery

from ddtrace import patch

patch(celery=True)

PROJECT_ROOT = abspath(dirname(__file__))
PORTAL_ROOT = join(PROJECT_ROOT, "portal")

BUILTIN_FIXUPS = frozenset([
    'juloserver.julo.fixups_custom:fixup',
])

CELERY_LOADER = "juloserver.routing.celery_loader_custom:AppLoader"

sys.path.insert(0, PORTAL_ROOT)
sys.path.insert(1, join(PORTAL_ROOT, "authentication"))
sys.path.insert(2, join(PORTAL_ROOT, "core"))
sys.path.insert(3, join(PORTAL_ROOT, "configuration"))
sys.path.insert(4, join(PORTAL_ROOT, "object"))
sys.path.insert(5, join(PORTAL_ROOT, "process"))

celery_app = Celery('juloserver', broker="amqp://guest:guest@localhost:5672//",
                    fixups=BUILTIN_FIXUPS, loader=CELERY_LOADER)
celery_app.config_from_object('django.conf:settings')
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
