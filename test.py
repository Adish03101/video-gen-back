import asyncio
import json
from dotenv import load_dotenv

# 1. Load environment variables (This finds your .env file)
load_dotenv()

# 2. Import your Logic and Schemas
from app.services.llm_engine import generate_video_ideas, generate_video_script
from app.core.schemas import IdeaRequest, ScriptRequest

async def main():
    print("🚀 Starting Backend Test...\n")

    # ==========================================
    # TEST 1: Generate Ideas
    # ==========================================
    print("--- Testing Idea Generation ---")
    try:
        idea_req = IdeaRequest(topic="Time Travel Paradoxes", audience="Sci-Fi Fans")
        
        # Call the function
        ideas = await generate_video_ideas(idea_req, count=3)
        
        # Print nicely
        print(f"✅ Success! Generated {len(ideas.ideas)} ideas.")
        print(json.dumps(ideas.model_dump(), indent=2))
        
        # Save the first idea for the next test
        best_idea = ideas.ideas[0]
        
    except Exception as e:
        print(f"❌ Idea Gen Failed: {e}")
        return

    # ==========================================
    # TEST 2: Generate Script (using the idea from above)
    # ==========================================
    print("\n--- Testing Script Generation ---")
    print(f"Writing script for: '{best_idea.title}'...")
    
    try:
        script_req = ScriptRequest(
            title=best_idea.title,
            tone="Mind-bending",
            target_duration=30 # Short 30s script for testing
        )
        
        # Call the function
        script = await generate_video_script(script_req)
        
        print("✅ Success! Script Generated.")
        print(f"Title: {script.title}")
        print(f"Characters Found: {script.characters_detected}")
        print(f"Preview: {script.full_script[:100]}...") # Show first 100 chars
        
    except Exception as e:
        print(f"❌ Script Gen Failed: {e}")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())