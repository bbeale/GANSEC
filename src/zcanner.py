from zapv2 import ZAPv2
# from src.scanner import Scanner


class Zcanner:  # (Scanner):
    def __init__(self, scan_data, api_key=None):
        # super(Zcanner, self).__init__(data=scan_data)
        self.data = scan_data
        self.zap = ZAPv2(api_key)
        self.stats = self.zap.stats
        print(".")
# <img style="height:100px; width:100px" onmouseover="javascript:alert(1)">
