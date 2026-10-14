"""Credential-free behavioral tests; no real account or network calls."""

from datetime import date, datetime, timedelta
import importlib.util
import io
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch
from contextlib import redirect_stdout
from zoneinfo import ZoneInfo

spec = importlib.util.spec_from_file_location('garmin_sync', Path(__file__).with_name('garmin_sync.py'))
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)


class FakeAPI:
    garmin_connect_activities = '/activitylist-service/activities/search/activities'

    def get_stats(self, day):
        return {'totalSteps': 0, 'restingHeartRate': -1, 'totalKilocalories': 2100,
                'activeKilocalories': 300, 'userProfileId': 'PRIVATE_ACCOUNT'}

    def get_sleep_data(self, day):
        return {'dailySleepDTO': {'sleepTimeSeconds': 25200,
                                 'sleepScores': {'overall': {'value': 80}}}}

    def get_hrv_data(self, day):
        return None

    def get_body_composition(self, start, end):
        return {'dateWeightList': [{'calendarDate': start, 'weight': 72300,
                                   'bodyFat': 21, 'samplePk': 'PRIVATE_ID'}]}

    def connectapi(self, url, params):
        return []


def activity(identity):
    return {'activityId': identity, 'startTimeLocal': '2026-10-13 08:00:00',
            'activityType': {'typeKey': 'strength_training'}, 'duration': 1800,
            'distance': 1500, 'startLatitude': 'PRIVATE_GPS',
            'activityName': 'PRIVATE_TITLE', 'calories': 200}


class GarminSyncTests(unittest.TestCase):
    def collect(self, api=None):
        return sync.collect(api or FakeAPI(), [date(2026, 10, 13)],
                            'global', 'Asia/Shanghai', delay=0)

    def test_units_missing_values_and_allowed_fields(self):
        data = self.collect()
        day = data['daily'][0]
        self.assertEqual(day['stats']['data']['steps'], 0)
        self.assertIsNone(day['stats']['data']['resting_heart_rate_bpm'])
        self.assertEqual(day['sleep']['data']['sleep_hours'], 7)
        self.assertEqual(day['hrv']['status'], 'no_data')
        self.assertIsNone(day['hrv']['data']['last_night_ms'])
        self.assertEqual(data['body_composition']['data'][0]['weight_kg'], 72.3)
        self.assertEqual(day['stats']['data']['total_energy_kcal_estimate'], 2100)
        self.assertNotIn('PRIVATE_', json.dumps(data))
        row = sync.normalize_activity(activity(1))
        self.assertEqual(row['duration_minutes'], 30)
        self.assertEqual(row['distance_km'], 1.5)
        self.assertNotIn('PRIVATE_', json.dumps(row))

    def test_pagination_deduplicates_and_records_completion(self):
        api = FakeAPI()
        pages = [[activity(1), activity(2)], [activity(2), activity(3)], []]
        calls = []

        def fetch(url, params):
            calls.append(dict(params))
            return pages[int(params['start']) // 2]

        api.connectapi = fetch
        with patch.object(sync, 'PAGE_SIZE', 2):
            result = sync.read_activities(api, '2026-10-13', '2026-10-13', delay=0)
        self.assertEqual([a['activity_id'] for a in result['data']], [1, 2, 3])
        self.assertTrue(result['complete'])
        self.assertEqual([x['start'] for x in calls], ['0', '2', '4'])
        self.assertTrue(all(x['startDate'] == '2026-10-13' for x in calls))

    def test_repeating_page_is_bounded_and_partial(self):
        api = FakeAPI()
        api.connectapi = lambda *args, **kwargs: [activity(1)]
        with patch.object(sync, 'PAGE_SIZE', 1), patch.object(sync, 'MAX_PAGES', 2):
            result = sync.read_activities(api, '2026-10-13', '2026-10-13', delay=0)
        self.assertFalse(result['complete'])
        self.assertEqual(result['code'], 'pagination_limit')
        self.assertEqual(len(result['data']), 1)

    def test_only_partial_activities_still_count_as_observations(self):
        api = FakeAPI()
        api.get_stats = api.get_sleep_data = api.get_hrv_data = lambda day: None
        api.get_body_composition = lambda *args: {'dateWeightList': [{'weight': None}]}
        api.connectapi = lambda *args, **kwargs: [activity(1)]
        with patch.object(sync, 'PAGE_SIZE', 1), patch.object(sync, 'MAX_PAGES', 1):
            result = self.collect(api)
        self.assertEqual(result['status'], 'partial')
        self.assertTrue(result['has_observations'])
        self.assertEqual(result['body_composition']['status'], 'no_data')

    def test_authentication_and_rate_limit_stop_subsequent_calls(self):
        for status in (401, 403, 429):
            api = FakeAPI()

            def fail(*args):
                raise RuntimeError(f'API Error {status} PRIVATE_TOKEN')

            api.get_stats = fail
            with patch.object(api, 'get_sleep_data') as sleep:
                with self.assertRaises(sync.SyncError) as raised:
                    self.collect(api)
                sleep.assert_not_called()
            self.assertNotIn('PRIVATE_TOKEN', str(raised.exception))

    def test_optional_metric_failure_keeps_other_data(self):
        api = FakeAPI()

        def fail(day):
            raise RuntimeError('API Error 404 PRIVATE_RESPONSE')

        api.get_hrv_data = fail
        result = self.collect(api)
        self.assertEqual(result['status'], 'partial')
        self.assertEqual(result['daily'][0]['hrv']['code'], 'unavailable')
        self.assertEqual(result['daily'][0]['sleep']['status'], 'ok')
        self.assertNotIn('PRIVATE_RESPONSE', json.dumps(result))

    def test_nulls_and_negative_sentinels_are_not_fabricated(self):
        for value in (-1, None, '50', True, float('nan'), float('inf')):
            self.assertIsNone(sync.number(value))
        self.assertEqual(sync.number(0), 0)
        result = sync.read_metric(lambda: [], lambda x: sync.summary(x, sync.STATS), delay=0)
        self.assertEqual(result['code'], 'unexpected_response')

    def test_no_data_does_not_overwrite_last_usable_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve() / 'state'
            previous = self.collect()
            sync.save_snapshot(root, previous)
            old = (root / 'latest.json').read_bytes()
            snapshot_path = sync.save_snapshot(root, {'has_observations': False, 'status': 'no_data'})
            self.assertEqual((root / 'latest.json').read_bytes(), old)
            self.assertTrue(snapshot_path.exists())
            self.assertEqual(stat.S_IMODE(snapshot_path.stat().st_mode), 0o600)
            self.assertEqual(stat.S_IMODE(snapshot_path.parent.stat().st_mode), 0o700)

    def test_state_inside_git_and_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            (root / '.git').mkdir()
            with self.assertRaisesRegex(sync.SyncError, 'outside_git'):
                sync.private_directory(root / 'state')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            (root / 'link').symlink_to(root, target_is_directory=True)
            with self.assertRaisesRegex(sync.SyncError, 'symlink'):
                sync.private_directory(root / 'link' / 'state')

    def test_window_is_inclusive_bounded_and_uses_requested_timezone(self):
        days = sync.date_window(7, '2026-10-13', 'Asia/Shanghai')
        self.assertEqual(days[0], date(2026, 10, 7))
        self.assertEqual(days[-1], date(2026, 10, 13))
        today = datetime.now(ZoneInfo('Asia/Shanghai')).date()
        self.assertEqual(sync.date_window(1, None, 'Asia/Shanghai'), [today - timedelta(days=1)])
        for count in (0, 32):
            with self.assertRaises(sync.SyncError):
                sync.date_window(count, None, 'Asia/Shanghai')
        with self.assertRaises(sync.SyncError):
            sync.date_window(1, (today + timedelta(days=1)).isoformat(), 'Asia/Shanghai')

    def test_status_does_not_authenticate_or_claim_connected(self):
        with tempfile.TemporaryDirectory() as temp:
            output = io.StringIO()
            with patch.object(sync, 'make_client') as client, redirect_stdout(output):
                result = sync.main(['status', '--state-dir', temp])
                client.assert_not_called()
            self.assertEqual(result, 0)
            data = json.loads(output.getvalue())
            self.assertFalse(data['token_cache_present'])
            self.assertEqual(data['region'], 'cn')
            self.assertEqual(data['live_authentication'], 'not_checked')


if __name__ == '__main__':
    unittest.main()
