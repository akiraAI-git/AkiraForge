import os
from dotenv import load_dotenv
from pathlib import Path
import sys

load_dotenv()

project_path = Path("C:/akiraforge/test_projects/TestSurfInstructor")

print("STEP 2: VERIFY GENERATED PROJECT RUNS")
print("="*60)
print(f"Testing project at: {project_path}")
print()

try:
    os.chdir(project_path)
    sys.path.insert(0, str(project_path))

    print("Testing: Can we import the agent module?")
    from agent import Agent
    print("Success! Agent module imported")

    print("\nTesting: Can we create an Agent instance?")
    agent = Agent()
    print(f"Success! Agent created: {agent.ai_name}")
    print(f"  - AI ID: {agent.ai_id}")
    print(f"  - Model: {agent.model}")
    print(f"  - API Key loaded: {bool(agent.client)}")

    print("\nChecking generated files for syntax errors...")
    files_to_check = [
        project_path / "gui" / "main_window.py",
        project_path / "gui_runner.py",
        project_path / "agent.py",
        project_path / "main.py"
    ]

    for file_path in files_to_check:
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                compile(code, str(file_path), 'exec')
                print(f"  - {file_path.name}: Valid Python syntax")
            except SyntaxError as e:
                print(f"  - {file_path.name}: SYNTAX ERROR - {e}")
                raise
        else:
            print(f"  - {file_path.name}: NOT FOUND")

    print("\nSTEP 2 STATUS: SUCCESS")
    print("Generated project is ready to use!")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
