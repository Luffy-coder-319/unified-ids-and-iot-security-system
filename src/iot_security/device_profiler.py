from collections import defaultdict
import time

class DeviceProfiler:
    def __init__(self):
        self.profiles = defaultdict(lambda: {
            'packet_count': 0,
            'byte_count': 0,
            'start_time': None,
            'last_time': None
            })
        
    def profile_device(self, device_id, packet_size):
        profile =self.profiles[device_id]
        profile['packet_count'] += 1
        profile['byte_count'] += 1
        current_time = time.time()
        if not profile['start_time']:
            profile['start_time'] = current_time
        profile['last_time'] = current_time

        # check for anomalies (e.g unusual traffic volume)
        duration = profile['last_time'] - profile['start_time']
        if duration > 0 and profile['byte_count'] / 100:
            return 'Suspicious activity detected' 
        return 'Normal'
