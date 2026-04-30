import ast
import os
import re
from pathlib import Path
from typing import List

class SafeCodeCleaner:
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.files_processed = 0
        self.files_failed = []
        self.files_modified = 0
    
    def clean_directory(self, directory: str, recursive: bool = True) -> None:
        directory = Path(directory)
        
        if not directory.is_dir():
            print(f"Error: {directory} is not a directory")
            return
        
        pattern = "**/*.py" if recursive else "*.py"
        python_files = list(directory.glob(pattern))
        
        print(f"Found {len(python_files)} Python files to process")
        
        for file_path in python_files:
            self.clean_file(file_path)
        
        print(f"\nCleanup Summary:")
        print(f"  Files processed: {self.files_processed}")
        print(f"  Files modified: {self.files_modified}")
        print(f"  Files failed: {len(self.files_failed)}")
        
        if self.files_failed:
            print(f"\nFailed files:")
            for f in self.files_failed:
                print(f"  - {f}")
    
    def clean_file(self, file_path: Path) -> bool:
        self.files_processed += 1
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            ast.parse(original_content)
            
            cleaned_content = self._remove_docstrings_and_comments(original_content)
            
            ast.parse(cleaned_content)
            
            if cleaned_content != original_content:
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(cleaned_content)
                
                self.files_modified += 1
                return True
            
            return True
        
        except SyntaxError as e:
            print(f"[ERROR] Syntax error in {file_path}: {e}")
            self.files_failed.append(str(file_path))
            return False
        except Exception as e:
            print(f"[ERROR] Failed to process {file_path}: {e}")
            self.files_failed.append(str(file_path))
            return False
    
    def _remove_docstrings_and_comments(self, content: str) -> str:
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return content
        
        lines = content.split('\n')
        docstring_ranges = self._find_docstring_ranges(tree, lines)
        
        cleaned_lines = []
        for i, line in enumerate(lines):
            line_num = i + 1
            
            if self._is_in_docstring_range(line_num, docstring_ranges):
                if self._is_triple_quote_line(line, docstring_ranges, line_num):
                    cleaned_lines.append(line)
                continue
            
            cleaned_line = self._remove_comment(line)
            cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    def _find_docstring_ranges(self, tree: ast.AST, lines: List[str]) -> List:
        ranges = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                docstring = ast.get_docstring(node)
                
                if docstring and hasattr(node, 'lineno'):
                    start_line = node.lineno
                    
                    if isinstance(node, ast.Module):
                        if node.body and isinstance(node.body[0], ast.Expr):
                            if isinstance(node.body[0].value, ast.Constant):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno or start_line
                    else:
                        if node.body and isinstance(node.body[0], ast.Expr):
                            if isinstance(node.body[0].value, ast.Constant):
                                start_line = node.body[0].lineno
                                end_line = node.body[0].end_lineno or start_line
                    
                    try:
                        end_line = self._find_docstring_end_line(start_line - 1, lines, docstring)
                        ranges.append((start_line, end_line))
                    except:
                        pass
        
        return ranges
    
    def _find_docstring_end_line(self, start_idx: int, lines: List[str], docstring: str) -> int:
        quote_type = None
        line_idx = start_idx
        
        while line_idx < len(lines):
            line = lines[line_idx]
            
            if '"""' in line:
                if quote_type is None:
                    quote_type = '"""'
                elif quote_type == '"""':
                    return line_idx + 1
            elif "'''" in line:
                if quote_type is None:
                    quote_type = "'''"
                elif quote_type == "'''":
                    return line_idx + 1
            
            line_idx += 1
        
        return line_idx
    
    def _is_in_docstring_range(self, line_num: int, ranges: List) -> bool:
        for start, end in ranges:
            if start < line_num < end:
                return True
        return False
    
    def _is_triple_quote_line(self, line: str, ranges: List, line_num: int) -> bool:
        for start, end in ranges:
            if line_num == start or line_num == end:
                return '"""' in line or "'''" in line
        return False
    
    def _remove_comment(self, line: str) -> str:
        in_string = False
        string_char = None
        i = 0
        
        while i < len(line):
            char = line[i]
            
            if not in_string:
                if char in ('"', "'"):
                    if i + 2 < len(line) and line[i:i+3] in ('"""', "'''"):
                        in_string = True
                        string_char = line[i:i+3]
                        i += 2
                    else:
                        in_string = True
                        string_char = char
                elif char == '#':
                    return line[:i].rstrip()
            else:
                if len(string_char) == 3:
                    if i + 2 < len(line) and line[i:i+3] == string_char:
                        in_string = False
                        i += 2
                else:
                    if char == string_char and (i == 0 or line[i-1] != '\\'):
                        in_string = False
            
            i += 1
        
        return line

if __name__ == "__main__":
    cleaner = SafeCodeCleaner(dry_run=True)
    cleaner.clean_directory("C:\\akiraforge\\DesktopAIApp", recursive=True)
