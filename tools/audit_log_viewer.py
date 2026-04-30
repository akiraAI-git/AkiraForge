#!/usr/bin/env python3
"""
Audit Log Viewer - Admin Tool
=============================

View and analyze audit logs from the AkiraForge audit logger.

Usage:
    python tools/audit_log_viewer.py [options]
    
Options:
    --important    Show only important (encrypted) logs
    --public       Show only public logs
    --filter USERNAME  Filter by specific user
    --action ACTION    Filter by specific action
    --limit N      Show last N entries
    --export FILE  Export to CSV/JSON
    --verify       Verify log signatures (requires security key)
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import argparse

class AuditLogViewer:
    def __init__(self):
        self.log_dir = Path.home() / ".akiraforge" / "audit_logs"
        
    def load_logs(self, log_type: str = "public") -> List[Dict[str, Any]]:
        """Load logs from file."""
        if log_type == "important":
            log_file = self.log_dir / "important_actions.log"
        elif log_type == "hidden":
            log_file = self.log_dir / "hidden_actions.log"
        else:
            log_file = self.log_dir / "public_actions.log"
        
        if not log_file.exists():
            return []
        
        logs = []
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        if log_type == "important":
                            entry = json.loads(line)
                            logs.append(entry["data"])
                        else:
                            logs.append(json.loads(line))
        except Exception as e:
            print(f"Error loading logs: {e}")
        
        return logs
    
    def filter_logs(self, logs: List[Dict], username: Optional[str] = None,
                   action: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
        """Filter logs by criteria."""
        filtered = logs
        
        if username:
            filtered = [l for l in filtered if l.get("username") == username]
        
        if action:
            filtered = [l for l in filtered if l.get("action") == action]
        
        if limit:
            filtered = filtered[-limit:]
        
        return filtered
    
    def format_timestamp(self, iso_timestamp: str) -> str:
        """Format ISO timestamp to readable format."""
        try:
            dt = datetime.fromisoformat(iso_timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return iso_timestamp
    
    def print_logs(self, logs: List[Dict], show_details: bool = True):
        """Print logs in formatted table."""
        if not logs:
            print("No logs found.")
            return
        
        print("\n" + "="*100)
        print("AUDIT LOG VIEWER")
        print("="*100)
        print(f"{'Timestamp':<20} {'User':<15} {'Action':<25} {'Details':<40}")
        print("-"*100)
        
        for log in logs:
            timestamp = self.format_timestamp(log.get("timestamp", ""))
            username = log.get("username", "unknown")[:15]
            action = log.get("action", "unknown")[:25]
            
            details = ""
            if show_details and log.get("details"):
                details_dict = log["details"]
                detail_items = [f"{k}={v}" for k, v in details_dict.items()]
                details = ", ".join(detail_items)[:40]
            
            print(f"{timestamp:<20} {username:<15} {action:<25} {details:<40}")
        
        print("="*100)
        print(f"Total entries: {len(logs)}\n")
    
    def print_summary(self, logs: List[Dict]):
        """Print summary statistics."""
        if not logs:
            print("No logs to summarize.")
            return
        
        print("\n" + "="*60)
        print("AUDIT LOG SUMMARY")
        print("="*60)
        
        # By user
        by_user = {}
        for log in logs:
            user = log.get("username", "unknown")
            by_user[user] = by_user.get(user, 0) + 1
        
        print("\nActions by User:")
        for user, count in sorted(by_user.items(), key=lambda x: x[1], reverse=True):
            print(f"  {user:<20} {count:>5} actions")
        
        # By action
        by_action = {}
        for log in logs:
            action = log.get("action", "unknown")
            by_action[action] = by_action.get(action, 0) + 1
        
        print("\nActions by Type:")
        for action, count in sorted(by_action.items(), key=lambda x: x[1], reverse=True):
            print(f"  {action:<20} {count:>5} times")
        
        # Recent activity
        if logs:
            first_log = logs[0]
            last_log = logs[-1]
            first_time = self.format_timestamp(first_log.get("timestamp", ""))
            last_time = self.format_timestamp(last_log.get("timestamp", ""))
            
            print(f"\nTime Range:")
            print(f"  First: {first_time}")
            print(f"  Last:  {last_time}")
        
        print("="*60 + "\n")
    
    def export_logs(self, logs: List[Dict], filepath: str, format_type: str = "json"):
        """Export logs to file."""
        try:
            output_path = Path(filepath)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format_type == "json":
                with open(output_path, 'w') as f:
                    json.dump(logs, f, indent=2)
            
            elif format_type == "csv":
                import csv
                if logs:
                    with open(output_path, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=logs[0].keys())
                        writer.writeheader()
                        for log in logs:
                            writer.writerow(log)
            
            else:
                with open(output_path, 'w') as f:
                    for log in logs:
                        f.write(json.dumps(log) + "\n")
            
            print(f"✓ Exported {len(logs)} logs to {output_path}")
            return True
        
        except Exception as e:
            print(f"✗ Failed to export: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(
        description="View and analyze AkiraForge audit logs"
    )
    parser.add_argument("--important", action="store_true", help="Show important logs only")
    parser.add_argument("--public", action="store_true", help="Show public logs only")
    parser.add_argument("--hidden", action="store_true", help="Show hidden logs")
    parser.add_argument("--filter-user", type=str, help="Filter by username")
    parser.add_argument("--filter-action", type=str, help="Filter by action type")
    parser.add_argument("--limit", type=int, help="Show last N entries")
    parser.add_argument("--export", type=str, help="Export to file (CSV/JSON)")
    parser.add_argument("--format", choices=["csv", "json"], default="json", help="Export format")
    parser.add_argument("--summary", action="store_true", help="Show summary statistics")
    
    args = parser.parse_args()
    
    viewer = AuditLogViewer()
    
    # Determine which logs to show
    if args.important:
        logs = viewer.load_logs("important")
        print("\n[Important Logs Only - Encrypted]")
    elif args.hidden:
        logs = viewer.load_logs("hidden")
        print("\n[Hidden Logs Only]")
    else:
        logs = viewer.load_logs("public")
        print("\n[Public Logs]")
    
    # Apply filters
    if args.filter_user or args.filter_action or args.limit:
        logs = viewer.filter_logs(
            logs,
            username=args.filter_user,
            action=args.filter_action,
            limit=args.limit
        )
    
    # Show summary if requested
    if args.summary:
        viewer.print_summary(logs)
    else:
        viewer.print_logs(logs)
    
    # Export if requested
    if args.export:
        viewer.export_logs(logs, args.export, args.format)

if __name__ == "__main__":
    main()
