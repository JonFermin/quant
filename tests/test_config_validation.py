import unittest

from strategies.lgbm_alpha158 import (
    ConfigValidationError,
    _apply_overrides,
    load_config,
    validate_config,
)


class TestConfigValidation(unittest.TestCase):
    def test_default_config_is_valid(self):
        config = load_config()
        validate_config(config)

    def test_missing_top_level_key_raises(self):
        config = load_config()
        config.pop("task")
        with self.assertRaises(ConfigValidationError):
            validate_config(config)

    def test_override_test_window_updates_dataset_and_backtest(self):
        config = load_config()
        updated = _apply_overrides(config, test_start="2024-01-01", test_end="2024-12-31")
        self.assertEqual(
            updated["task"]["dataset"]["kwargs"]["segments"]["test"],
            ["2024-01-01", "2024-12-31"],
        )
        self.assertEqual(
            updated["port_analysis_config"]["backtest"]["start_time"], "2024-01-01"
        )
        self.assertEqual(updated["port_analysis_config"]["backtest"]["end_time"], "2024-12-31")


if __name__ == "__main__":
    unittest.main()
