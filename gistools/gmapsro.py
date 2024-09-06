import os
import pandas
import geopandas
import zipfile
import ipywidgets as widgets

from copy import copy, deepcopy
from shapely import wkt
from cartoframes.viz import *
from proto import Message
from google.protobuf.json_format import MessageToJson
from google.maps import routeoptimization_v1

from gistools.utils    import *
from gistools.strings  import remove_character
from gistools.geometry import Point, decode_polyline, to_shapely, to_geo

FLEET_DIMENSIONS = [
	'no_stops', 
	'floor_pallets', 
	'weight', 
	'volume'
]

DEFAULT_CURRENCY = '€'

def _get_item(obj, item):
	return obj.get(item, None) if obj is not None and len(obj) > 0 else None

def _convert_datetime(t, format_string='%Y-%m-%dT%H:%M:%S', offset=0):
	delta = timestamp_utcoffset(t)+offset
	s = '+{:02d}:00'.format(abs(delta)) if delta > 0 else '-{:02d}:00'.format(abs(delta))
	return timestamp2str(t, format_string)+s

def _set_duration(obj, col_name='duration'):
	duration = 0

	if is_set(obj, col_name):
		t = {'hours': 3600, 'minutes': 60, 'seconds': 1}
		
		d = int(obj.get(col_name))
		k = t.get(obj.get('duration_unit', 'minutes'), 60)
		
		duration=d*k

	return duration

class FleetRoutingEntity(geopandas.GeoDataFrame):
	def __init__(self, data):
		if isinstance(data, geopandas.GeoDataFrame):
			super().__init__(data=data)

		else:
			_data = pandas.DataFrame(data)

			if 'geometry' in _data.columns:
				geometry=_data['geometry'].apply(wkt.loads)

			elif 'longitude' in _data.columns and 'latitude' in _data.columns:
				geometry = geopandas.GeoSeries(
					[Point(x, y) for x, y in zip(_data['longitude'], _data['latitude'])], 
					crs='EPSG:4326'
				)
			else:
				raise ValueError("Ooups! Something went wrong.")

			super().__init__(data=_data, geometry=geometry, crs='EPSG:4326')

		super().reset_index(drop=True, inplace=True)

	def set_time_window(self, columns=None, format_string='%Y-%m-%d %H:%M:%S'):
		if columns is None:
			columns = {
				'period': 'period',
				'time_window_start': 'time_window_start',
				'time_window_end': 'time_window_end',
				'start_timestamp': 'start_timestamp',
				'end_timestamp': 'end_timestamp'
			}

		def to_datetime(r):
			start_dt = r[columns['period']] + ' ' + r[columns['time_window_start']]
			end_dt   = r[columns['period']] + ' ' + r[columns['time_window_end']]
			return [start_dt, end_dt]

		time_window = self.apply(lambda x: pandas.Series(to_datetime(x), index=['start_datetime', 'end_datetime']), axis='columns')
		df = pandas.concat([self[:], time_window[:]], axis='columns')
		
		df[columns['start_timestamp']] = df['start_datetime'].apply(lambda s: str2timestamp(s, format_string=format_string))
		df[columns['end_timestamp']]   = df['end_datetime'  ].apply(lambda s: str2timestamp(s, format_string=format_string))

		self.__init__(df.drop(columns=['start_datetime', 'end_datetime']))

		return self

	def set_lunch_break_time_window(self, format_string='%Y-%m-%d %H:%M:%S'):
		return self.set_time_window(
			columns = {
				'period': 'period',
				'time_window_start': 'lunch_break_time_window_start',
				'time_window_end': 'lunch_break_time_window_end',
				'start_timestamp': 'lunch_break_start_timestamp',
				'end_timestamp': 'lunch_break_end_timestamp'
			},
			format_string=format_string
		)

	def where(self, expr):
		self.__init__(where(self, expr))

		return self

class FleetRouting(object):
	def __init__(self, data={}, expr=None, calendar=None, **kwargs):
		if isinstance(data, list):
			self._data = {
				'shipments': data[0],
				'depots'   : data[1],
				'vehicles' : data[2],
				'stores'   : data[3],
				'locations': data[4]
			}
		else:
			self._data = data

		self._calendar = calendar
		self._utc_offset = 0

		if self._data is not None and len(self._data) > 0:
			for k in self._data.keys():
				if isinstance(self._data[k], pandas.DataFrame) or isinstance(self._data[k], geopandas.GeoDataFrame):
					self._data[k] = FleetRoutingEntity(self._data[k])
				if expr is not None:
					self._data[k] = self._data[k].where(expr)

				self._data[k] = self.__set_gmapsro_index(self._data[k], col_name='gmapsro_id')

			if not isinstance(self._data['shipments'].iloc[0]['shipment_name'], str):
				self._data['shipments']['shipment_name'] = self._data['shipments']['shipment_name'].astype(str)

			if 'depots' in self._data.keys():
				self._depots_dict = {}
				for index, row in self._data['depots'].iterrows():
					self._depots_dict[row['depot_id']] = index
			if 'stores' in self._data.keys():
				self._stores_dict = {}
				for index, row in self._data['stores'].iterrows():
					self._stores_dict[row['store_id']] = index
			if 'locations' in self._data.keys():
				self._locations_dict = {}
				for index, row in self._data['locations'].iterrows():
					self._locations_dict[row['location_id']] = index
			
			self._global_start_time, self._global_end_time = self.__set_global_time_window(
				self.vehicles, self.shipments
			)
			
		self._currency = DEFAULT_CURRENCY

		self._scenario = None
		self._protobuf_response = None
		self._timeout = None
		self._response = None
		self._metrics = {}
		self._elapsed_time = 0
		self._tag_delimiter = '-'

		self._protobuf_request = routeoptimization_v1.OptimizeToursRequest()
		self._protobuf_request.populate_polylines = True
		self._protobuf_request.populate_transition_polylines = True

		self.project_id = None

		self.set_config(**kwargs)
		
		self.scenario = {
			"parent": "",
			"model": {},
			"solvingMode": 0,
			"searchMode": 1,
			"interpretInjectedSolutionsUsingLabels": False,
			"considerRoadTraffic": False,
			"populatePolylines": True,
			"populateTransitionPolylines": False,
			"allowLargeDeadlineDespiteInterruptionRisk": False,
			"useGeodesicDistances": False,
			"label": "",
			"populateTravelStepPolylines": False
		}
		
		self._solution = {}

	@staticmethod
	def __set_gmapsro_index(data, col_name):
		data = data.reset_index(drop=True)
		data[col_name] = data.index.tolist()
		data = data.set_index(col_name, drop=False)

		return FleetRoutingEntity(data)

	@staticmethod
	def __set_global_time_window(vehicles, shipments):
		global_start_time = 0
		global_end_time = 0

		if 'start_timestamp' in vehicles.columns:
			if 'start_timestamp' in shipments.columns:
				global_start_time = min(vehicles['start_timestamp'].min(), shipments['start_timestamp'].min())
			else:
				global_start_time = min(vehicles['start_timestamp'].min())

		if 'end_timestamp' in vehicles.columns: 
			if 'end_timestamp' in shipments.columns:
				global_end_time = max(vehicles['end_timestamp'].max(), shipments['end_timestamp'].max())
			else:
				global_end_time = max(vehicles['end_timestamp'].max())

		return global_start_time, global_end_time

	def set_fleet(self, depot_id, no_vehicles, available_periods=None):
		return self

	def __repr__(self) -> str:
		return '<{}>'.format(getattr(self, '__name__', self.__class__.__name__))

	def __getitem__(self, key):
		return getattr(self, key)

	def __setitem__(self, key, value):
		setattr(self, key, value)

	@property
	def data(self):
		return self._data

	@data.setter
	def data(self, v):
		self._data = v

	@property
	def depots(self):
		return _get_item(self._data, 'depots')

	@depots.setter
	def depots(self, v):
		self._data['depots'] = v

	@property
	def depots_dict(self):
		return self._depots_dict

	@property
	def vehicles(self):
		return _get_item(self._data, 'vehicles')

	@vehicles.setter
	def vehicles(self, v):
		self._data['vehicles'] = v

	@property
	def stores(self):
		return _get_item(self._data, 'stores')

	@stores.setter
	def stores(self, v):
		self._data['stores'] = v

	@property
	def stores_dict(self):
		return self._stores_dict

	@property
	def locations(self):
		return _get_item(self._data, 'locations')

	@locations.setter
	def locations(self, v):
		self._data['locations'] = v

	@property
	def locations_dict(self):
		return self._locations_dict

	@property
	def routes(self):
		return _get_item(self._data, 'routes')

	@routes.setter
	def routes(self, v):
		self._data['routes'] = v

	@property
	def shipments(self):
		return _get_item(self._data, 'shipments')

	@shipments.setter
	def shipments(self, v):
		self._data['shipments'] = v

	@property
	def skipped_visits(self):
		return _get_item(self._data, 'skipped_visits')

	@skipped_visits.setter
	def skipped_visits(self, v):
		self._data['skipped_visits'] = v

	@property
	def visits(self):
		return _get_item(self._data, 'visits')

	@visits.setter
	def visits(self, v):
		self._data['visits'] = v

	@property
	def calendar(self):
		return self._calendar

	@calendar.setter
	def calendar(self, v):
		self._calendar = v

	@property
	def scenario(self):
		return self._scenario
		
	@scenario.setter
	def scenario(self, value):
		if isinstance(value, dict):
			self._scenario = value
		elif os.path.isfile(value):
			self._scenario = read_json(value) 
		
		else:
			raise TypeError("Oops! Expected a dict or a filename but got %s" % type(value).__name__)

	@property
	def protobuf_response(self):
		return self._protobuf_response
		
	@property
	def response(self):
		return self._response
		
	@response.setter
	def response(self, value):
		if isinstance(value, dict):
			self._response = value
		elif os.path.isfile(value):
			self._response = read_json(value) 
		
		else:
			raise TypeError("Oops! Expected a dict or a filename but got %s" % type(value).__name__)

	@property
	def elapsed_time(self):
		return self._elapsed_time

	@property
	def solution(self):
		return self._solution

	@solution.setter
	def solution(self, v):
		self._solution = v

	@property
	def protobuf_request(self):
		return self._protobuf_request

	@protobuf_request.setter
	def protobuf_request(self, protobuf_request):
		self._protobuf_request = protobuf_request

	@property
	def project_id(self):
		return self._project_id

	@project_id.setter
	def project_id(self, v):
		self._project_id = v	

	@property
	def timeout(self):
		return self._timeout

	@timeout.setter
	def timeout(self, timeout):
		if timeout is None:
			self._timeout = 0
		else:
			self._timeout = timeout
			
	@property
	def currency(self):
		return self._currency

	@currency.setter
	def currency(self, currency):
		self._currency = currency

	@property
	def label(self):
		return self._protobuf_request.label

	@label.setter
	def label(self, label):
		self._protobuf_request.label = label

	@property
	def populate_polylines(self):
		return self._protobuf_request.populate_polylines

	@populate_polylines.setter
	def populate_polylines(self, populate_polylines):
		self._protobuf_request.populate_polylines = populate_polylines

	@property
	def populate_transition_polylines(self):
		return self._protobuf_request.populate_transition_polylines
	
	@populate_transition_polylines.setter
	def populate_transition_polylines(self, populate_transition_polylines):
		self._protobuf_request.populate_transition_polylines = populate_transition_polylines
	
	@property
	def populate_travel_step_polylines(self):
		return self._protobuf_request.populate_travel_step_polylines
	
	@populate_travel_step_polylines.setter
	def populate_travel_step_polylines(self, populate_travel_step_polylines):
		self._protobuf_request.populate_travel_step_polylines = populate_travel_step_polylines
	
	@property
	def consider_road_traffic(self):
		return self._protobuf_request.consider_road_traffic

	@consider_road_traffic.setter
	def consider_road_traffic(self, consider_road_traffic):
		self._protobuf_request.consider_road_traffic = consider_road_traffic
	
	@property
	def search_mode(self):
		return self._protobuf_request.search_mode

	@search_mode.setter
	def search_mode(self, search_mode):
		self._protobuf_request.search_mode = search_mode
	
	@property
	def solving_mode(self):
		return self._protobuf_request.solving_mode

	@solving_mode.setter
	def solving_mode(self, solving_mode):
		self._protobuf_request.solving_mode = solving_mode
	
	@property
	def use_geodesic_distances(self):
		return self._protobuf_request.use_geodesic_distances

	@use_geodesic_distances.setter
	def use_geodesic_distances(self, use_geodesic_distances):
		self._protobuf_request.use_geodesic_distances = use_geodesic_distances
	
	@property
	def max_active_vehicles(self):
		return self._protobuf_request.model.max_active_vehicles

	@max_active_vehicles.setter
	def max_active_vehicles(self, max_active_vehicles):
		self._protobuf_request.model.max_active_vehicles = max_active_vehicles
	
	@property
	def allow_large_deadline_despite_interruption_risk(self):
		return self._protobuf_request.model.max_active_vehicles

	@allow_large_deadline_despite_interruption_risk.setter
	def allow_large_deadline_despite_interruption_risk(self, allow_large_deadline_despite_interruption_risk):
		self._protobuf_request.model.allow_large_deadline_despite_interruption_risk = allow_large_deadline_despite_interruption_risk
	
	@property
	def utc_offset(self):
		return self._utc_offset

	@utc_offset.setter
	def utc_offset(self, offset):
		self._utc_offset = offset
	
	@property
	def tag_delimiter(self):
		return self._tag_delimiter

	@tag_delimiter.setter
	def tag_delimiter(self, tag_delimiter):
		self._tag_delimiter = tag_delimiter
	
	def set_config(self, **kwargs):
		for k, v in kwargs.items():
			if k == 'project_id':
				self.project_id = v
			elif k == 'timeout':
				self.timeout = v
			elif k == 'currency':
				self.currency = v 
			elif k == 'label':
				self.label = v 
			elif k == 'populate_polylines':
				self.populate_polylines = v 
			elif k == 'populate_transition_polylines':
				self.populate_transition_polylines = v
			elif k == 'populate_travel_step_polylines':
				self.populate_travel_step_polylines = v
			elif k == 'consider_road_traffic':
				self.consider_road_traffic = v
			elif k == 'search_mode':
				self.search_mode  = v
			elif k == 'solving_mode':
				self.solving_mode = v
			elif k == 'use_geodesic_distances':
				self.use_geodesic_distances = v
			elif k == 'max_active_vehicles':
				self.max_active_vehicles = v
			elif k == 'allow_large_deadline_despite_interruption_risk':
				self.allow_large_deadline_despite_interruption_risk = v
			elif k == 'utc_offset':
				self.utc_offset = v
			elif k == 'tag_delimiter':
				self.tag_delimiter = v

			else:
				raise ValueError("Oops! Unknown parameter <{}>".format(k))
					
		return None

	@property
	def global_start_time(self):
		return _convert_datetime(self._global_start_time, offset=self.utc_offset)

	@property
	def global_end_time(self):
		return _convert_datetime(self._global_end_time, offset=self.utc_offset)

	@property
	def global_time_window(self):
		return (self.global_start_time, self.global_end_time)

	def save_scenario(self, pathname='.', filename='scenario.json'):
		to_json(self.scenario, filename=filename, pathname=pathname)
		return self

	def load_scenario(self, pathname='.', filename='scenario.json'):
		return self

	def build_scenario(self):
		self.scenario = {
			"model": {
				"shipments": [],
				"vehicles" : [],
				"globalStartTime": self.global_start_time,
				"globalEndTime": self.global_end_time,
				"globalDurationCostPerHour": 0
			},
			"solvingMode": self.solving_mode,
			"searchMode": self.search_mode,
			"interpretInjectedSolutionsUsingLabels": False,
			"considerRoadTraffic": self.consider_road_traffic,
			"populatePolylines": self.populate_polylines,
			"populateTransitionPolylines": self.populate_transition_polylines,
			"allowLargeDeadlineDespiteInterruptionRisk": False,
			"useGeodesicDistances": self.use_geodesic_distances,
			"label": self.label
		}

		if self._timeout is not None:
			self.scenario['timeout'] = '{:d}s'.format(self.timeout)

		self.__set_shipments()
		self.__set_vehicles ()

		return self

	@staticmethod
	def __set_required_vehicles(visit, vehicles):
		allowed_vehicles = []

		print('ok')

		df = vehicles.where('required_vehicle_name', '==', required_vehicle)
		allowed_vehicles = df['gmapsro_id'].tolist()

		return allowed_vehicles

	@staticmethod
	def __set_allowed_vehicles(visit, vehicles, tag_delimiter):
		allowed_vehicles = []

		tags = None
		if 'tags' in visit.keys():
			tokens = visit['tags'].split(tag_delimiter)
			if len(tokens) and len(tokens[0]):
				tags = tokens

		forbidden_tags = None
		if 'forbidden_tags' in visit.keys():
			tokens = visit['forbidden_tags'].split(tag_delimiter)
			if len(tokens) and len(tokens[0]):
				forbidden_tags = tokens

		if tags is not None or forbidden_tags is not None:
			allowed_vehicles = []
			forbidd_vehicles = []

			if tags is not None:
				df = vehicles

				for tag_ in tags:
					df = df[df[tag_] == tag_] 
				allowed_vehicles = df['gmapsro_id'].tolist()
				
			if forbidden_tags is not None:
				df = vehicles

				if tags is None:
					allowed_vehicles = df['gmapsro_id'].tolist()

				for tag_ in forbidden_tags:
					df = df[df[tag_] == tag_]

				forbidd_vehicles = df['gmapsro_id'].tolist()
				allowed_vehicles = [item for item in allowed_vehicles if item not in forbidd_vehicles]

		return allowed_vehicles

	def __set_location(self, entity, label=None):
		location_id = None

		if label is not None:
			location_id = entity.get(label, None)

		if location_id is not None:
			l = self.locations.loc[self.locations_dict[location_id]]

			lat = l['latitude' ]
			lng = l['longitude']

		else:
			lat = entity['latitude' ]
			lng = entity['longitude']

		return self.__set_waypoint(lat, lng)

	@staticmethod
	def __set_waypoint(lat, lng):
		waypoint = {}

		waypoint['location'] = {}
		waypoint['location']['latLng'] = {}
		waypoint['location']['latLng']['latitude' ] = lat
		waypoint['location']['latLng']['longitude'] = lng

		return waypoint

	@staticmethod
	def __set_time_window(visit, utc_offset):
		time_window = []

		if is_set(visit, 'start_timestamp') and is_set(visit, 'end_timestamp'):

			tw = {}
			tw['startTime'] = _convert_datetime(visit['start_timestamp'], offset=utc_offset)
			tw['endTime']   = _convert_datetime(visit['end_timestamp'], offset=utc_offset)

			if is_set(visit, 'soft_start_timestamp') and is_set(visit, 'soft_end_timestamp'):
				if visit['soft_start_timestamp'] > 0 and visit['soft_end_timestamp'] > 0:
					tw['softStartTime'] = _convert_datetime(visit['soft_start_timestamp'], offset=utc_offset)
					tw['softEndTime'] = _convert_datetime(visit['soft_end_timestamp'], offset=utc_offset)
					tw['costPerHourBeforeSoftStartTime'] = visit.get('cost_per_hour_before_soft_start_time', 0)
					tw['costPerHourAfterSoftEndTime'] = visit.get('cost_per_hour_after_soft_end_time', 0)
			
			time_window.append(tw)

		return time_window

	@staticmethod
	def __set_time_window_from_calendar(visit, calendar, utc_offset):
		time_window = []

		day_no = v['weekday']

		if is_integer(day_no):
			periods = [day_no]
		else:
			if '-' in day_no:
				start, end = map(int, day_no.split('-'))
				periods = list(range(start, end + 1))
			elif ',' in day_no:
				periods = [int(x) for x in day_no.split(',')]

		for p in periods:
			tw = {}

			t1 = str2timestamp('{} {}'.format(self.calendar[p], v['time_window_start']), format_string='%Y-%m-%d %H:%M:%S')
			tw['startTime'] = _convert_datetime(t1, offset=utc_offset)
			t2 = str2timestamp('{} {}'.format(self.calendar[p], v['time_window_end']),   format_string='%Y-%m-%d %H:%M:%S')
			tw['endTime']   = _convert_datetime(t2, offset=utc_offset)

			time_windows.append(tw)

		return time_window

	@staticmethod
	def __set_opening_hours(visit, location):
		time_windows = []
		day = weekday_name(visit['period']).lower()

		if day in location:
			opening_hours = location[day]

			tw1, tw2 = None, None

			if '|' in opening_hours:
				tw  = opening_hours.split('|')
				tw1 = tw[0].split('-')
				tw2 = tw[1].split('-')
			else:
				tw1 = opening_hours.split('-')

			if tw1 is not None:
				tw = {}
				tw['startTime'] = '{}T{}:00'.format(visit['period'], tw1[0])
				tw['endTime']   = '{}T{}:00'.format(visit['period'], tw1[1])
				time_windows.append(tw)

			if tw2 is not None:
				tw = {}
				tw['startTime'] = '{}T{}:00'.format(visit['period'], tw2[0])
				tw['endTime']   = '{}T{}:00'.format(visit['period'], tw2[1])
				time_windows.append(tw)

		return time_windows

	def __set_pickup_at_depot_location(self, visit):
		task = {}

		if is_set(visit, 'pickup_location_id'):
			pickup_location_id = self.depots.loc[
				self.depots_dict[visit['pickup_location_id']]
			]

			way_point = {}
			way_point['location'] = {}
			way_point['location']['latLng'] = {}
			way_point['location']['latLng']['latitude']  = pickup_location_id['latitude']
			way_point['location']['latLng']['longitude'] = pickup_location_id['longitude']

			task = {
				"arrivalWaypoint": way_point,
				"duration" : '{:d}s'.format(_set_duration(visit, col_name='pickup_duration')),
				"cost": visit.get('pickup_cost', 0),
				"label": pickup_location_id['depot_name']
			}

			time_windows = self.__set_opening_hours(visit, pickup_location_id)
			if len(time_windows):
				task['timeWindows'] = task_windows

		return task

	def __set_pickup_at_store_location(self, visit):
		task = {}

		if is_set(visit, 'pickup_location_id'):
			pickup_location_id = self.stores.loc[
				self.stores_dict[visit['pickup_location_id']]
			]

			way_point = {}
			way_point['location'] = {}
			way_point['location']['latLng'] = {}
			way_point['location']['latLng']['latitude']  = pickup_location_id['latitude']
			way_point['location']['latLng']['longitude'] = pickup_location_id['longitude']

			task = {
				"arrivalWaypoint": way_point,
				"duration" : '{:d}s'.format(_set_duration(visit, col_name='pickup_duration')),
				"cost": visit.get('pickup_cost', 0),
				"label": pickup_location_id['store_name']
			}

			time_windows = self.__set_opening_hours(visit, pickup_location_id)
			if len(time_windows):
				task['timeWindows'] = time_windows

		return task

	def __set_pickup(self, visit):
		if self.calendar is not None:
			time_window = self.__set_time_window_from_calendar(visit, self.calendar, self.utc_offset)
		else:
			time_window = self.__set_time_window(visit, self.utc_offset)

		task = {
			"arrivalWaypoint": self.__set_location(visit),
			"duration" : '{:d}s'.format(_set_duration(visit, col_name='pickup_duration')),
			"cost": visit.get('pickup_cost', 0),
			"label": remove_character(visit['formatted_address'], ','),
			"timeWindows": time_window
		}

		return task

	def __set_delivery(self, visit):
		if self.calendar is not None:
			time_window = self.__set_time_window_from_calendar(visit, self.calendar, self.utc_offset)
		else:
			time_window = self.__set_time_window(visit, self.utc_offset)

		task = {
			"arrivalWaypoint": self.__set_location(visit),
			"duration" : '{:d}s'.format(_set_duration(visit)),
			"cost": visit.get('delivery_cost', 0),
			"label": remove_character(visit['formatted_address'], ','),
			"timeWindows": time_window
		}

		return task

	def __set_drop_off_at_depot_location(self, visit):
		task = {}

		if is_set(visit, 'drop_off_location_id'):
			drop_off_location_id = self.depots.loc[
				self.depots_dict[visit['drop_off_location_id']]
			]

			way_point = {}
			way_point['location'] = {}
			way_point['location']['latLng'] = {}
			way_point['location']['latLng']['latitude']  = drop_off_location_id['latitude']
			way_point['location']['latLng']['longitude'] = drop_off_location_id['longitude']

			task = {
				"arrivalWaypoint": way_point,
				"duration" : '{:d}s'.format(_set_duration(visit)),
				"cost": visit.get('delivery_cost', 0),
				"label": drop_off_location_id['depot_name']
			}

			time_windows = self.__set_opening_hours(visit, drop_off_location_id)
			if len(time_windows):
				task['timeWindows'] = task_windows

		return task

	def __set_shipments(self):
		for v in self.shipments.to_dict(orient='records'):
			shipment = {
				"label": '{}'.format(v['shipment_name']),
				"shipmentType": v.get('visit_type') if is_set(v, 'visit_type') else v.get('shipment_type'),
				"loadDemands": {}
			}

			if 'required_vehicle_name' in v.keys():
				shipment['allowedVehicleIndices'] = self.__set_required_vehicles(v, self.vehicles)
			else:				
				if 'tags' in v.keys() or 'forbidden_tags' in v.keys():
					shipment['allowedVehicleIndices'] = self.__set_allowed_vehicles(
						v, self.vehicles, self.tag_delimiter
					)

			for dimension in FLEET_DIMENSIONS:
				if dimension in v.keys():
					demand = {}
					demand['amount'] = str(v[dimension])
					shipment['loadDemands'][dimension] = demand

			match v.get('shipment_type'):
				case 'store_pickup_and_delivery':
					shipment['pickups'] = [self.__set_pickup_at_store_location(v)]
					shipment['deliveries'] = [self.__set_delivery(v)]

				case 'depot_pickup_and_delivery':
					shipment['pickups'] = [self.__set_pickup_at_depot_location(v)]
					shipment['deliveries'] = [self.__set_delivery(v)]

				case 'pickup_and_depot_drop_off':
					shipment['pickups'] = [self.__set_pickup(v)]
					shipment['deliveries'] = [self.__set_drop_off_at_depot_location(v)]

				case 'delivery':
					shipment['deliveries'] = [self.__set_delivery(v)]
				case 'pickup':
					shipment['pickups'] = [self.__set_pickup(v)]

				case _:
					raise ValueError("Oops! Something went wrong.")

			self.scenario['model']['shipments'].append(shipment)

		return self

	@staticmethod
	def __set_vehicle_working_hours(vehicle, utc_offset):
		tw_start, tw_end = [], []

		if is_set(vehicle, 'start_timestamp'):
			tw = {}
			tw['startTime'] = _convert_datetime(vehicle['start_timestamp'], offset=utc_offset)
			tw_start.append(tw)
			
		if is_set(vehicle, 'end_timestamp'):
			tw = {}
			tw['endTime'] = _convert_datetime(vehicle['end_timestamp'], offset=utc_offset)
			tw_end.append(tw)

		return tw_start, tw_end

	def __set_vehicles(self):
		for v in self.vehicles.to_dict(orient='records'):
			vehicle = {
				"label": v['vehicle_name'],
				"travelMode": 1,
				"unloadingPolicy": 0,
				"costPerHour": v.get('cost_per_hour', 0),
				"costPerTraveledHour": v.get('cost_per_traveled_hour', 0),
				"costPerKilometer": v.get('cost_per_kilometer', 0),
				"fixedCost": v.get('fixed_cost', 0),
				"usedIfRouteIsEmpty": False,
				"loadLimits": {}
			}

			for dimension in FLEET_DIMENSIONS:
				if dimension in v.keys():
					demand = {}

					demand['maxLoad'] = str(v[dimension])
					if is_set(v, '{}_soft_max'.format(dimension)):
						demand['softMaxLoad'] = str(v.get('{}_soft_max'.format(dimension)))
						demand['costPerUnitAboveSoftMax'] = v.get('{}_cost_per_unit_above_soft_max'.format(dimension))

					vehicle['loadLimits'][dimension] = demand

			if not v.get('start_at_first_location', False):
				vehicle['startWaypoint'] = self.__set_location(v, label='start_location_id')
			
			if not v.get('end_at_last_location', False):
				vehicle['endWaypoint'] = self.__set_location(v, label='end_location_id')

			for dimension in ['route_duration', 'route_distance']:
				if v.get('{}_limit'.format(dimension), 0) > 0:
					vehicle['routeDurationLimit'] = {
						'maxDuration': '{:d}s'.format(v['{}_limit'.format(dimension)]*60)
					}
					if is_set(v, '{}_limit_soft_max'.format(dimension)):
						soft_limit = int(v['{}_limit_soft_max'.format(dimension)])

						if (soft_limit) > 0:
							vehicle['routeDurationLimit']['softMaxDuration'] = '{:d}s'.format(soft_limit*60)
							vehicle['routeDurationLimit']['costPerHourAfterSoftMax'] = v.get(
								'{}_limit_cost_per_hour_after_soft_max'.format(dimension), 0
							)

			tw_start, tw_end = self.__set_vehicle_working_hours(v, self.utc_offset)

			if len(tw_start):
				vehicle['startTimeWindows'] = tw_start
			if len(tw_end):
				vehicle['endTimeWindows'] = tw_end

			if v.get('lunch_break'):
				if is_set(v, 'lunch_break_start_timestamp') and is_set(v, 'lunch_break_end_timestamp'):
					vehicle['breakRule'] = {}
					vehicle['breakRule']['breakRequests'] = []

					break_request = {}
					break_request['earliestStartTime'] = _convert_datetime(v['lunch_break_start_timestamp'], offset=self.utc_offset)
					break_request['latestStartTime']   = _convert_datetime(v['lunch_break_end_timestamp'], offset=self.utc_offset)

					duration = v['lunch_break_duration']*60
					break_request['minDuration'] = '{:d}s'.format(duration)

					vehicle['breakRule']['breakRequests'].append(break_request)

			self.scenario['model']['vehicles'].append(vehicle)

		return self

	def solve(self, request_file_name=None, **kwargs):
		fleet_routing_client = routeoptimization_v1.RouteOptimizationClient()
		self.set_config(**kwargs)

		if request_file_name is not None:
			with open(request_file_name) as f:
				self._protobuf_request: Message = routeoptimization_v1.OptimizeToursRequest.from_json(f.read())
		
		else:
			self._protobuf_request: Message = routeoptimization_v1.OptimizeToursRequest.from_json(
				json.dumps(self._scenario, indent = 4)
			)
		self._protobuf_request.parent = 'projects/{}'.format(self.project_id)

		if self._timeout is not None:
			self._search_mode = 2
			self._protobuf_request.search_mode = self._search_mode
		
		t0 = time.time()

		self._protobuf_response = fleet_routing_client.optimize_tours(self._protobuf_request, timeout=self.timeout)
		self.response = json.loads(MessageToJson(self.protobuf_response._pb))

		self._elapsed_time = time.time() - t0
		
		return self.parse_response()

	def save_solution(self, pathname='.', filename='solution.json'):
		json_dict = json.loads(MessageToJson(self.protobuf_response._pb))

		with open(ospathjoin(pathname, filename), "w") as f:
			json.dump(json_dict, f, indent=4)		
		return self

	def to_zip(self, pathname='.', filename='problem.zip'):
		if not filename.lower().endswith('.zip'):
			raise ValueError("Oups! Something went wrong.")

		else:
			self.save_scenario(filename='scenario.json')
			self.save_solution(filename='solution.json')

			with zipfile.ZipFile(ospathjoin(pathname, filename), 'w') as f:
				f.write('scenario.json')
				f.write('solution.json')

			os.remove('scenario.json')
			os.remove('solution.json')

		return self

	def __parse_visits(self):
		columns = [
			'shipmentIndex', 
			'shipmentLabel', 
			'isPickup', 
			'vehicleIndex', 
			'vehicleLabel', 
			'startTime', 
			'visitLabel',
			'assigned_route_order_id'
		]

		visits = []

		for index, r in enumerate(self.response['routes']):
			if 'visits' in r:
				df = pandas.DataFrame(r['visits'])
				df = df.reset_index(drop=True)

				df['vehicleIndex'] = r['vehicleIndex']
				df['vehicleLabel'] = r['vehicleLabel']

				df['assigned_route_order_id'] = add_to(df.index.tolist(), value=1)

				visits.append(
					df.reindex(columns=columns)
				)

		visits = pandas.concat(visits)

		visits['assigned_date'] = visits['startTime'].apply(lambda s: s.split('T')[0][:10]) 
		visits['assigned_time'] = visits['startTime'].apply(lambda s: s.split('T')[1][:8])

		visits = visits.rename(columns={
			'shipmentIndex': 'gmapsro_id',
			'shipmentLabel': 'shipment_name',
			'visitLabel'   : 'visit_name',
			'isPickup'     : 'is_pickup',
			'vehicleIndex' : 'vehicle_id',
			'vehicleLabel' : 'vehicle_name',
			'startTime'    : 'assigned_datetime',
			'orderId'      : 'assigned_route_order_id'
		})

		if self.shipments is not None:
			visits = pandas.merge(
				left=visits, 
				right=self.shipments.reset_index(drop=True), 
				left_on='gmapsro_id', 
				right_on='gmapsro_id', 
				how='inner'
			).sort_values(
				by='gmapsro_id', 
				ascending=True
			)

			visits = FleetRoutingEntity(to_geo(visits, from_='geometry'))

			if self.shipments is not None:
				if 'shipment_name' in self.shipments:
					visits = visits.drop(columns=['shipment_name_y']).rename(columns={'shipment_name_x': 'shipment_name'})

		self._data['visits'] = visits

		return self
			
	def __parse_skipped_visits(self):
		self._data['skipped_visits'] = pandas.DataFrame()

		#TO DO

		return self

	def __parse_routes(self):
		columns = {
			'vehicleIndex'          : 'vehicle_id', 
			'vehicleLabel'          : 'vehicle_name', 
			'vehicleStartTime'      : 'vehicle_start_time', 
			'vehicleEndTime'        : 'vehicle_end_time', 
			'performedShipmentCount': 'number_of_shipments', 
			'number_of_stops'       : 'number_of_stops',
			'routeTotalCost'        : 'total_cost',
			'travelDuration'        : 'travel_time', 
			'waitDuration'          : 'idle_time', 
			'delayDuration'         : 'delay_duration', 
			'breakDuration'         : 'break_duration', 
			'visitDuration'         : 'visit_duration', 
			'totalDuration'         : 'total_duration', 
			'travelDistanceMeters'  : 'distance', 
			'maxLoads'              : 'max_loads',
			'routePolyline'         : 'route_polyline', 
			'geometry'              : 'geometry'
		}

		assigned_visits = self.visits
		assigned_routes = []

		for index, r in enumerate(self.response['routes']):
			if 'visits' in r:
				r['number_of_stops'] = len(assigned_visits[assigned_visits['vehicle_name'] == r['vehicleLabel']])

				if 'metrics' in r.keys():
					for k, v in r['metrics'].items():
						r[k] = v

				if 'routePolyline' in r.keys():
					r['overview_polyline'] = r['routePolyline']
					r['geometry'] = to_shapely(decode_polyline(r['overview_polyline']['points']))

				assigned_routes.append(r)

			if 'maxLoads' in r:
				for k, v in r.get('maxLoads').items():
					if k in FLEET_DIMENSIONS:
						r[k] = int(v.get('amount'))

		assigned_routes = pandas.DataFrame(assigned_routes)
		assigned_routes = assigned_routes.reindex(columns=list(columns.keys())+FLEET_DIMENSIONS)
		assigned_routes = assigned_routes.sort_values(by='vehicleIndex', ascending=True)
		assigned_routes = assigned_routes.rename(columns=columns)

		assigned_routes = drop_null_columns(assigned_routes, columns=FLEET_DIMENSIONS)

		time_metrics = [
			'travel_time',
			'idle_time',
			'delay_duration',
			'break_duration',
			'visit_duration',
			'total_duration'
		]

		assigned_routes['distance'] = assigned_routes['distance']/1000
		assigned_routes['distance_text'] = assigned_routes['distance'].apply(lambda x: '{:,.1f} km'.format(x))

		for k in time_metrics:
			assigned_routes[k] = assigned_routes[k].apply(lambda s: int(s[:-1])//60)
			assigned_routes['{}_text'.format(k)] = assigned_routes[k].apply(lambda x: to_timestr(x))

		assigned_routes['total_cost_text'] = assigned_routes['total_cost'].apply(lambda x: '{:,.1f} {}'.format(x, self.currency))

		self._data['routes'] = FleetRoutingEntity(to_geo(assigned_routes, from_='geometry'))

		return self

	def __parse_metrics(self):
		if self.response is not None:
			dict_metrics = {
				'travel_time'   : 'travelDuration',
				'idle_time'     : 'waitDuration',
				'delay_duration': 'delayDuration',
				'break_duration': 'breakDuration',
				'service_time'  : 'visitDuration',
				'total_duration': 'totalDuration'
			}

			self._metrics['total_cost'] = self.response['metrics']['totalCost']
			self._metrics['number_of_vehicles_used'] = self.response['metrics']['usedVehicleCount']
			self._metrics['number_of_skipped_mandatory_shipments'] = self.response['metrics']['skippedMandatoryShipmentCount']

			agg_metrics = self.response['metrics']['aggregatedRouteMetrics']

			for k, v in dict_metrics.items():
				m = int(agg_metrics[v][:-1])
				self._metrics[k] = m//60
				self._metrics['{}_text'.format(k)] = to_timestr(m)

			self._metrics['total_distance'] = agg_metrics['travelDistanceMeters']/1000
			self._metrics['total_distance_text'] = '{:,.1f} km'.format(self._metrics['total_distance'])

		return self

	def parse_response(self):
		if self.response is not None:			
			self.__parse_visits()
			self.__parse_skipped_visits()
			self.__parse_routes()
			self.__parse_metrics()

		return self

	def load_solution(self, pathname=None, filename='solution.json'):
		if not filename.lower().endswith('.zip'):
			self.response = read_json(pathname=pathname, filename=filename)

		else:
			with zipfile.ZipFile(ospathjoin(pathname=pathname, filename=filename), 'r') as z:
				with z.open('solution.json', 'r') as f:
					self.response = json.loads(f.read())

		return self.parse_response()

	@property
	def metrics(self):
		return self._metrics

	@property
	def number_of_skipped_mandatory_shipments(self):
		return self._metrics['number_of_skipped_mandatory_shipments']

	@property
	def number_of_vehicles_used(self):
		return self._metrics['number_of_vehicles_used']

	@property
	def total_cost(self):
		return self._metrics['total_cost']

	@property
	def total_distance(self):
		return self._metrics['total_distance']

	@property
	def total_duration(self):
		return self._metrics['total_duration']

	@property 
	def average_service_time(self):
		if self.routes is not None:
			return (self.routes['visit_duration'].sum()/self.total_duration)*100
		else:
			return None

	@property 
	def average_travel_time(self):
		if self.routes is not None:
			return (self.routes['travel_time'].sum()/self.total_duration)*100
		else:
			return None

	@property
	def number_of_routes(self):
		if self.routes is not None:
			return len(self.routes)
		else:
			return None

	@property
	def number_of_visits(self):
		if self.routes is not None:
			return len(self.visits)
		else:
			return None

	@property
	def number_of_skipped_visits(self):
		if self.routes is not None:
			return len(self.skipped_visits)
		else:
			return None

	@property 
	def overall_productivity(self):
		if self.routes is not None:
			return self.number_of_visits/self.number_of_routes
		else:
			return None

	def to_pickle(self, pathname='.', filename='problem.pickle'):
		to_pickle(self, pathname=pathname, filename=filename)

		return self

	def describe(self):
		print('\nSummary:')
		print('{:6d} shipments'.format(len(self.shipments)))if self.shipments is not None else None
		print('{:6d} depots'.format(len(self.depots))) if self.depots is not None else None
		print('{:6d} vehicles'.format(len(self.vehicles))) if self.vehicles is not None else None

		if self._response is not None:
			print('\nKPIs:')
			print('   Number of routes: {:d}     '.format(self.number_of_routes))
			print('   Skipped visits:   {:d}     '.format(self.number_of_skipped_visits))
			print('   Productivity:     {:.1f}   '.format(self.overall_productivity))
			print('   Distance:         {:.3f} km'.format(self.total_distance))
			print('   Average distance: {:.3f} km'.format(self.total_distance/self.number_of_routes))
			print('   Service time:     {:.0f} % '.format(self.average_service_time))
			print('   Travel time:      {:.0f} % '.format(self.average_travel_time))
			print('   Total cost:       {:.1f} {}'.format(self.total_cost, self.currency))

		return self

	@staticmethod
	def __get_basemap(basemap_label):
		basemap = None

		match basemap_label:
			case 'darkmatter':
				basemap = basemaps.darkmatter
			case 'positron':
				basemap = basemaps.positron
			case 'voyager':
				basemap = basemaps.voyager

			case _:
				raise ValueError("Oops! Something went wrong.")

		return basemap	

	def plot_scenario(self, expr=None, custom_styles=None, custom_popups=None, basemap_label='positron', visible_layers=('shipments', 'depots', 'stores')):
		styles = {
			'shipments': basic_style(
				size=10,
				color='#4285F4',
				stroke_color='white',
				stroke_width=1,
				opacity=0.9
			),
			'depots': basic_style(
				size=20,
				color='#DB4437',
				stroke_color='white',
				stroke_width=2,
				opacity=0.9
			),
			'stores': basic_style(
				size=15,
				color='#F4B400',
				stroke_color='white',
				stroke_width=2,
				opacity=0.9
			)
		}

		if custom_styles is not None:
			for k, v in custom_styles.items():
				styles[k] = v

		layers = []

		if 'shipments' in visible_layers:
			if self.shipments is not None:
				if expr is not None:
					shipments = self.shipments.where(expr=expr)
				else:
					shipments = self.shipments

				layers.append(
					Layer(
						shipments, 
						style=styles.get('shipments')
					)
				)

		if 'stores' in visible_layers:
			if self.stores is not None:
				layers.append(
					Layer(
						self.stores, 
						style=styles.get('stores')
					)
				)

		if 'depots' in visible_layers:
			if self.depots is not None:
				if expr is not None:
					depots = self.depots.where(expr=expr)
				else:
					depots = self.depots

				layers.append(
					Layer(
						depots, 
						style=styles.get('depots')
					)
				)
		
		return Map(
			layers, 
			basemap=self.__get_basemap(basemap_label)
		)

	def plot_solution(self, expr=None, custom_styles=None, custom_popups=None, basemap_label='positron', visible_layers=('routes', 'visits', 'depots')):
		styles = {
			'routes': basic_style(
				size=3,
				color='#4CC8A3',
				opacity=0.9
			),
			'shipments': basic_style(
				size=10,
				color='#B3B3B3',
				stroke_color='white',
				stroke_width=1,
				opacity=0.9
			),
			'visits': basic_style(
				size=10,
				color='#4285F4',
				stroke_color='white',
				stroke_width=1,
				opacity=0.9
			),
			'depots': basic_style(
				size=20,
				color='#DB4437',
				stroke_color='white',
				stroke_width=2,
				opacity=0.9
			),
			'stores': basic_style(
				size=15,
				color='#F4B400',
				stroke_color='white',
				stroke_width=2,
				opacity=0.9
			)
		}

		if custom_styles is not None:
			for k, v in custom_styles.items():
				styles[k] = v

		popups = {
			'depots': {
				'popup_click': [
					popup_element('depot_name', 'Depot name'),
				]
			},
			'visits': {
				'popup_click': [
					popup_element('shipment_name', 'Shipment name'),
					popup_element('formatted_address', 'Address'),
					popup_element('vehicle_name', 'Assigned vehicle name'),
					popup_element('assigned_date', 'Assigned date'),
					popup_element('assigned_time', 'Assigned time'),
					popup_element('assigned_route_order_id', 'Route order id')
				]
			},
			'routes': {
				'popup_click' : [
					popup_element('vehicle_name', 'Vehicle name'),
					popup_element('distance_text', 'Distance'),
					popup_element('total_duration_text', 'Duration'),
					popup_element('visit_duration_text', 'Service time'),
					popup_element('travel_time_text', 'Travel time'),
					popup_element('total_cost_text', 'Cost')
				]
			}			
		}

		if custom_popups is not None:
			for k, v in custom_popups.items():
				popups[k] = v

		layers = []

		if 'routes' in visible_layers:
			if self.routes is not None:
				if expr is not None:
					routes = self.routes.where(expr=expr)
				else:
					routes = self.routes

				layers.append(
					Layer(
						routes, 
						style=styles.get('routes'),
						popup_click=popups.get('routes').get('popup_click', None)
					)
				)

		if 'shipments' in visible_layers:
			if self.shipments is not None:
				layers.append(
					Layer(
						self.shipments, 
						style=styles.get('shipments')
					)
				)

		if 'visits' in visible_layers:
			if self.visits is not None:
				if expr is not None:
					visits = self.visits.where(expr=expr)
				else:
					visits = self.visits

				layers.append(
					Layer(
						visits, 
						style=styles.get('visits'),
						popup_click=popups.get('visits').get('popup_click', None)
					)
				)

		if 'stores' in visible_layers:
			if self.stores is not None:
				layers.append(
					Layer(
						self.stores, 
						style=styles.get('stores')
					)
				)

		if 'depots' in visible_layers:
			if self.depots is not None:
				layers.append(
					Layer(
						self.depots, 
						style=styles.get('depots'),
						popup_click=popups.get('depots').get('popup_click', None)
					)
				)
			
		return Map(
			layers, 
			basemap=self.__get_basemap(basemap_label)
		)

	def interac(self):
		#TO DO
		return None

def read_csv(filename, encoding='utf-8', delimiter=','):
	return FleetRoutingEntity(pandas.read_csv(filename, encoding=encoding, delimiter=delimiter))