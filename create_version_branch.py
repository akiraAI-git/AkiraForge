#!/usr/bin/env python3
"""
Version Branch Manager for Akira Forge
This script creates new version branches following semantic versioning.
Version progression: 1.1 -> 1.1.2(stable) -> 1.1.3(experimental) -> ... -> 1.1.9 -> 1.2(stable)

Supports release stability levels:
  - (stable) - Production-ready releases
  - (experimental) - Beta/testing releases

NOT included in GitHub - LOCAL DEVELOPMENT ONLY
"""

import subprocess
import re
import sys
from typing import List, Tuple, Optional, Literal
from pathlib import Path


class VersionBranchManager:
    def __init__(self):
        self.repo_path = Path(__file__).parent
        self.version_file = self.repo_path / "VERSION"
        self.version_py_file = self.repo_path / "core" / "__version__.py"
        
    def run_git_command(self, command: List[str]) -> str:
        """Execute a git command and return output"""
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"❌ Git error: {e.stderr}")
            sys.exit(1)

    def get_all_version_branches(self) -> List[str]:
        """Get all version branches from remote and local"""
        try:
            # Get all branches (local and remote)
            output = self.run_git_command(["git", "branch", "-a"])
            branches = [b.strip().replace("remotes/origin/", "").replace("*", "").strip() for b in output.split("\n")]
            
            # Filter only version branches (semantic versioning pattern)
            version_pattern = re.compile(r"^\d+\.\d+(\.\d+)?$")
            version_branches = sorted(
                [b for b in branches if version_pattern.match(b)],
                key=lambda x: self._version_tuple(x),
                reverse=True
            )
            return version_branches
        except Exception as e:
            print(f"❌ Error getting branches: {e}")
            sys.exit(1)

    def _version_tuple(self, version_str: str) -> Tuple[int, ...]:
        """Convert version string to tuple for sorting"""
        return tuple(map(int, version_str.split(".")))

    def get_latest_version(self) -> str:
        """Get the latest version branch (without stability suffix)"""
        branches = self.get_all_version_branches()
        if not branches:
            print("⚠️  No version branches found. Using 1.1 as base.")
            return "1.1"
        return branches[0]
    
    def ask_stability(self) -> str:
        """Ask user to choose release stability"""
        print("\n🔧 Select Release Stability:")
        print("  1. (stable)        - Production-ready release")
        print("  2. (experimental)  - Beta/testing release")
        print("  3. (unstable)      - Development/unstable release")
        
        while True:
            choice = input("\nChoose stability level (1-3): ").strip()
            if choice == "1":
                return "stable"
            elif choice == "2":
                return "experimental"
            elif choice == "3":
                return "unstable"
            else:
                print("❌ Invalid option. Choose 1, 2, or 3.")
    
    def format_version_with_stability(self, version: str, stability: str) -> str:
        """Format version string with stability suffix"""
        return f"{version}({stability})"

    def calculate_next_version(self, current_version: str) -> str:
        """
        Calculate next version following the scheme:
        1.1 -> 1.1.2 -> 1.1.3 -> ... -> 1.1.9 -> 1.2
        """
        parts = current_version.split(".")
        
        if len(parts) == 2:
            # Format: 1.1 -> 1.1.2
            major, minor = int(parts[0]), int(parts[1])
            return f"{major}.{minor}.2"
        
        elif len(parts) == 3:
            # Format: 1.1.2 -> 1.1.3 or 1.1.9 -> 1.2
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
            
            if patch < 9:
                # Increment patch version
                return f"{major}.{minor}.{patch + 1}"
            else:
                # Rollover to next minor version
                return f"{major}.{minor + 1}"
        
        else:
            print(f"❌ Invalid version format: {current_version}")
            sys.exit(1)

    def update_version_file(self, version: str):
        """Update VERSION file"""
        version_file = self.repo_path / "VERSION"
        version_file.write_text(version + "\n")
        print(f"✓ Updated VERSION file to {version}")

    def update_version_py(self, version: str, stability: str):
        """Update __version__.py if it exists"""
        version_py = self.repo_path / "core" / "__version__.py"
        
        version_full = self.format_version_with_stability(version, stability)
        content = f'''"""
Akira Forge Version Information
Auto-generated by create_version_branch.py
"""

__version__ = "{version_full}"
__version_number__ = "{version}"
__stability__ = "{stability}"
__version_info__ = tuple(map(int, __version_number__.split(".")))
'''
        
        version_py.write_text(content)
        print(f"✓ Updated core/__version__.py to {version_full}")

    def create_branch(self, version: str, stability: str = None):
        """Create and checkout new version branch with stability"""
        try:
            # Ask for stability if not provided
            if stability is None:
                stability = self.ask_stability()
            
            # Format version with stability
            version_full = self.format_version_with_stability(version, stability)
            
            print(f"\n📦 Creating branch: {version_full}")
            
            # Create new branch from current branch
            self.run_git_command(["git", "checkout", "-b", version_full])
            print(f"✓ Created branch '{version_full}'")
            
            # Update version files
            self.update_version_file(version_full)
            self.update_version_py(version, stability)
            
            # Commit version changes
            self.run_git_command(["git", "add", "VERSION", "core/__version__.py"])
            self.run_git_command(["git", "commit", "-m", f"Release version {version_full}"])
            print(f"✓ Committed version {version_full}")
            
            print(f"\n✅ SUCCESS! Branch '{version_full}' created and ready.")
            print(f"   Push to GitHub with: git push -u origin {version_full}")
            
        except Exception as e:
            print(f"❌ Error creating branch: {e}")
            sys.exit(1)

    def list_versions(self):
        """List all existing version branches"""
        branches = self.get_all_version_branches()
        if not branches:
            print("No version branches found.")
            return
        
        print("\n📋 Existing Version Branches:")
        print("-" * 40)
        for i, branch in enumerate(branches, 1):
            is_latest = "✓ Latest" if i == 1 else ""
            print(f"  {i}. {branch:<15} {is_latest}")
        print("-" * 40)

    def interactive_mode(self):
        """Interactive mode for creating versions"""
        print("\n" + "=" * 50)
        print("🔧 AKIRA FORGE VERSION BRANCH MANAGER")
        print("=" * 50)
        
        current_version = self.get_latest_version()
        next_version = self.calculate_next_version(current_version)
        
        print(f"\n📌 Current Latest Version: {current_version}")
        print(f"📌 Next Version: {next_version}")
        print(f"💡 Stability options: (stable), (experimental), (unstable)")
        
        self.list_versions()
        
        print("\nOptions:")
        print("  1. Create new branch with auto-calculated version")
        print("  2. Create branch with custom version")
        print("  3. List all versions")
        print("  4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            stability = self.ask_stability()
            self.create_branch(next_version, stability)
        elif choice == "2":
            custom_version = input("Enter custom version (e.g., 1.3.5): ").strip()
            if re.match(r"^\d+\.\d+(\.\d+)?$", custom_version):
                stability = self.ask_stability()
                self.create_branch(custom_version, stability)
            else:
                print("❌ Invalid version format. Use format: 1.1 or 1.1.2")
        elif choice == "3":
            self.list_versions()
        elif choice == "4":
            print("Goodbye!")
        else:
            print("❌ Invalid option")

    def run(self, args: List[str] = None):
        """Main entry point"""
        if args and len(args) > 0:
            if args[0] == "list":
                self.list_versions()
            elif args[0] == "next":
                current = self.get_latest_version()
                next_ver = self.calculate_next_version(current)
                print(f"Latest: {current} → Next: {next_ver}")
            elif args[0] == "create":
                current = self.get_latest_version()
                next_ver = self.calculate_next_version(current)
                # Get stability from args or ask interactively
                stability = args[1] if len(args) > 1 else None
                if stability and stability not in ["stable", "experimental", "unstable"]:
                    print(f"❌ Invalid stability: {stability}")
                    print("Use: stable, experimental, or unstable")
                    sys.exit(1)
                self.create_branch(next_ver, stability)
            elif args[0] == "create-custom" and len(args) > 1:
                version = args[1]
                stability = args[2] if len(args) > 2 else None
                if stability and stability not in ["stable", "experimental", "unstable"]:
                    print(f"❌ Invalid stability: {stability}")
                    print("Use: stable, experimental, or unstable")
                    sys.exit(1)
                self.create_branch(version, stability)
            else:
                print("Usage:")
                print("  create_version_branch.py list                    - List all versions")
                print("  create_version_branch.py next                    - Show next version")
                print("  create_version_branch.py create [stability]      - Create next version")
                print("  create_version_branch.py create-custom X.Y [stability] - Create custom version")
                print("\nStability options: stable, experimental, unstable")
                print("(If not specified, you'll be asked to choose)")
        else:
            # Interactive mode
            self.interactive_mode()


def main():
    manager = VersionBranchManager()
    manager.run(sys.argv[1:] if len(sys.argv) > 1 else None)


if __name__ == "__main__":
    main()
