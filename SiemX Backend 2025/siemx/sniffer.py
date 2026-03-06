from scapy.all import sniff, IP, TCP, Raw
from datetime import datetime
import os

ROUTER_IP = "192.168.1.1"
LOG_FILE = os.path.join(os.path.dirname(__file__), "received.log")

def packet_handler(pkt):
    if IP in pkt and TCP in pkt:
        src = pkt[IP].src
        dst = pkt[IP].dst
        sport = pkt[TCP].sport
        dport = pkt[TCP].dport
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Capture traffic TO and FROM router
        if src == ROUTER_IP or dst == ROUTER_IP:
            direction = "REQUEST" if dst == ROUTER_IP else "RESPONSE"

            if Raw in pkt:
                try:
                    payload = pkt[Raw].load.decode(errors="ignore")
                except:
                    payload = repr(pkt[Raw].load)
            else:
                payload = "<NO BODY>"

            '''print(f"[{ts}] {direction}")
            print(f"{src}:{sport} → {dst}:{dport}")
            print("BODY:")
            print(payload)
            print("-" * 70)'''
            if any(word in payload for word in ['ERROR', 'invalid', 'wrong']):
                print('Failed Login Attempt Detected')
                # Log failed login to received.log
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    log_entry = f"{ts},('{ROUTER_IP}',{dport}),[LOGIN] failed\n"
                    f.write(log_entry)
                    print(f"[LOGGED] {log_entry.strip()}")



sniff(prn=packet_handler, store=False)