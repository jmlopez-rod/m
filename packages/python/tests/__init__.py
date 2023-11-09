from m.core import Issue
from m.testing import block_m_side_effects, block_network_access

# Disabling yaml output - during tests we want to focus on json data
Issue.yaml_traceback = False

originals = block_m_side_effects()
block_network_access()
