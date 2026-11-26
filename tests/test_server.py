__author__ = "Mário Antunes"
__version__ = "1.0.0"
__email__ = "mario.antunes@ua.pt"
__status__ = "Development"

import unittest

from server.server import VIEWER_DIR, SpaceInvadersGameServer, parse_args


class TestServer(unittest.TestCase):
    def test_defaults(self):
        args = parse_args([])
        self.assertEqual((args.host, args.port, args.seed, args.fps), ("0.0.0.0", 8765, None, 30))

    def test_seed_short_and_long(self):
        self.assertEqual(parse_args(["-s", "5"]).seed, 5)
        self.assertEqual(parse_args(["--seed", "9"]).seed, 9)

    def test_server_definition(self):
        srv = SpaceInvadersGameServer(seed=1, fps=20)
        self.assertTrue(srv.is_real_time)
        self.assertEqual(srv.fps, 20)
        self.assertEqual(srv.game.seed, 1)
        self.assertEqual(srv.static_dirs, [str(VIEWER_DIR)])
        self.assertTrue((VIEWER_DIR / "index.html").is_file())
        self.assertEqual(srv.get_setup_payload(), {"width": 11, "height": 11})


if __name__ == "__main__":
    unittest.main()
