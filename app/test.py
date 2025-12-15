# test_graph.py
import asyncio
from app.services.workflow import app as graph_app

# Mock Inputs
initial_input = {
    "topic": "A Cyberpunk Detective who is actually a toaster",
    "feedback": None
}

async def run_test():
    print("--- 1. STARTING IDEA GENERATION ---")
    # We call the graph. config tells it which thread (session) to use.
    config = {"configurable": {"thread_id": "test_session_1"}}
    
    # Run the Idea Node (Simulating API Trigger)
    # Note: In a real run, we might just let it flow, but here we invoke specific updates.
    
    # Step 1: Ideas
    print("Generating Ideas...")
    # We invoke the graph with the input. The graph handles the flow.
    # Since we set entry point to idea_node, it starts there.
    state_after_ideas = await graph_app.ainvoke(initial_input, config=config,count=2)
    print("Ideas Generated:", state_after_ideas['generated_ideas'])
    
    # Step 2: Simulate User Selection
    selected = state_after_ideas['generated_ideas'][0] # Pick the first one
    print(f"\nUser Selected: {selected['title']}")
    
    # Update State with Selection
    input_step_2 = {
        "selected_idea": selected,
        "feedback": None
    }
    
    print("\n--- 2. GENERATING BEATS ---")
    # We resume the graph. It updates the state. 
    # To force the 'beat_node' to run, we might need to adjust the workflow or just trust the state update if edges are set.
    # BUT, since our edges are linear in the file I gave you, just calling invoke again with the new state usually triggers the next step IF edges are correct.
    # However, for manual stepping (which is what your API does), we usually invoke specific nodes.
    # Let's just update the state and let LangGraph figure it out? 
    # Actually, the best way to test YOUR specific 'Steppable' architecture 
    # is to run the specific node logic or use graph.update_state if using persistence heavily.
    
    # SIMPLIFIED TEST: Just feeding inputs to the graph function.
    # Since your graph has linear edges (Idea -> Beat), it might try to run everything at once if we aren't careful.
    # Let's just assume we want to run the next step.
    
    # For this test, let's just re-invoke with the new state data.
    state_after_beats = await graph_app.ainvoke(input_step_2, config=config)
    print("Beats Generated:", state_after_beats['beats'])
    
    # Step 3: Structure
    print("\n--- 3. ORGANIZING STRUCTURE ---")
    state_after_structure = await graph_app.ainvoke({"feedback": None}, config=config)
    print("Structure:", state_after_structure['structure'])

    # Step 4: Scenes (Hook)
    print("\n--- 4. GENERATING HOOK SCENES ---")
    input_hook = {
        "current_section_name": "hook",
        "feedback": None
    }
    state_after_hook = await graph_app.ainvoke(input_hook, config=config)
    print("Hook Scenes:", state_after_hook['scenes'])

    # Step 5: Scenes (Mid - The Context Test)
    print("\n--- 5. GENERATING MID SCENES (Checking Context) ---")
    input_mid = {
        "current_section_name": "mid",
        "feedback": None
    }
    state_after_mid = await graph_app.ainvoke(input_mid, config=config)
    print("Mid Scenes:", state_after_mid['scenes'])
    
    # Validation: Check if all_scenes has both
    print("\n--- VALIDATION ---")
    print(f"Total Scenes in Memory: {len(state_after_mid['all_scenes'])}")
    if len(state_after_mid['all_scenes']) > len(state_after_mid['scenes']):
         print("SUCCESS: Memory is accumulating!")
    else:
         print("FAILURE: Memory is not sticking.")

if __name__ == "__main__":
    asyncio.run(run_test())