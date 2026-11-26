import json
import math
import unittest

from server.logic import Alien, Laser, SpaceInvaders

PATTERNS = ('classic_homing', 'late_homing', 'zigzag', 'sine_wave',
            'feint', 'accelerating_dive', 'laser_dodge', 'adaptive_hunter')
UNLOCKS = (1, 3, 5, 7, 10, 13, 16, 20)


def diver(pattern, x=5, y=8):
    a = Alien(0, x, y)
    a.start_dive(x, speed=10, pattern=pattern)
    return a


class TestEpicAttackPatterns(unittest.TestCase):
    def test_epic_classic(self):
        g = SpaceInvaders(difficulty='classic')
        for wave in (1, 20, 100):
            g.wave = wave
            self.assertEqual(g.available_patterns(), PATTERNS[:1])

    def test_epic_hardcore(self):
        self.assertEqual(SpaceInvaders(difficulty='hardcore').available_patterns(), PATTERNS)

    def test_epic_progressive_unlocks(self):
        g = SpaceInvaders(difficulty='progressive')
        for wave in range(1, 25):
            with self.subTest(wave=wave):
                g.wave = wave
                self.assertEqual(g.available_patterns(), tuple(p for p, w in zip(PATTERNS, UNLOCKS) if w <= wave))

    def test_epic_invalid_mode(self):
        with self.assertRaises(ValueError):
            SpaceInvaders(difficulty='invalid')

    def test_epic_classic_homing(self):
        a = diver('classic_homing', y=2.5)
        a.update(.05, 0, player_x=8)
        self.assertEqual(a.target_x, 5)
        self.assertAlmostEqual(a.x, 5)

    def test_epic_late_homing(self):
        a = diver('late_homing', y=2.5)
        a.update(.05, 0, player_x=8)
        self.assertEqual(a.target_x, 8)
        self.assertGreater(a.x, 5)
        a.y = 1.9
        a.update(.01, 0, player_x=2)
        self.assertEqual(a.target_x, 8)

    def test_epic_zigzag(self):
        a = diver('zigzag')
        a.update(.1, 0)
        self.assertGreater(a.x, 5)
        a.x = 5
        a.dive_elapsed = .30
        a.update(.1, 0)
        self.assertLess(a.x, 5)

    def test_epic_sine_wave(self):
        a = diver('sine_wave')
        a.update(.1, 0)
        self.assertGreater(a.x, 5)
        a.x = 5
        a.dive_elapsed = .4
        a.update(.1, 0)
        self.assertLess(a.x, 5)

    def test_epic_feint(self):
        a = diver('feint')
        a.y = 4.5
        a.update(.05, 0)
        self.assertLess(a.x, 5)
        a.x = 5
        a.y = 3
        a.update(.05, 0)
        self.assertAlmostEqual(a.x, 5)

    def test_epic_acceleration(self):
        a = diver('accelerating_dive')
        a.update(.1, 0)
        early = 8 - a.y
        a.y = 3
        a.update(.1, 0)
        self.assertGreater(3 - a.y, early)

    def test_epic_laser_dodge(self):
        a = diver('laser_dodge')
        a.update(.1, 0, lasers=[Laser(5, 7)])
        self.assertGreater(a.x, 5)
        for laser in (Laser(5, 9), Laser(8, 7), Laser(5, 3)):
            a = diver('laser_dodge')
            a.update(.1, 0, lasers=[laser])
            self.assertAlmostEqual(a.x, 5)
        laser = Laser(5, 7)
        laser.active = False
        a = diver('laser_dodge')
        a.update(.1, 0, lasers=[laser])
        self.assertAlmostEqual(a.x, 5)

    def test_epic_adaptive_hunter(self):
        a, b = diver('adaptive_hunter'), diver('adaptive_hunter')
        a.update(.1, 0, lasers=[Laser(5, 7)])
        b.update(.1, 0)
        self.assertGreater(a.x, b.x)
        self.assertLess(b.y, 8)
        self.assertGreater(b.x, 5)

    def test_epic_all_patterns_finite_and_descending(self):
        for pattern in PATTERNS:
            with self.subTest(pattern=pattern):
                a = diver(pattern)
                while a.y > 0:
                    previous = a.y
                    a.update(1/30, 0, player_x=9, lasers=[Laser(a.x, a.y-1)])
                    self.assertTrue(math.isfinite(a.x) and math.isfinite(a.y))
                    self.assertLess(a.y, previous)
                    if pattern != 'classic_homing':
                        self.assertTrue(0 <= a.x <= 10)

    def test_epic_scheduler_and_seed(self):
        def sequence(mode, wave):
            g = SpaceInvaders(seed=42, difficulty=mode)
            g.wave = wave
            result = []
            for _ in range(80):
                g.time_since_last_dive = 10
                g.update(0)
                a = next(a for a in g.aliens if a.is_diving)
                self.assertIn(a.pattern, g.available_patterns())
                result.append((a.index, a.pattern))
                a.reset_dive()
            return result
        for mode, wave in [('classic', 20), ('progressive', 7), ('hardcore', 1)]:
            self.assertEqual(sequence(mode, wave), sequence(mode, wave))
        self.assertEqual({p for _, p in sequence('hardcore', 1)}, set(PATTERNS))

    def test_epic_viewer_serialization(self):
        for mode in ('classic', 'progressive', 'hardcore'):
            g = SpaceInvaders(difficulty=mode)
            g.shoot_laser()
            for pattern in PATTERNS:
                g.aliens[0].start_dive(5, pattern=pattern)
                state = json.loads(json.dumps(g.get_viewer_state()))
                self.assertEqual(state['difficulty'], mode)
                self.assertEqual(state['aliens'][0]['pattern'], pattern)
                self.assertEqual(state['aliens'][1]['pattern'], 'formation')
                self.assertEqual(state['lasers'][0]['x'], 5)
            g.reset_game()
            self.assertEqual(g.difficulty, mode)
            self.assertEqual(g.wave, 1)


if __name__ == '__main__':
    unittest.main()
