
class Datasource:
    def __init__(self, nested_data):
        self.ip = nested_data['ip']
        self.port = nested_data['port']
        self.database=nested_data['database']
        self.username=nested_data['username']
        self.password=nested_data['password']

class CameraConfig:
    def __init__(self,nested_data):
        self.pool_camera_source=nested_data['pool_camera']
        self.side_camera_source=nested_data['side_camera']
        
class Broker:
    def __init__(self, nested_data):
        self.ip = nested_data['ip']
        self.username=nested_data['username']
        self.password=nested_data['password']

class MqttTopic:
    def __init__(self, nested_data):
        self.alert = nested_data['alert']
        self.cylinder = nested_data['cylinder']
        self.ping= nested_data['ping']
        self.ultra=nested_data['ultra']
        self.stream_cam1=nested_data['stream_cam1']
        self.stream_cam2=nested_data['stream_cam2']
        self.cylinder_control=nested_data['cylinder_control']

class SystemConfiguration:
    def __init__(self, data):
        self.datasource= Datasource(data['datasource'])
        self.broker = Broker(data['broker'])
        self.topic = MqttTopic(data['mqtt_topic'])
        self.camera=CameraConfig(data['camera'])
