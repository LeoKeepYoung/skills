#!/usr/bin/env python3
"""Read Garmin coaching summaries; never upload, edit, or delete account data."""

import argparse
from datetime import date, datetime, timedelta, timezone
from getpass import getpass
import json
import logging
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from zoneinfo import ZoneInfo

DEFAULT_STATE = Path.home() / '.local/share/fitness-coach/garmin'
PAGE_SIZE = 100
MAX_PAGES = 5


class SyncError(Exception):
    """Only sanitized, user-facing error codes belong in this exception."""


def number(value, divisor=1):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not math.isfinite(value) or value < 0:
        return None
    return round(value / divisor, 3)


def nested(data, *keys):
    for key in keys:
        if not isinstance(data, dict):
            return None
        data = data.get(key)
    return data


def summary(data, fields):
    if data is not None and not isinstance(data, dict):
        raise ValueError('Unexpected response shape')
    return {name: number(nested(data, *path), scale)
            for name, path, scale in fields}


STATS = [
    ('steps', ('totalSteps',), 1),
    ('resting_heart_rate_bpm', ('restingHeartRate',), 1),
    ('total_energy_kcal_estimate', ('totalKilocalories',), 1),
    ('active_energy_kcal_estimate', ('activeKilocalories',), 1),
    ('moderate_minutes', ('moderateIntensityMinutes',), 1),
    ('vigorous_minutes', ('vigorousIntensityMinutes',), 1),
    ('stress_average', ('averageStressLevel',), 1),
    ('body_battery_high', ('bodyBatteryHighestValue',), 1),
    ('body_battery_low', ('bodyBatteryLowestValue',), 1),
]
SLEEP = [
    ('sleep_hours', ('dailySleepDTO', 'sleepTimeSeconds'), 3600),
    ('sleep_score', ('dailySleepDTO', 'sleepScores', 'overall', 'value'), 1),
]
HRV = [
    ('last_night_ms', ('hrvSummary', 'lastNightAvg'), 1),
    ('weekly_average_ms', ('hrvSummary', 'weeklyAvg'), 1),
    ('baseline_low_ms', ('hrvSummary', 'baseline', 'balancedLow'), 1),
    ('baseline_high_ms', ('hrvSummary', 'baseline', 'balancedUpper'), 1),
]


def error_code(exc):
    name = type(exc).__name__
    status = getattr(getattr(exc, 'response', None), 'status_code', None)
    if status is None:
        match = re.search(r'(?:API Error|HTTP|Error)\s*(\d{3})', str(exc))
        status = int(match[1]) if match else None
    if 'TooManyRequests' in name or status == 429:
        return 'rate_limited'
    if 'Authentication' in name or status in (401, 403):
        return 'authentication_required'
    if 'NotFound' in name or status in (400, 404):
        return 'unavailable'
    if isinstance(exc, (ValueError, TypeError, KeyError)):
        return 'unexpected_response'
    return 'request_failed'


def read_metric(call, normalize, delay=0.2):
    """Preserve missing data and stop the run on authentication/rate failures."""
    try:
        raw = call()
        data = normalize(raw)
        present = any(v is not None for v in data.values()) if isinstance(data, dict) else bool(data)
        return {'status': 'ok' if present else 'no_data', 'data': data}
    except Exception as exc:
        code = error_code(exc)
        if code in ('authentication_required', 'rate_limited'):
            raise SyncError(code) from None
        return {'status': 'error', 'code': code, 'data': None}
    finally:
        if delay:
            time.sleep(delay)


def date_window(days, end, tz_name):
    if not 1 <= days <= 31:
        raise SyncError('days_must_be_between_1_and_31')
    try:
        today = datetime.now(ZoneInfo(tz_name)).date()
        last = date.fromisoformat(end) if end else today - timedelta(days=1)
    except (ValueError, KeyError):
        raise SyncError('invalid_date_or_timezone') from None
    if last > today:
        raise SyncError('end_date_is_in_the_future')
    return [last - timedelta(days=offset) for offset in reversed(range(days))]


def normalize_activity(item):
    if not isinstance(item, dict) or item.get('activityId') is None:
        raise ValueError('Missing activity identity')
    return {
        'activity_id': item['activityId'],
        'start_local': item.get('startTimeLocal'),
        'type': nested(item, 'activityType', 'typeKey'),
        'duration_minutes': number(item.get('duration'), 60),
        'distance_km': number(item.get('distance'), 1000),
        'average_hr_bpm': number(item.get('averageHR')),
        'max_hr_bpm': number(item.get('maxHR')),
        'energy_kcal_estimate': number(item.get('calories')),
    }


def read_activities(api, start, end, delay=0.2):
    """Bound pagination and deduplicate by Garmin activity ID."""
    items, seen = [], set()
    for page in range(MAX_PAGES):
        params = {'startDate': start, 'endDate': end,
                  'start': str(page * PAGE_SIZE), 'limit': str(PAGE_SIZE)}

        def normalize(raw):
            if not isinstance(raw, list):
                raise ValueError('Expected activity list')
            return [normalize_activity(row) for row in raw]

        result = read_metric(
            lambda: api.connectapi(api.garmin_connect_activities, params=params),
            normalize, delay)
        if result['status'] == 'error':
            return {**result, 'data': items, 'complete': False}
        rows = result['data']
        for row in rows:
            # Range filtering uses Garmin's local activity date, not UTC.
            local = row['start_local']
            if not isinstance(local, str) or not start <= local[:10] <= end:
                return {'status': 'error', 'code': 'unexpected_activity_date',
                        'data': items, 'complete': False}
            if row['activity_id'] not in seen:
                seen.add(row['activity_id'])
                items.append(row)
        if len(rows) < PAGE_SIZE:
            return {'status': 'ok', 'data': items, 'complete': True}
    return {'status': 'error', 'code': 'pagination_limit',
            'data': items, 'complete': False}


def normalize_body(raw):
    if raw is None:
        return []
    if not isinstance(raw, dict) or not isinstance(raw.get('dateWeightList'), list):
        raise ValueError('Expected dateWeightList')
    rows = [
        {'calendar_date': row.get('calendarDate'),
         'weight_kg': number(row.get('weight'), 1000),
         'body_fat_percent_estimate': number(row.get('bodyFat'))}
        for row in raw['dateWeightList'] if isinstance(row, dict)
    ]
    return [row for row in rows if row['weight_kg'] is not None
            or row['body_fat_percent_estimate'] is not None]


def collect(api, dates, region, tz_name, delay=0.2):
    daily = []
    for day in dates:
        key = day.isoformat()
        record = {'date': key}
        for label, method, fields in [('stats', api.get_stats, STATS),
                                      ('sleep', api.get_sleep_data, SLEEP),
                                      ('hrv', api.get_hrv_data, HRV)]:
            record[label] = read_metric(lambda: method(key),
                                        lambda raw: summary(raw, fields), delay)
        daily.append(record)
    start, end = dates[0].isoformat(), dates[-1].isoformat()
    body = read_metric(lambda: api.get_body_composition(start, end), normalize_body, delay)
    activities = read_activities(api, start, end, delay)
    metrics = [day[key] for day in daily for key in ('stats', 'sleep', 'hrv')]
    metrics += [body, activities]
    has_data = any(bool(m['data']) and (m['status'] == 'ok' or isinstance(m['data'], list))
                   for m in metrics)
    incomplete = any(m['status'] == 'error' for m in metrics)
    return {
        'schema_version': 1,
        'source': 'Garmin Connect via unofficial garminconnect 0.3.17',
        'fetched_at_utc': datetime.now(timezone.utc).isoformat(),
        'region': region, 'date_timezone': tz_name,
        'date_basis': 'Garmin calendarDate / activity startTimeLocal',
        'range': {'start': start, 'end': end, 'days': len(dates)},
        'status': ('partial' if incomplete else 'ok') if has_data else 'no_data',
        'has_observations': has_data,
        'daily': daily, 'body_composition': body, 'activities': activities,
    }


def private_directory(path):
    path = path.expanduser().absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise SyncError('state_directory_must_not_be_a_symlink')
    if any((p / '.git').exists() for p in (path, *path.parents)):
        raise SyncError('state_directory_must_be_outside_git')
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.chmod(0o700)
    return path


def write_json(path, data):
    parent = private_directory(path.parent)
    fd, temp = tempfile.mkstemp(prefix='.snapshot-', dir=parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            os.chmod(temp, 0o600)
            json.dump(data, handle, ensure_ascii=False, indent=2, allow_nan=False)
            handle.write('\n')
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def save_snapshot(root, snapshot):
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    path = root / 'snapshots' / f'{stamp}.json'
    write_json(path, snapshot)
    # A no-data response must not destroy the last usable snapshot.
    if snapshot['has_observations']:
        write_json(root / 'latest.json', snapshot)
    return path


def make_client(region, email=None, password=None):
    try:
        from garminconnect import Garmin
    except ImportError:
        raise SyncError('install_requirements_garmin_first') from None
    return Garmin(email=email, password=password, is_cn=region == 'cn',
                  prompt_mfa=lambda: getpass('Garmin 验证码（不回显）：'),
                  retry_attempts=0)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('login', 'status', 'sync'))
    parser.add_argument('--region', choices=('global', 'cn'), default='cn',
                        help='Account region; defaults to the user-confirmed China region')
    parser.add_argument('--state-dir', type=Path, default=DEFAULT_STATE)
    parser.add_argument('--days', type=int, default=7)
    parser.add_argument('--end', help='Inclusive YYYY-MM-DD; defaults to yesterday')
    parser.add_argument('--timezone', default='Asia/Shanghai')
    args = parser.parse_args(argv)
    root = args.state_dir.expanduser().absolute() / args.region
    tokens = root / 'tokens'
    token_file = tokens / 'garmin_tokens.json'
    # Third-party errors may include credentials or response bodies.
    logging.disable(logging.CRITICAL)
    os.umask(0o077)
    try:
        if args.command == 'status':
            print(json.dumps({'region': args.region, 'token_cache_present': token_file.is_file(),
                              'live_authentication': 'not_checked',
                              'latest_snapshot_present': (root / 'latest.json').is_file()}))
            return 0
        dates = date_window(args.days, args.end, args.timezone)
        if args.command == 'login':
            if not sys.stdin.isatty():
                raise SyncError('login_requires_your_interactive_terminal')
            private_directory(root)
            private_directory(tokens)
            email = input('Garmin 邮箱：').strip()
            password = getpass('Garmin 密码（不回显）：')
            api = make_client(args.region, email, password)
            del password
        else:
            if not token_file.is_file():
                raise SyncError('login_required_run_login_in_your_terminal')
            private_directory(root)
            private_directory(tokens)
            api = make_client(args.region)
        result = api.login(str(tokens))
        if result and result[0]:
            raise SyncError('login_incomplete')
        api.client.dump(str(tokens))
        if args.command == 'login':
            print(json.dumps({'status': 'authenticated', 'region': args.region,
                              'next': 'Run sync with the same --region'}))
            return 0
        snapshot = collect(api, dates, args.region, args.timezone)
        output = save_snapshot(root, snapshot)
        print(json.dumps({'status': snapshot['status'], 'snapshot': str(output),
                          'range': snapshot['range'],
                          'activity_count': len(snapshot['activities']['data'])}, ensure_ascii=False))
        return {'ok': 0, 'partial': 3, 'no_data': 4}[snapshot['status']]
    except SyncError as exc:
        print(json.dumps({'status': 'error', 'code': str(exc)}), file=sys.stderr)
        return 2
    except (KeyboardInterrupt, EOFError):
        print('{"status":"cancelled"}', file=sys.stderr)
        return 2
    except Exception as exc:
        print(json.dumps({'status': 'error', 'code': error_code(exc)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
