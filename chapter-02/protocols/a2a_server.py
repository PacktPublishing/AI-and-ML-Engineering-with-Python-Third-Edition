# # A minimal A2A agent still requires three things MCP doesn't:

# class EchoExecutor(AgentExecutor):
#     async def execute(self, context, event_queue):
#         # drive the task lifecycle: create task -> add artifact -> mark complete
#         ...

# card = AgentCard(name="Echo Agent", skills=[...], ...)   # 1. discovery contract

# handler = DefaultRequestHandler(
#     agent_executor=EchoExecutor(),      # 2. your logic, wrapped in task lifecycle
#     task_store=InMemoryTaskStore(),     # 3. tasks are stateful, not fire-and-forget
#     agent_card=card,
# )
# # served over HTTP via Starlette routes — full listing in the repo.
"""
a2a_server.py — the smallest A2A agent the protocol allows.

Even minimal, A2A needs three things MCP doesn't:
  1. An Agent Card   (discovery: what can this agent do?)
  2. An Agent Executor (your logic, driven through the task lifecycle)
  3. A task store    (A2A tasks are stateful, not fire-and-forget)

Dependencies: uv pip install a2a-sdk uvicorn
"""

import uvicorn

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.helpers import new_task_from_user_message, new_text_part
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill, TaskState
from starlette.applications import Starlette


class EchoExecutor(AgentExecutor):
    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        task = context.current_task or new_task_from_user_message(context.message)
        if not context.current_task:
            await event_queue.enqueue_event(task)

        updater = TaskUpdater(event_queue, task_id=task.id, context_id=task.context_id)
        await updater.add_artifact(parts=[new_text_part(text="Hello from the agent!")])
        await updater.update_status(state=TaskState.TASK_STATE_COMPLETED)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise NotImplementedError


if __name__ == "__main__":
    card = AgentCard(
        name="Echo Agent",
        description="A stub agent that always says hello.",
        version="0.0.1",
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        capabilities=AgentCapabilities(streaming=False),
        supported_interfaces=[
            AgentInterface(
                protocol_binding="JSONRPC",
                url="http://127.0.0.1:9999",
                protocol_version="1.0",
            )
        ],
        skills=[
            AgentSkill(
                id="echo",
                name="Echo",
                description="Says hello.",
                tags=["example"],
            )
        ],
    )

    handler = DefaultRequestHandler(
        agent_executor=EchoExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=card,
    )

    routes = create_agent_card_routes(card) + create_jsonrpc_routes(handler, "/")
    uvicorn.run(Starlette(routes=routes), host="127.0.0.1", port=9999)