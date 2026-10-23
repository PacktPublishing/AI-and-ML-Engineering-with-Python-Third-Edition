from strands import Agent
from strands.experimental.hooks.multiagent import BeforeNodeCallEvent
from strands.hooks import HookProvider
from strands.interrupt import Interrupt
from strands.multiagent import GraphBuilder
from strands.multiagent.base import Status


class ApprovalHook(HookProvider):
    def register_hooks(self, registry):
        registry.add_callback(BeforeNodeCallEvent, self.approve)

    def approve(self, event):
        if event.node_id == "txn_analysis":
            return

        response = event.interrupt("my_interrupt", reason=f"{event.node_id} needs approval")
        if response != "APPROVE":
            event.cancel_node = "node rejected"


context_retriever = Agent(
    name="context_retriever",
    tools=[fetch_customer_context]
)

txn_analyser = Agent(
    name="txn_analysis",
    tools=[fetch_txn_metadata]
)

analyst = Agent(
    name="analyst", 
    system_prompt="Analyse all context available with a view to product recommendation."
    )

recommender = Agent(
    name="recommender",
    system_prompt="Recommend a product for the customer"
)

builder = GraphBuilder()
builder.add_node(context_retriever, "context_retriever")
builder.add_node(txn_analyser, "txn_analysis")
builder.add_node(analyst, "analysis")
builder.add_node(recommender, "recommend")

builder.add_edge("context_retriever", "txn_analysis")
builder.add_edge("txn_analysis", "recommender")
builder.set_hook_providers([ApprovalHook()])
graph = builder.build()

multiagent_result = graph("Given this customer, what products can we recommend?")
while multiagent_result.status == Status.INTERRUPTED:
    responses = []
    for interrupt in multiagent_result.interrupts:
        if interrupt.name == "my_interrupt":
            response = input(f"{interrupt.reason} (y/N): ")
            responses.append(
                {
                    "interruptResponse": {
                         "interruptId": interrupt.id,
                         "response": response,
                    },
                },
             )

    multiagent_result = graph(responses)

print(multiagent_result.results)