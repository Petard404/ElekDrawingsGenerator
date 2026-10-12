"""Allow `python -m huiselek`, the documented way to start the tool."""

import sys

from huiselek.cli import main

sys.exit(main())
