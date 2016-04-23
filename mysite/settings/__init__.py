from .base import *

try:
	live = False

except:
	live = True

if live:
	from .production import *