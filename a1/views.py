from django.http import HttpResponse
import os
import psutil
from datetime import datetime
import pytz

def htop_view(request):
    name = "Ahzam Saba"
    username = os.getenv("morph_cs", "ahzamsaba")

    ist = pytz.timezone('Asia/Kolkata')
    server_time = datetime.now(ist).strftime('%Y-%m-%d %H:%M:%S.%f')

    cpu_usage = psutil.cpu_percent(interval=1)
    load_avg = os.getloadavg() if hasattr(os, "getloadavg") else (0.0, 0.0, 0.0)
    memory_info = psutil.virtual_memory()

    buffers = getattr(memory_info, 'buffers', 0) / (1024 ** 2)  
    cached = getattr(memory_info, 'cached', 0) / (1024 ** 2)    

    top_header = f"""
    top - {datetime.now().strftime('%H:%M:%S')} up, {len(psutil.pids())} users, load average: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}
    Tasks: {len(psutil.pids())} total, {sum(1 for p in psutil.process_iter() if p.status() == 'running')} running, 
    CPU(s): {cpu_usage}% used
    MiB Mem : {memory_info.total / (1024 ** 2):.1f} total, {memory_info.available / (1024 ** 2):.1f} free, {memory_info.used / (1024 ** 2):.1f} used, {buffers:.1f} buff/cache
    """

    process_output = "PID USER    VIRT    RES  %CPU %MEM COMMAND\n"
    for proc in psutil.process_iter(['pid', 'username', 'memory_info', 'cpu_percent', 'name']):
        try:
            pid = proc.info['pid']
            user = proc.info['username'] or "unknown"
            virt = proc.memory_info().vms / (1024 ** 2)  
            res = proc.memory_info().rss / (1024 ** 2)  
            cpu_percent = proc.info['cpu_percent']
            mem_percent = proc.memory_percent()
            command = proc.info['name']

            process_output += f"{pid:<5} {user:<8} {virt:>7.1f} {res:>7.1f} {cpu_percent:>5.1f} {mem_percent:>5.1f} {command}\n"
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    response_content = f"""
    <html>
        <body>
            <h3>Name: {name}</h3>
            <h3>User: {username}</h3>
            <h3>Server Time (IST): {server_time}</h3>
            <h3>TOP output : </h3>
            <pre>{top_header}</pre>
            <pre>{process_output}</pre>
        </body>
    </html>
    """

    return HttpResponse(response_content)
