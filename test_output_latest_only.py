#!/usr/bin/env python3
import runpy
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parent
RUN_PY = REPO_ROOT / "run.py"


class OutputLatestOnlyTest(unittest.TestCase):
    def test_output_csv_only_keeps_output_latest(self):
        with patch("urllib.request.urlopen", side_effect=Exception("offline")):
            mod = runpy.run_path(str(RUN_PY), run_name="not_main")

        output_csv = mod["output_csv"]

        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            verified = base / "verified.txt"
            verified.write_text(
                "IP地址,端口,TLS,数据中心,地区,城市,网络延迟,下载速度,ASN\n"
                "1.1.1.1,443,TRUE,HKG,HK,Hong Kong,10,1024,AS13335\n"
            )
            (base / "output_old.csv").write_text("old\n")
            (base / "custom.csv").write_text("old\n")

            output_csv.__globals__["BASE"] = base
            output_csv.__globals__["get_public_ip"] = lambda: "127.0.0.1"
            output_csv.__globals__["ensure_download_server"] = lambda: None

            output_csv(["209242"])

            csv_files = sorted(p.name for p in base.glob("*.csv"))
            self.assertEqual(csv_files, ["output_latest.csv"])
            self.assertIn("1.1.1.1,443,TRUE,HKG,HK,Hong Kong,10,1024,AS13335", (base / "output_latest.csv").read_text())


if __name__ == "__main__":
    unittest.main()
