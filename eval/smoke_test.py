"""Confirm the Gemini backend works end to end, using the real client
path (a persistent client, not an inline temporary that closes itself).

Run:  python eval/smoke_test.py
"""

import sys
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, "src")
from dotenv import load_dotenv

from leaseowl.llm_client import GeminiClient

load_dotenv()

client = GeminiClient()  # held alive; this is the pattern the eval uses
print("model:", client.model)
print("RESULT:", client.complete("Reply with exactly: OK"))
