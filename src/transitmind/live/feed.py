from collections import defaultdict
from google.transit import gtfs_realtime_pb2
import httpx
import structlog
from transitmind.graph.routing import G

logger = structlog.getLogger(__name__)

def get_api_suffix(line: str) -> str:
    line_api = {"/1/2/3/4/5/6/7/GS/" : "nyct%2Fgtfs",
                "/A/C/E/" : "nyct%2Fgtfs-ace",
                "/B/D/F/M/": "nyct%2Fgtfs-bdfm",
                "/G/": "nyct%2Fgtfs-g",
                "/J/Z/": "nyct%2Fgtfs-jz",
                "/N/Q/R/W/": "nyct%2Fgtfs-nqrw",
                "/L/": "nyct%2Fgtfs-l",
                "/SI/": "nyct%2Fgtfs-si",
    }

    for line_group, api_suffix in line_api.items():
        line_key = f"/{line}/"
        if line_key in line_group:
            return api_suffix

    return None

# FeedMessage protobuf message class
# Object follows the data schema
feed = gtfs_realtime_pb2.FeedMessage()

def get_live_positions(line: str) -> list[str]:
    """Given a line, returns a list of strings indicating positions."""

    api_suffix = get_api_suffix(line)
    if not api_suffix:
        return []
    # Retrieve raw bytes from endpoint
    response = httpx.get(f"https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/{api_suffix}")
    # Raw data
    rawbytes = response.content

    # Mutate the feed object with the header and entity data
    feed.ParseFromString(rawbytes)

    positions = defaultdict(lambda: defaultdict(dict))
    result = []
    total_trains = 0
    plurality = {True: {"train": "train", "is": "is"}, False: {"train": "trains", "is": "are"}}

    status_text = {"stopped_at": "stopped at", "incoming_at": "arriving at", "in_transit_to": "in transit to"}

    for entity in feed.entity:
        if entity.HasField("vehicle"):
            vehicle = entity.vehicle
            trip = vehicle.trip
            if trip.route_id == line:
                direction = vehicle.stop_id[-1]
                parent_station = vehicle.stop_id.removesuffix(direction)
                try:
                    station = G.nodes[parent_station]["name"]
                except KeyError:
                    station = parent_station
                status = (gtfs_realtime_pb2.VehiclePosition.VehicleStopStatus.Name(vehicle.current_status)).lower()
                station_dir = positions[station][direction]
                station_dir[status] = station_dir.get(status, 0) + 1
                total_trains += 1

    total_train_index = total_trains == 1
    result.append(f"There are {total_trains} {plurality[total_train_index]['train']} for line {line}.")

    for station, direction_dict in positions.items():
        for direction, status_dict in direction_dict.items():
            for status, count in status_dict.items():
                formal_direction = "northbound" if direction == "N" else "southbound"
                train_index = count == 1
                result.append(f"{count} {plurality[train_index]['train']} {plurality[train_index]['is']} {status_text[status]} {station} in the {formal_direction} direction.")

    return result

def get_service_alerts(line: str) -> list[dict]:
    """Given a line, return a list of dictionaries for every service alert on that line"""

    api_suffix = get_api_suffix(line)
    if not api_suffix:
        return []
    # Retrieve raw bytes from endpoint
    response = httpx.get(f"https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/{api_suffix}")

    # Raw data
    rawbytes = response.content

    # Mutate the feed object with the header and entity data
    feed.ParseFromString(rawbytes)

    alerts = []
    for entity in feed.entity:
        if entity.HasField("alert"):
            # English alert translation
            alert = entity.alert
            alert_msg = alert.header_text.translation[0].text
            current_alert = {"alert_text": alert_msg}
            impacted_trips = []
            for alert_entity in alert.informed_entity:
                if alert_entity.trip.route_id == line:
                    impacted_trips.append({"trip_id": alert_entity.trip.trip_id,
                                        "route_id": alert_entity.trip.route_id})

            if len(impacted_trips):
                current_alert["trips"] = list(impacted_trips)
                alerts.append(current_alert)

            
    return alerts

if __name__ == "__main__":
    glp_params = ('1',)
    gsa_params = ('F',)
    logger.info("get_live_positions", params=glp_params, output=get_live_positions(*glp_params))
    logger.info("get_service_alerts", params=gsa_params, output=get_service_alerts(*gsa_params))
