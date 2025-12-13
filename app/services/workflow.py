from langgraph.graph import StateGraph, END
from langgraph.memory import MemorySaver
from app.services.node import idea_node, beat_node, structure_node, scene_node, dialogue_node
from app.core.model import StoryState

workflow = StateGraph(StoryState)

# Add Nodes
workflow.add_node("generate_ideas", idea_node)
workflow.add_node("generate_beats", beat_node)
workflow.add_node("organize_structure", structure_node)
workflow.add_node("generate_scenes", scene_node)
workflow.add_node("generate_dialogue", dialogue_node)

# Set Entry Point (Optional, since we trigger nodes manually via API)
workflow.set_entry_point("generate_ideas")

# Add Edges (Linear flow - Optional for API usage but good for visualization)
workflow.add_edge("generate_ideas", "generate_beats")
workflow.add_edge("generate_beats", "organize_structure")
workflow.add_edge("organize_structure", "generate_scenes")
workflow.add_edge("generate_scenes", "generate_dialogue")
workflow.add_edge("generate_dialogue", END)

# Compile with Memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)