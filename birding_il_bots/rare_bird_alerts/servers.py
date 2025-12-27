class ServerConfig:
    alerts_channel: str
    region: str
    server_id: int

    def __init__(self, server_id: int, alerts_channel: str, region: str):
        self.alerts_channel = alerts_channel
        self.server_id = server_id
        self.region = region

server_configs: list[ServerConfig] = [
    ServerConfig(1219333971851346030, "ebird-alerts", "US-IL"), # test server
    ServerConfig(1100492398129328232, "ebird-alerts", "US-IL"), # Birding Illinois
    ServerConfig(1244461044819038278, "ebird-alerts", "US-IL") # FBCC
]

filtered_species_filenames: dict[str, str] = {
    "US-IL": "rare-bird-excludes.txt"
}
