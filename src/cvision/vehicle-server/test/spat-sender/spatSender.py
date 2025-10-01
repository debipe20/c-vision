"""
Usage:  
python3 spatsender.py 
python3 spatsender.py once
"""
import socket, json, time, os, platform, sys
from itertools import cycle

def main(loop=True):
    # FILENAMES = ["spat.json", "spat1.json"]
    FILENAMES = ["spat.json"]

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
    port = config["PortNumber"]["SpatSender"]
    spat_sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    spat_sender_socket.bind((hostIp, port))  # left as-is per your format

    vehicleServerPort = config["PortNumber"]["VehicleServer"]
    client_info = (hostIp, vehicleServerPort)

    send_period = 0.1  # 10 Hz
    next_time = time.perf_counter()

    try:
        # choose iterator: infinite cycle if loop=True, single pass if loop=False
        file_iter = cycle(FILENAMES) if loop else iter(FILENAMES)

        for fname in file_iter:
            # pacing with catch-up to avoid drift
            now = time.perf_counter()
            while next_time <= now:
                next_time += send_period
            sleep_s = next_time - now
            if sleep_s > 0:
                time.sleep(sleep_s)

            try:
                # validate JSON and re-serialize (ensures well-formed payload)
                with open(fname, "r", encoding="utf-8") as f:
                    obj = json.load(f)
                data = json.dumps(obj, separators=(",", ":"), ensure_ascii=False)

                spat_sender_socket.sendto(data.encode("utf-8"), client_info)
                print(f"Sent {fname} to {client_info[0]}:{client_info[1]} at {time.time():.3f}")
            except FileNotFoundError:
                print(f"[WARN] {fname} not found; skipping.")
            except json.JSONDecodeError as e:
                print(f"[WARN] {fname} invalid JSON ({e}); skipping.")

    except KeyboardInterrupt:
        print("Stopping…")
    finally:
        spat_sender_socket.close()

if __name__ == "__main__":
    # one optional arg: 'once' → loop=False; anything else (or nothing) → loop=True
    loop_flag = True
    if len(sys.argv) > 1 and sys.argv[1].lower() == "once":
        loop_flag = False
    main(loop=loop_flag)
