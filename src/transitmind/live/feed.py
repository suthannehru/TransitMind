from google.transit import gtfs_realtime_pb2
import httpx
import structlog

logger = structlog.getLogger(__name__)

def get_api_suffix(line):
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

def get_live_postitions(line):
    api_suffix = get_api_suffix(line)
    if not api_suffix:
        return None
    # Retrieve raw bytes from endpoint
    response = httpx.get(f"https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/{api_suffix}")
    # Raw data
    rawbytes = response.content

    # Mutate the feed object with the header and entity data
    feed.ParseFromString(rawbytes)

    positions = []

    for entity in feed.entity:
        if entity.HasField("vehicle"):
            vehicle = entity.vehicle
            trip = vehicle.trip
            if trip.route_id == line:
                positions.append({"trip_id": trip.trip_id, 
                                "status": gtfs_realtime_pb2.VehiclePosition.VehicleStopStatus.Name(vehicle.current_status),
                                "stop_id": vehicle.stop_id})


    return positions

def get_service_alerts(line):
    api_suffix = get_api_suffix(line)
    if not api_suffix:
        return None
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
    logger.info("get_live_postitions", params=glp_params, output=get_live_postitions(*glp_params))
    logger.info("get_service_alerts", params=gsa_params, output=get_service_alerts(*gsa_params))
