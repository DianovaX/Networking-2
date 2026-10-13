# Network Latency Scanner

Pings google.com 5 times with Python + Scapy and shows the average latency in the browser. Networking 2, Module 13.

## What to download

1. **Python 3**: https://www.python.org/downloads/
2. **Flask and Scapy**:
   ```
   pip install flask scapy
   ```
3. **Npcap** (Windows only): https://npcap.com
   Check "Install Npcap in WinPcap API-compatible Mode" during setup, then reopen your terminal.

## Run

Run as administrator (Windows) or root (Mac/Linux). Scapy needs it to send packets.

```
python app.py
```

Mac/Linux:

```
sudo python3 app.py
```

Open http://127.0.0.1:5000 and click **Run scan**.

## Files

```
app.py
index.html
style/style.css
```
