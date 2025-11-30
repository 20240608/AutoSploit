#!/usr/bin/env python3
import os

os.chdir('/AutoSploit')

# 1. 替换所有 raw_input 为 input
print("[*] Replacing raw_input with input in all . py files...")
os.system("find . -name '*.py' -type f -exec sed -i 's/raw_input/input/g' {} \\;")

# 2. 修复 print 语句
print("[*] Fixing print statements...")
os.system("sed -i 's/print error_traceback/print(error_traceback)/g' autosploit/main.py")

# 3. 添加 Docker 环境检测到 main.py
print("[*] Adding Docker environment detection...")
with open('autosploit/main.py', 'r') as f:
    content = f. read()

# 替换服务检查部分
old = '''        misc_info("checking for disabled services")
        # according to ps aux, postgre and apache2 are the names of the services on Linux systems
        service_names = ("postgres", "apache2")
        try:
            for service in list(service_names):
                while not check_services(service):
                    if "darwin" in platform_running. lower():
                        info(
                            "seems you're on macOS, skipping service checks "
                            "(make sure that Apache2 and PostgreSQL are running)"
                        )
                        break
                    choice = prompt(
                        "it appears that service {} is not enabled, would you like us to enable it for you[y/N]". format(
                            service. title()
                        )
                    )
                    if choice.lower(). startswith("y"):
                        try:
                            if "linux" in platform_running.lower():
                                cmdline("{} linux".format(START_SERVICES_PATH))
                            else:
                                close("your platform is not supported by AutoSploit at this time", status=2)

                            # moving this back because it was funky to see it each run
                            info("services started successfully")
                        # this tends to show up when trying to start the services
                        # I'm not entirely sure why, but this fixes it
                        except psutil.NoSuchProcess:
                            pass
                    else:
                        process_start_command = "`sudo service {} start`"
                        if "darwin" in platform_running. lower():
                            process_start_command = "`brew services start {}`"
                        close(
                            "service {} is required to be started for autosploit to run successfully (you can do it manually "
                            "by using the command {}), exiting". format(
                                service.title(), process_start_command. format(service)
                            )
                        )
        except Exception:
            pass'''

new = '''        # 检查是否在 Docker 环境中运行
        is_docker = os.path. exists("/.dockerenv")
        
        if is_docker:
            info("running in Docker environment, skipping local service checks")
        else:
            misc_info("checking for disabled services")
            # according to ps aux, postgre and apache2 are the names of the services on Linux systems
            service_names = ("postgres", "apache2")
            try:
                for service in list(service_names):
                    while not check_services(service):
                        if "darwin" in platform_running.lower():
                            info(
                                "seems you're on macOS, skipping service checks "
                                "(make sure that Apache2 and PostgreSQL are running)"
                            )
                            break
                        choice = prompt(
                            "it appears that service {} is not enabled, would you like us to enable it for you[y/N]". format(
                                service.title()
                            )
                        )
                        if choice.lower().startswith("y"):
                            try:
                                if "linux" in platform_running.lower():
                                    cmdline("{} linux".format(START_SERVICES_PATH))
                                else:
                                    close("your platform is not supported by AutoSploit at this time", status=2)

                                # moving this back because it was funky to see it each run
                                info("services started successfully")
                            # this tends to show up when trying to start the services
                            # I'm not entirely sure why, but this fixes it
                            except psutil. NoSuchProcess:
                                pass
                        else:
                            process_start_command = "`sudo service {} start`"
                            if "darwin" in platform_running.lower():
                                process_start_command = "`brew services start {}`"
                            close(
                                "service {} is required to be started for autosploit to run successfully (you can do it manually "
                                "by using the command {}), exiting".format(
                                    service.title(), process_start_command.format(service)
                                )
                            )
            except Exception:
                pass'''

content = content.replace(old, new)

with open('autosploit/main.py', 'w') as f:
    f.write(content)

print("[+] All fixes applied successfully!")
