"""Simple bot runner script."""

import asyncio
import os
from dotenv import load_dotenv
from app.main import main

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    print("Starting cafe bot...")
    asyncio.run(main())