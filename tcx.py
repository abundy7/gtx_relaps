import sys
from datetime import datetime
import xml.etree.ElementTree as ET


class Lap:
    def __init__(self, start_time, end_time, distance, max_speed, heartrates, trackpoints):
        self.lap_StartTime = datetime.isoformat(start_time).replace('+00:00', 'Z')
        self.lap_TotalTimeSeconds = str((end_time - start_time).seconds)
        self.lap_DistanceMeters = str(distance)
        self.lap_MaximumSpeed = str(max_speed)
        # self.lap_Calories = 0
        self.lap_AverageHeartRateBpm_Value = str(sum(heartrates) / len(heartrates))
        self.lap_MaximumHeartRateBpm_Value = str(max(heartrates))
        self.lap_Intensity = 'Active'
        self.lap_TriggerMethod = 'Manual'
        self.trackpoints = trackpoints


class Tcx:
    def __init__(self, xml_file_name):
        self.ns = {
            'tcd': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2',
            'ns3': 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'
        }
        self.tree = ET.parse(xml_file_name)
        self.root = self.tree.getroot()
        self.laps:list[Lap] = []

    def create_new_laps(self, lap_split:float):
        lap_MaximumSpeed = 0.0
        # lap_Calories = 0
        lap_heartrate_list = []
        lap_start = None
        lap_end = None
        lap_trackpoints = []
        all_trackpoints = self.root.findall('.//tcd:Trackpoint', self.ns)
        previous_lap_distance = 0.0
        for idx, trackpoint in enumerate(all_trackpoints):
            if not lap_start:
                # 2021-10-13T10:19:18.000Z
                lap_start = datetime.fromisoformat(trackpoint.find('tcd:Time', self.ns).text.replace('Z', '+00:00'))
            lap_distance = float(trackpoint.find('tcd:DistanceMeters', self.ns).text)
            trackpoint_speed = float(trackpoint.findall('.//ns3:Speed', self.ns)[0].text)
            lap_MaximumSpeed = max(trackpoint_speed, lap_MaximumSpeed)
            lap_heartrate_list.append(
                int(
                    trackpoint.find('tcd:HeartRateBpm', self.ns).find('tcd:Value', self.ns).text
                )
            )
            lap_trackpoints.append(trackpoint)
            tpl = len(all_trackpoints) - 1
            net_lap_distance = lap_distance - previous_lap_distance
            if net_lap_distance >= lap_split or idx == len(all_trackpoints) - 1:
                lap_end = datetime.fromisoformat(trackpoint.find('tcd:Time', self.ns).text.replace('Z', '+00:00'))
                self.laps.append(Lap(lap_start, lap_end, net_lap_distance, lap_MaximumSpeed, lap_heartrate_list, lap_trackpoints))
                # reset
                lap_trackpoints = []
                lap_start = None
                lap_end = None
                lap_heartrate_list = []
                lap_MaximumSpeed = 0.0
                previous_lap_distance = lap_distance

    def delete_old_laps(self):
        activities = self.root.find('tcd:Activities', self.ns)
        activity = activities.find('tcd:Activity', self.ns)
        for lap in activity.findall('tcd:Lap', self.ns):
            activity.remove(lap)

    def build_new_xml(self):
        activities = self.root.find('tcd:Activities', self.ns)
        activity = activities.find('tcd:Activity', self.ns)
        for lap in self.laps:
            lap_element = ET.SubElement(activity, 'Lap')
            lap_element.set('StartTime', lap.lap_StartTime)
            TotalTimeSeconds_element = ET.SubElement(lap_element, 'TotalTimeSeconds')
            TotalTimeSeconds_element.text = lap.lap_TotalTimeSeconds
            DistanceMeters_element = ET.SubElement(lap_element, 'DistanceMeters')
            DistanceMeters_element.text = lap.lap_DistanceMeters
            MaximumSpeed_element = ET.SubElement(lap_element, 'MaximumSpeed')
            MaximumSpeed_element.text = lap.lap_MaximumSpeed
            AverageHeartRateBpm_element = ET.SubElement(lap_element, 'AverageHeartRateBpm')
            AverageHeartRateBpmValue_element = ET.SubElement(AverageHeartRateBpm_element, 'Value')
            AverageHeartRateBpmValue_element.text = lap.lap_AverageHeartRateBpm_Value
            MaximumHeartRateBpm_element = ET.SubElement(lap_element, 'MaximumHeartRateBpm')
            MaximumHeartRateBpmValue_element = ET.SubElement(MaximumHeartRateBpm_element, 'Value')
            MaximumHeartRateBpmValue_element.text = lap.lap_MaximumHeartRateBpm_Value
            Intensity_element = ET.SubElement(lap_element, 'Intensity')
            Intensity_element.text = lap.lap_Intensity
            TriggerMethod_element = ET.SubElement(lap_element, 'TriggerMethod')
            TriggerMethod_element.text = lap.lap_TriggerMethod
            Track_element = ET.SubElement(lap_element, 'Track')
            for trackpoint in lap.trackpoints:
                Track_element.append(trackpoint)

tcx = Tcx(sys.argv[1])
tcx.create_new_laps(400)
tcx.delete_old_laps()
tcx.build_new_xml()
xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n'
xml_main = ET.tostring(tcx.root).decode('utf-8').replace('ns0:', '').replace(':ns0', '')
print(f'{xml_header}{xml_main}')
# for lap in tcx.laps:
#     mile_meters = 1609.34
#     multiplier = mile_meters / lap.lap_DistanceMeters
#     mile_pace = lap.lap_TotalTimeSeconds * multiplier
#     print(f'{lap.lap_DistanceMeters}m @ {mile_pace}')

