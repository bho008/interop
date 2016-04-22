from __future__ import print_function
from interop import AsyncClient
from interop import Telemetry
from interop import StationaryObstacle
from interop import Client
from time import time
import argparse

try:
    # Python 3
    from xmlrpc.server import SimpleXMLRPCServer
except ImportError:
    # Python 2
    from SimpleXMLRPCServer import SimpleXMLRPCServer

__author__ = 'Joseph Moster'

class RelayService:
    def __init__(self, url, username, password):
        self.client = AsyncClient(url=url,
                                  username=username,
                                  password=password)
        self.last_telemetry = time()

    def telemetry(self, lat, lon, alt, heading):
        t = Telemetry(latitude=lat,
                      longitude=lon,
                      altitude_msl=alt,
                      uas_heading=heading)
        self.client.post_telemetry(t)

        new_time = time()
        print(1 / (new_time - self.last_telemetry))
        self.last_telemetry = new_time

        return True

    def get_obstacles(self):
        async_future = self.client.get_obstacles()
        async_stationary, async_moving = async_future.result()
        #print("here")
        # stat_ob, moving_ob = self.client.get_obstacles()
        async_radii_stationary = [o.cylinder_radius for o in async_stationary]
        async_lat_stationary = [o.latitude for o in async_stationary]
        async_lng_stationary = [o.longitude for o in async_stationary]
        async_radii_moving = [o.sphere_radius for o in async_moving]
        async_lat_moving = [o.latitude for o in async_moving]
        async_lng_moving = [o.longitude for o in async_moving]
        
        
        return async_radii_stationary, async_lat_stationary, async_lng_stationary, async_radii_moving, async_lat_moving, async_lng_moving
	
	def get_moving_obstacles(self):
	
		return True

    def server_info(self):
        info = self.client.get_server_info().result()
        return str(info.message)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AUVSI SUAS Server Interface Relay')
    parser.add_argument('--url',
        dest='url',
        help='Interoperability Server URL, example: http://10.10.130.10:80',
        required=True)
    parser.add_argument('--username',
        dest='username',
        help='Interoperability Username, example: calpoly-broncos',
        required=True)
    parser.add_argument('--password',
                        dest='password',
                        help='Interoperability Password, example: 4597630144',
                        required=True)

    cmd_args = parser.parse_args()
    relay = RelayService(url=cmd_args.url,
                         username=cmd_args.username,
                         password=cmd_args.password)

    server = SimpleXMLRPCServer(('127.0.0.1', 9000),
        logRequests=True,
        allow_none=True)
    server.register_instance(relay)

    try:
        print('Use Control-C to exit')
        server.serve_forever()
    except KeyboardInterrupt:
        print('Exiting')
