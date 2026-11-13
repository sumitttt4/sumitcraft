#!/bin/sh
# Unix wrapper. The real setup is setup.py (cross-platform). Shows the plan; add --yes to install.
exec python3 "$(dirname "$0")/setup.py" "$@"
