import os
import time
from pathlib import Path
from unittest import TestCase
from unittest import mock

import cloudflarestatus


class MockResponse:
    def __init__(self, status_code=200, content=""):
        self.status_code = status_code
        self.content = content


class TestCloudflarestatus(TestCase):
    def setUp(self):
        self.data_dir = Path(os.path.dirname(__file__)) / "data"
        self.now = int(time.time())

    @mock.patch("time.time")
    @mock.patch("requests.Session")
    def test_dc(self, mock_session, mock_time):
        with open(self.data_dir / "content.html", "r") as f:
            content = f.read()
            mock_session.return_value.get.return_value = MockResponse(200, content)
        mock_time.return_value = self.now

        all_dc_status = cloudflarestatus.dc()
        self.assertEqual(len(all_dc_status.keys()), 296)

        syd_hba_dc_status = cloudflarestatus.dc("SYD", "HBA")
        self.assertEqual(
            syd_hba_dc_status,
            {
                "HBA": {
                    "code": "HBA",
                    "name": "Hobart, Australia",
                    "status": "partial_outage",
                    "timestamp": self.now,
                },
                "SYD": {
                    "code": "SYD",
                    "name": "Sydney, NSW, Australia",
                    "status": "operational",
                    "timestamp": self.now,
                },
            },
        )

        hba_dc_status = cloudflarestatus.dc("HBA")
        self.assertEqual(
            hba_dc_status,
            {
                "HBA": {
                    "code": "HBA",
                    "name": "Hobart, Australia",
                    "status": "partial_outage",
                    "timestamp": self.now,
                },
            },
        )

    @mock.patch("time.sleep")
    @mock.patch("requests.Session")
    def test_400_dc(self, mock_session, mock_sleep):
        mock_session.return_value.get.return_value = MockResponse(400)

        with self.assertRaises(cloudflarestatus.CloudflarestatusException):
            cloudflarestatus.dc()
