import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from engineering.agent_channel_gate import ChannelRequest, ScopedGrant, authorize


class ChannelGateTests(unittest.TestCase):
    def setUp(self):
        self.grant = ScopedGrant('agent-1', 'tenant-A', frozenset({'packages.readonly'}), frozenset({'read'}), True)

    def test_explicit_read(self):
        self.assertTrue(authorize(ChannelRequest('agent-1','tenant-A','packages.readonly','read'),self.grant))
    def test_artifact_message_board_denied(self):
        self.assertFalse(authorize(ChannelRequest('agent-1','tenant-A','packages.readonly','write'),self.grant))
    def test_indirect_proxy_egress_denied(self):
        self.assertFalse(authorize(ChannelRequest('agent-1','tenant-A','arbitrary.internet','http'),self.grant))
    def test_cross_tenant_denied(self):
        self.assertFalse(authorize(ChannelRequest('agent-1','tenant-B','packages.readonly','read'),self.grant))
    def test_cross_agent_denied(self):
        self.assertFalse(authorize(ChannelRequest('agent-2','tenant-A','packages.readonly','read'),self.grant))
    def test_no_grant_denied(self):
        self.assertFalse(authorize(ChannelRequest('agent-1','tenant-A','packages.readonly','read'),None))
    def test_unapproved_grant_denied(self):
        denied=ScopedGrant('agent-1','tenant-A',frozenset({'packages.readonly'}),frozenset({'read'}),False)
        self.assertFalse(authorize(ChannelRequest('agent-1','tenant-A','packages.readonly','read'),denied))
    def test_empty_destination_denied(self):
        self.assertFalse(authorize(ChannelRequest('agent-1','tenant-A','','read'),self.grant))

if __name__=='__main__':
    unittest.main()
