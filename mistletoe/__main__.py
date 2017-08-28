"""
Make mistletoe runnable as a script with default settings.
"""

import sys
from mistletoe.convert import convert
from mistletoe.interactive import interactive


def main():
    """
    Entry point. Select mode based on len(sys.argv).
    """
    if len(sys.argv) > 1:
        convert(*sys.argv[1:])
    else:
        interactive()

if __name__ == "__main__":
    main()
