#!/usr/bin/env python3
import subprocess
import time
import logging
import datetime

# Setup logging
logging.basicConfig(filename='wireguard_monitor.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s')

def monitor_connections():
    """Monitor WireGuard connections and log them"""
    known_peers = set()
    
    while True:
        try:
            result = subprocess.run(["sudo", "wg", "show", "server"], capture_output=True, text=True)
            if result.returncode == 0:
                output = result.stdout
                current_peers = set()
                
                lines = output.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('peer:'):
                        peer = line.split(': ')[1]
                        current_peers.add(peer)
                        
                        # Check next line for handshake info
                        if i + 1 < len(lines) and 'latest handshake:' in lines[i + 1]:
                            handshake_line = lines[i + 1].strip()
                            
                            if peer not in known_peers:
                                logging.info(f"New connection: {peer}")
                                print(f"[{datetime.datetime.now()}] New connection: {peer}")
                                known_peers.add(peer)
                            elif 'latest handshake:' in handshake_line and 'ago' in handshake_line:
                                logging.info(f"Active connection: {peer} - {handshake_line}")
                
                # Check for disconnected peers
                disconnected = known_peers - current_peers
                for peer in disconnected:
                    logging.info(f"Disconnected: {peer}")
                    print(f"[{datetime.datetime.now()}] Disconnected: {peer}")
                    known_peers.remove(peer)
                    
        except Exception as e:
            logging.error(f"Monitor error: {e}")
            
        time.sleep(30)  # Check every 30 seconds

if __name__ == '__main__':
    print("Starting WireGuard connection monitor...")
    print(f"[{datetime.datetime.now()}] Monitor started")
    logging.info("WireGuard connection monitor started")
    monitor_connections()