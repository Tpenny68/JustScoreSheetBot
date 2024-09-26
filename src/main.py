import asyncio
from os.path import dirname, realpath
import sys
import nest_asyncio
# Add project folder to sys.path
_project_path = dirname(dirname(realpath(__file__)))
sys.path.append(_project_path)

from src.scoreSheetBot import main

# nest_asyncio.apply()
asyncio.run(main())
