#!/usr/bin/env python3
import subprocess
import sys
import time
import socket
import argparse
import os
import signal
import psutil  # You'll need to install this package

def check_redis_running():
    """Check if Redis server is running by attempting to connect to it"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(('localhost', 6379))
        s.close()
        return True
    except:
        return False

def find_redis_pid():
    """Find the PID of the Redis server process"""
    try:
        # Method 1: Use netstat to find process using port 6379
        if sys.platform == 'win32':
            output = subprocess.check_output('netstat -ano | findstr :6379', shell=True).decode()
            if output:
                for line in output.splitlines():
                    if 'LISTENING' in line:
                        parts = line.strip().split()
                        return int(parts[-1])
        else:
            # For Linux/WSL
            try:
                output = subprocess.check_output('netstat -nlp | grep :6379', shell=True).decode()
                if output:
                    for line in output.splitlines():
                        if 'LISTEN' in line:
                            pid_part = line.split('LISTEN')[1].strip()
                            pid = pid_part.split('/')[0]
                            return int(pid)
            except:
                pass
                
            # Alternative method using lsof
            try:
                output = subprocess.check_output('lsof -i :6379 -t', shell=True).decode()
                if output:
                    return int(output.strip())
            except:
                pass

        # Method 2: Use psutil to find the redis-server process
        for proc in psutil.process_iter(['pid', 'name']):
            if 'redis-server' in proc.info['name']:
                return proc.info['pid']
    except Exception as e:
        print(f"Error finding Redis PID: {str(e)}")
    
    return None

def start_redis():
    """Start Redis server if not already running"""
    if check_redis_running():
        print("Redis is already running on port 6379")
        return True
    
    try:
        # Start Redis in background
        print("Starting Redis server...")
        subprocess.Popen(["redis-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for Redis to start
        for _ in range(5):  # Try 5 times
            time.sleep(1)
            if check_redis_running():
                print("Redis server started successfully")
                return True
        
        print("Failed to start Redis server")
        return False
    except Exception as e:
        print(f"Error starting Redis: {str(e)}")
        return False

def stop_redis():
    """Stop Redis server if running"""
    if not check_redis_running():
        print("Redis is not running")
        return True
    
    # Try the graceful shutdown first
    try:
        print("Attempting graceful shutdown with redis-cli...")
        result = subprocess.run(["sudo systemctl stop redis"], capture_output=True, text=True, timeout=5)
        
        # Wait a moment to see if it worked
        time.sleep(2)
        if not check_redis_running():
            print("Redis server stopped successfully using redis-cli")
            return True
        else:
            print(f"redis-cli shutdown attempt failed: {result.stderr}")
    except Exception as e:
        print(f"Error during graceful shutdown: {str(e)}")
    
    # Try to find and kill the Redis process
    redis_pid = find_redis_pid()
    if redis_pid:
        print(f"Found Redis running with PID {redis_pid}, attempting to terminate...")
        
        # Try multiple termination methods depending on platform
        try:
            if sys.platform == 'win32':
                # Windows
                subprocess.run(['taskkill', '/F', '/PID', str(redis_pid)])
            else:
                # Linux/WSL - try SIGTERM first
                try:
                    os.kill(redis_pid, signal.SIGTERM)
                    print(f"Sent SIGTERM to Redis process {redis_pid}")
                except Exception as e:
                    print(f"SIGTERM failed: {str(e)}")
                    
                # If failed, try with sudo (this will prompt for password)
                if check_redis_running():
                    print("Attempting to stop Redis with sudo (you may be prompted for password)...")
                    try:
                        subprocess.run(['sudo', 'kill', str(redis_pid)])
                    except Exception as e:
                        print(f"sudo kill failed: {str(e)}")
                
                # Last resort, try SIGKILL
                if check_redis_running():
                    try:
                        print("Trying SIGKILL...")
                        os.kill(redis_pid, signal.SIGKILL)
                    except Exception as e:
                        print(f"SIGKILL failed: {str(e)}")
        except Exception as e:
            print(f"Error terminating process: {str(e)}")
    else:
        print("Could not find Redis process ID")
    
    # Final check
    if check_redis_running():
        print("\nWARNING: Redis is still running. You may need to:")
        print("1. Run this script with administrator/sudo privileges")
        print("2. Manually kill the process:")
        print("   - On Windows: Task Manager > Details > find redis-server.exe > End task")
        print("   - On Linux/WSL: sudo pkill redis-server")
        print("3. Restart your system if all else fails")
        return False
    else:
        print("Redis server has been stopped")
        return True

def redis_status():
    """Check if Redis is running and print status information"""
    is_running = check_redis_running()
    status = "running" if is_running else "not running"
    print(f"Redis server is {status}")
    
    if is_running:
        redis_pid = find_redis_pid()
        if redis_pid:
            print(f"Redis server process ID: {redis_pid}")
        
        try:
            # Get Redis server info
            process = subprocess.run(
                ["redis-cli", "info"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            info = process.stdout
            
            # Extract useful information
            redis_version = None
            uptime = None
            connected_clients = None
            used_memory_human = None
            
            for line in info.splitlines():
                if line.startswith("redis_version:"):
                    redis_version = line.split(":")[1].strip()
                elif line.startswith("uptime_in_seconds:"):
                    uptime_seconds = int(line.split(":")[1].strip())
                    uptime = f"{uptime_seconds // 3600}h {(uptime_seconds % 3600) // 60}m {uptime_seconds % 60}s"
                elif line.startswith("connected_clients:"):
                    connected_clients = line.split(":")[1].strip()
                elif line.startswith("used_memory_human:"):
                    used_memory_human = line.split(":")[1].strip()
            
            print(f"Redis version: {redis_version}")
            print(f"Uptime: {uptime}")
            print(f"Connected clients: {connected_clients}")
            print(f"Memory used: {used_memory_human}")
        except Exception as e:
            print(f"Error fetching Redis info: {str(e)}")
    
    return is_running

def restart_redis():
    """Restart Redis server"""
    stop_redis()
    time.sleep(1)
    return start_redis()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Redis Server Manager")
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status', 'force-stop'],
                      help='Action to perform on Redis server')
    
    args = parser.parse_args()
    
    if args.action == 'start':
        start_redis()
    elif args.action == 'stop':
        stop_redis()
    elif args.action == 'restart':
        restart_redis()
    elif args.action == 'status':
        redis_status()
    elif args.action == 'force-stop':
        # Direct method for non-interactive environments
        print("Attempting forceful Redis shutdown...")
        redis_pid = find_redis_pid()
        if redis_pid:
            print(f"Found Redis with PID {redis_pid}, forcefully terminating...")
            try:
                if sys.platform != 'win32':
                    subprocess.run(['sudo', 'kill', '-9', str(redis_pid)])
                else:
                    subprocess.run(['taskkill', '/F', '/PID', str(redis_pid)])
                print("Force stop command sent")
            except Exception as e:
                print(f"Force stop failed: {str(e)}")
        else:
            print("Could not find Redis process to terminate")
