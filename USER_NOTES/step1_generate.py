import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

from core.project_generator import ProjectGenerator

output_dir = Path("C:/akiraforge/test_projects")
output_dir.mkdir(exist_ok=True)

project_path = output_dir / "TestSurfInstructor"

print("STEP 1: GENERATING AI PROJECT")
print("="*60)
print(f"Project Name: TestSurfInstructor")
print(f"Description: A professional surf instructor AI")
print(f"Location: {project_path}")
print()

try:
    result = ProjectGenerator.generate_project(
        path=project_path,
        description="A professional surf instructor that teaches different lessons",
        api_key=os.getenv("GROQ_API_KEY", "test_api_key"),
        model="llama-3.1-8b-instant",
        user_id=1
    )

    print("Project generated successfully!")
    print(f"Project location: {result}")

    files = list(project_path.iterdir())
    print(f"\nGenerated files ({len(files)} total):")
    for f in sorted(files):
        print(f"  - {f.name}")

    print("\nSTEP 1 STATUS: SUCCESS")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
