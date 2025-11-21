import sys
import os

print("--- LLM ENGINE MEMORY ACCESS DEBUG ---")
print("Current Working Directory:", os.getcwd())

# 1. Try to import the CORE MEMORY package
try:
    import app.core.memory as memory_module
    print("✅ Successfully loaded app.core.memory module.")
    
    # 2. Check if the required functions exist within that module
    if hasattr(memory_module, 'get_history'):
        print("✅ Function 'get_history' FOUND in memory module.")
    else:
        # This means the function definition line itself failed in memory.py
        print("❌ CRITICAL: Function 'get_history' NOT found in memory module.")
        
    if hasattr(memory_module, 'add_message'):
        print("✅ Function 'add_message' FOUND in memory module.")
    else:
        print("❌ CRITICAL: Function 'add_message' NOT found in memory module.")

    # 3. Now, try to load the engine that consumes the package
    import app.services.llm_engine as engine
    print("✅ Successfully loaded llm_engine module.")

except ImportError as e:
    # This will catch if the module itself cannot be found
    print(f"❌ FATAL ImportError: {e}")
    print("\nSUGGESTION: Check __init__.py files.")
except Exception as e:
    # This catches crashes inside memory.py that happen during loading
    print(f"❌ RUNTIME Error during module initialization: {e}")


print("------------------------------------------")