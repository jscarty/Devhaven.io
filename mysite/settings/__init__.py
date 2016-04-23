from .base import *

try:
	from .base import *
	live = False

except:
	live = True

if live:
	from .production import *