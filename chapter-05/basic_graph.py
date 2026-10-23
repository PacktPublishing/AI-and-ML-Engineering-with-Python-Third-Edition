from strands import Agent
from strands.multiagent import GraphBuilder
from strands.vended_tools.web_fetch import web_fetch

researcher = Agent(
    name="researcher",
    system_prompt="Gather comprehensive information from the web.",
    tools=[web_fetch],
)

analyst = Agent(
    name="analyst",
    system_prompt="Identify patterns, trends, and key insights from research.",
)

summarizer = Agent(
    name="summarizer",
    system_prompt="Condense raw research into concise key points.",
)

report_writer = Agent(
    name="report_writer",
    system_prompt="Synthesize analysis and summaries into a final report.",
)

builder = GraphBuilder()
builder.add_node(researcher, "research")
builder.add_node(analyst, "analysis")
builder.add_node(summarizer, "summarize")
builder.add_node(report_writer, "report")

builder.add_edge("research", "analysis")
builder.add_edge("research", "summarize")   # analyst + summarizer run in parallel
builder.add_edge("analysis", "report")
builder.add_edge("summarize", "report")      # report waits for both

builder.set_execution_timeout(600)
graph = builder.build()

result = graph("Research the impact of AI on healthcare")