# Django settings for countryx project.
import os.path
from thraxilsettings.shared import common

app = 'countryx'
base = os.path.dirname(__file__)

locals().update(common(app=app, base=base))

PROJECT_APPS = ['countryx.sim', 'countryx.events']

INSTALLED_APPS += [  # noqa
    'bootstrapform',
    'countryx.sim',
    'countryx.events',
    'countryx.reports',
    'impersonate',
]

STATE_COLORS = [
    'ffd478', '009192', 'ff9400', 'd25700', '935200', 'd4fb79',
    '73fa79', '8efa00', '4e8f00', '0096ff', '0a31ff', 'd783ff',
    '7a80ff', '531a93', 'ff8ad8', 'ff3092', 'ff40ff', '009051',
    '942092', '941751', '941200', 'ff2700', '005393', 'ff7e79',
    'fffc00', '76d6ff', '00f900', '929292', '929000']

LOGIN_REDIRECT_URL = "/"
