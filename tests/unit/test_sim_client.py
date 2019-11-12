"""
Contains a mock SimClient implementation for use in testing
"""

from bluebird.sim_client.abstract_sim_client import AbstractSimClient


# class TestSimClient(AbstractSimClient):
class TestSimClient:
    """
    Mock SimClient for use in testing
    """


### OLD ###

#     class TestBlueSkyClient(BlueSkyClient):
#         """
#         Mock BlueSky client for use in testing
#         """

#         def __init__(self):
#             super().__init__(sim_state, ac_data)
#             self.last_stack_cmd = None
#             self.last_scenario = None
#             self.last_dtmult = None
#             self.was_reset = False
#             self.was_stepped = False
#             self.seed = None
#             self.scn_uploaded = False

#         def send_stack_cmd(self, data=None, response_expected=False, target=b"*"):
#             self._logger.debug(f"STACK {data} response_expected={response_expected}")
#             self.last_stack_cmd = data

#         def load_scenario(self, filename, speed=1.0, start_paused=False):
#             self._logger.debug(f"load_scenario {filename} {speed} {start_paused}")
#             self.last_scenario = filename
#             self.last_dtmult = speed
#             self._ac_data.fill(TEST_DATA)

#         def reset_sim(self):
#             self.was_reset = True

#         def upload_new_scenario(self, name, lines):
#             self._logger.debug(f"upload_new_scenario, {name}")
#             self.scn_uploaded = True

#         def step(self):
#             self.was_stepped = True
