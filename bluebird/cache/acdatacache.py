"""
Contains the class for storing aircraft data which is streamed from the simulation
"""

from .base import Cache, generate_extras


# TODO Call clear when sim reset
class AcDataCache(Cache):
	"""
	Holds the most recent aircraft data
	"""

	def get(self, key):
		"""
		Get data for an aircraft
		:param key: An aircraft identifier
		:return: Aircraft information
		"""

		acid = key.upper()

		# If requested, just return the complete aircraft data
		if acid == 'ALL':
			return list(self.store.values())

		return super().get(acid)

	def fill(self, data):

		if isinstance(data, dict) and 'id' in data:

			# TODO Can definitely tidy this up
			for idx in range(len(data['id'])):
				acid = data['id'][idx]

				ac_data = {'acid': data['id'][idx], 'alt': data['alt'][idx], 'lat': data['lat'][idx],
                   'lon': data['lon'][idx], 'gs': data['gs'][idx], 'vs': data['vs'][idx]}

				self.store[acid] = {**ac_data, **generate_extras()}
