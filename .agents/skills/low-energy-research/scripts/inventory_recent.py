"""Bounded metadata discovery only. File dates are leads, never experimental conclusions."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path

SKIP = {'.git', '.agents', '.planning', '.work', '.internal', 'node_modules', '__pycache__'}
EXTENSIONS = {'.md', '.txt', '.log', '.json', '.pptx', '.pdf', '.xlsx', '.xls', '.csv', '.tsv', '.png', '.jpg', '.jpeg', '.tif', '.tiff', '.asc', '.dat', '.pl2', '.nex', '.nex5', '.opju', '.opj', '.pzfx', '.prism', '.py', '.ipf'}


def inventory(roots, since, limit=5000, max_depth=6, exclude=None):
    result = {'since': since, 'date_meaning': 'mtime discovery hint only; verify actual experiment/report date', 'files': [], 'unavailable': [], 'truncated': False, 'depth_limited': [], 'scanned_files': 0}
    seen = set()
    threshold = dt.date.fromisoformat(since)
    excluded = Path(exclude).resolve() if exclude else None
    for root in roots:
        root = Path(root).resolve()
        if not root.is_dir():
            result['unavailable'].append(str(root))
            continue
        def onerror(error): result['unavailable'].append(str(error))
        for current, dirs, files in os.walk(root, followlinks=False, onerror=onerror):
            current = Path(current)
            dirs[:] = sorted(d for d in dirs if d not in SKIP and not (current / d).is_symlink() and not (hasattr(current / d, 'is_junction') and (current / d).is_junction()))
            if len(current.relative_to(root).parts) >= max_depth and dirs:
                result['depth_limited'].append(str(current))
                dirs[:] = []
            for name in sorted(files):
                p = current / name
                if p.is_symlink() or p.resolve() == excluded:
                    continue
                key = str(p.resolve()).casefold() if os.name == 'nt' else str(p.resolve())
                if key in seen:
                    continue
                seen.add(key)
                if result['scanned_files'] >= limit:
                    result['truncated'] = True
                    return result
                result['scanned_files'] += 1
                if p.suffix.lower() not in EXTENSIONS:
                    continue
                try:
                    stat = p.stat()
                except OSError as error:
                    result['unavailable'].append(str(error))
                    continue
                modified = dt.datetime.fromtimestamp(stat.st_mtime).astimezone()
                result['files'].append({'path': str(p), 'bytes': stat.st_size, 'modified': modified.isoformat(), 'recent_hint': modified.date() >= threshold, 'extension': p.suffix.lower()})
    result['files'].sort(key=lambda item: item['modified'], reverse=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', action='append', help='Explicit roots replace configured roots')
    parser.add_argument('--since', default=(dt.date.today() - dt.timedelta(days=14)).isoformat())
    parser.add_argument('--config', type=Path, default=Path(__file__).resolve().parents[1] / 'references/project-sources.json')
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--limit', type=int, default=5000)
    parser.add_argument('--max-depth', type=int, default=6)
    args = parser.parse_args()
    if args.limit < 1 or args.max_depth < 0:
        parser.error('limit must be positive and max-depth nonnegative')
    project = Path(__file__).resolve().parents[4]
    roots = args.root or [r.replace('${PROJECT_ROOT}', str(project)) for r in json.loads(args.config.read_text(encoding='utf-8-sig'))['roots']]
    data = inventory(roots, args.since, args.limit, args.max_depth, args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'indexed': len(data['files']), 'recent_hints': sum(f['recent_hint'] for f in data['files']), 'truncated': data['truncated'], 'unavailable_count': len(data['unavailable']), 'depth_limited_count': len(data['depth_limited'])}))
