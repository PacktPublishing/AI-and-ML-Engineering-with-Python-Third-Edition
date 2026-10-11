# Based on:
# Strands Agents — Persistent Memory with Session Managers

from strands import Agent
from strands.session import SnapshotSessionManager
from strands.storage import LocalFileStorage


session_manager = SnapshotSessionManager(
    session_id="customer-session-001",
    storage=LocalFileStorage("./sessions"),
)

agent = Agent(
    session_manager=session_manager,
)

agent("I'm investigating customer 12345.")

# Restart the process later with the same session ID.
# The latest agent/session state is restored automatically.