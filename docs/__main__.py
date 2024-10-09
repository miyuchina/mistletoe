import sys
from docs import build

build(sys.argv[1:] if len(sys.argv) > 1 else None)
