"""
Usage:  
python3 bsmsender.py 
python3 bsmsender.py once
"""
import socket, json, time, os, platform, sys
from itertools import cycle

def main(loop=True):
    # FILENAMES = ["bsm.json", "bsm1.json"]
    FILENAMES = ["bsm.json"]

    # config (kept as-is)
    current_os = platform.system()
    if current_os == "Linux":
        config_file_path = os.path.join(os.path.expanduser("~"), "Desktop", "debashis-workspace", "config", "anl-master-config.json")
    elif current_os == "Windows":
        config_file_path = os.path.join("C:\\", "Users", "ddas", "debashis-workspace", "config", "anl-master-config.json")
    else:
        raise OSError(f"Unsupported operating system: {current_os}")

    with open(config_file_path, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)

    hostIp = config["IPAddress"]["HostIp"]
    port = config["PortNumber"]["BsmSender"]
    bsm_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bsm_sender_socket.bind((hostIp, port))  # left as-is per your format

    vehicleServerPort = config["PortNumber"]["VehicleServer"]
    client_info = (hostIp, vehicleServerPort)

    # (kept) load once, not used later but leaving your lines intact
    fileName = "bsm.json"
    with open(fileName, "r", encoding="utf-8") as f:
        obj = json.load(f)
    encoded_data = json.dumps(obj).encode("utf-8")

    send_period = 0.1  # 10 Hz
    next_time = time.perf_counter()

    try:
        # choose iterator: infinite cycle if loop=True, single pass if loop=False
        file_iter = cycle(FILENAMES) if loop else iter(FILENAMES)

        for fname in file_iter:
            now = time.perf_counter()
            sleep_s = next_time - now
            if sleep_s > 0:
                time.sleep(sleep_s)
            next_time += send_period

            try:
                with open(fname, "r", encoding="utf-8") as f:
                    data = f.read()
                bsm_sender_socket.sendto(data.encode("utf-8"), client_info)
                print(f"Sent {fname} at {time.time():.3f}")
            except FileNotFoundError:
                print(f"[WARN] {fname} not found; skipping.")

    except KeyboardInterrupt:
        print("Stopping…")
    finally:
        bsm_sender_socket.close()

if __name__ == "__main__":
    # one optional arg: 'once' → loop=False; anything else (or nothing) → loop=True
    loop_flag = True
    if len(sys.argv) > 1 and sys.argv[1].lower() == "once":
        loop_flag = False
    main(loop=loop_flag)
