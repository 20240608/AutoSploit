#!/usr/bin/env python3
import os

os.chdir('/AutoSploit')

# 1. 替换所有 raw_input 为 input
print("[*] Replacing raw_input with input in all .py files...")
os.system("find . -name '*.py' -type f -exec sed -i 's/raw_input/input/g' {} \\;")

# 2. 修复 print 语句
print("[*] Fixing print statements...")
os.system("sed -i 's/print error_traceback/print(error_traceback)/g' autosploit/main.py")

# 3. 添加 Docker 环境检测到 main.py
print("[*] Adding Docker environment detection...")
with open('autosploit/main.py', 'r') as f:
    lines = f.readlines()

# Validate that we can find the expected code structure
service_check_found = any('misc_info("checking for disabled services")' in line for line in lines)
if not service_check_found:
    print("[!] Warning: Could not find service check line in main.py - skipping Docker detection modification")
else:
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Look for the service check line
        if 'misc_info("checking for disabled services")' in line:
            # Get the indentation of this line
            base_indent = len(line) - len(line.lstrip())
            base_indent_str = ' ' * base_indent
            extra_indent = '    '
            
            # Insert Docker environment check
            new_lines.append(f'{base_indent_str}# Check if running in Docker environment\n')
            new_lines.append(f'{base_indent_str}is_docker = os.path.exists("/.dockerenv")\n')
            new_lines.append(f'{base_indent_str}\n')
            new_lines.append(f'{base_indent_str}if is_docker:\n')
            new_lines.append(f'{base_indent_str}{extra_indent}info("running in Docker environment, skipping local service checks")\n')
            new_lines.append(f'{base_indent_str}else:\n')
            
            # Add the service check block with extra indentation
            # Continue until we find the line "if len(sys.argv)"
            while i < len(lines):
                current_line = lines[i]
                
                # Stop when we reach "if len(sys.argv)"
                if 'if len(sys.argv)' in current_line:
                    new_lines.append(current_line)
                    i += 1
                    break
                
                # Add extra indentation (4 spaces) to the beginning of each non-empty line
                if current_line.strip():
                    new_lines.append(extra_indent + current_line)
                else:
                    new_lines.append(current_line)
                i += 1
        else:
            new_lines.append(line)
            i += 1

    with open('autosploit/main.py', 'w') as f:
        f.writelines(new_lines)

print("[+] All fixes applied successfully!")
