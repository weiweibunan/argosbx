#!/usr/bin/env python3
"""Run isolated template/migration tests: python3 tests/test_xray.py /path/to/xray.
No services, firewall, actual HOME, or network are touched.
"""
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

SOURCE = (Path(__file__).resolve().parents[1] / 'argosbx.sh').read_text()
CORE = Path(sys.argv[1]).resolve()


def section(start, end):
    return SOURCE[SOURCE.index(start):SOURCE.index(end, SOURCE.index(start))]


FUNCTIONS = section('xray_download(){', 'upsingbox(){')
FUNCTIONS += section('insuuid(){', 'installsb(){')
FUNCTIONS += section('xrsbhy2(){', 'xrsbout(){')
# Extract the real output template; omit all service management.
FUNCTIONS += section('xrsbout(){', 'if pidof systemd') + 'fi\n}\n'
FUNCTIONS = FUNCTIONS.replace('$HOME', '$TASK_HOME')

with tempfile.TemporaryDirectory(prefix='argosbx-xray-') as tmp:
    root = Path(tmp)
    (root / 'agsbx').mkdir()
    shutil.copy2(CORE, root / 'agsbx/xray')
    functions = root / 'functions.sh'
    functions.write_text(FUNCTIONS)
    subprocess.run(['openssl', 'req', '-x509', '-newkey', 'rsa:2048', '-nodes',
                    '-keyout', str(root / 'key.pem'), '-out', str(root / 'cert.pem'),
                    '-subj', '/CN=localhost', '-days', '1'], check=True, capture_output=True)

    def shell(body, ok=True):
        p = subprocess.run(['bash', '-c', 'source "$1"; TASK_HOME="$2"; ' + body,
                            'test', str(functions), str(root)], text=True, capture_output=True)
        if ok and p.returncode:
            raise AssertionError(p.stdout + p.stderr)
        return p

    setup = '''upxray(){ return 0; }
certificateHTA="$TASK_HOME/cert.pem"; keyHTA="$TASK_HOME/key.pem"
xryx=ForceIPv4v6; wxryx=ForceIPv6v4
pvk="52cuYFgCJXp0LAq7+nWJIbCXXgU9eGggOc+Hlfz5u6A="
wpv6="2606:4700:110:8d8d:1845:c39f:2dd5:a03a"; res="[215,69,233]"
xendip=162.159.192.1; xip='"::/0","0.0.0.0/0"'
x1outtag=direct; x2outtag=direct
'''
    flags = ['xhp', 'vlp', 'vxp', 'vwp', 'xup', 'xcp', 'hyp', 'vmp', 'sop']
    config = root / 'agsbx/xr.json'
    for enabled in [[f] for f in flags] + [flags]:
        shell(setup + ';'.join(f'{f}=yes' for f in enabled) +
              '; installxray; xrsbhy2; xrsbvm; xrsbso; xrsbout')
        d = json.loads(config.read_text())
        assert len(d['inbounds']) == len(enabled)
        assert 'proxySettings' not in config.read_text()
        for o in d['outbounds']:
            assert 'domainStrategy' not in o.get('settings', {})
    print('PASS: 9 individual protocols and combined template, real core -test')

    # Keep routing behavior identical for all direct/WARP combinations and IP families.
    d = json.loads(config.read_text())
    for first, second, ips in itertools.product(['direct', 'warp-out'], repeat=3):
        d['routing']['rules'][0]['outboundTag'] = first
        d['routing']['rules'][1]['outboundTag'] = second
        d['routing']['rules'][0]['ip'] = ['0.0.0.0/0'] if ips == 'direct' else ['::/0']
        config.write_text(json.dumps(d))
        subprocess.run([str(CORE), 'run', '-test', '-c', str(config)], check=True, capture_output=True)
    print('PASS: direct/WARP routing combinations')

    # Reconstruct legacy fields, then verify only the intended fields change.
    legacy = json.loads(json.dumps(d))
    for o in legacy['outbounds']:
        if o['protocol'] == 'freedom':
            sock = o.pop('streamSettings')['sockopt']
            o['settings'] = {'domainStrategy': sock['domainStrategy']}
            if 'dialerProxy' in sock:
                o['proxySettings'] = {'tag': sock['dialerProxy']}
    for i in legacy['inbounds']:
        stream = i.get('streamSettings', {})
        if stream.get('network') == 'raw':
            stream['network'] = 'tcp'
        if 'realitySettings' in stream:
            stream['realitySettings']['fingerprint'] = 'chrome'
            stream['realitySettings']['dest'] = stream['realitySettings'].pop('target')
    config.write_text(json.dumps(legacy))
    shell('xray_migrate_config "$TASK_HOME/agsbx/xr.json" "$TASK_HOME/migrated.json"')
    migrated = json.loads((root / 'migrated.json').read_text())
    for o in migrated['outbounds']:
        if o.get('settings') == {}:
            del o['settings']
    assert migrated == d
    subprocess.run([str(CORE), 'run', '-test', '-c', str(root / 'migrated.json')], check=True, capture_output=True)
    print('PASS: legacy migration preserves protocol credentials, routing and WARP')

    before_core = (root / 'agsbx/xray').read_bytes()
    before_config = config.read_bytes()
    # Downloader failure must return nonzero and preserve both installed files.
    result = shell('cpu=amd64; xray_dependencies(){ return 0; }; xray_download(){ return 1; }; upxray', ok=False)
    assert result.returncode != 0
    assert (root / 'agsbx/xray').read_bytes() == before_core and config.read_bytes() == before_config
    assert not list((root / 'agsbx').glob('.xray-update.*'))
    print('PASS: failed update preserves installed core/config and removes staging files')

    # Reject unexpected release URLs/metadata without touching the installation.
    (root / 'release.json').write_text(json.dumps({
        'tag_name': 'v26.10.31', 'draft': False, 'prerelease': False,
        'assets': [{'name': 'Xray-linux-64.zip', 'browser_download_url': 'https://example.com/xray.zip',
                    'digest': 'sha256:' + '0' * 64}]}))
    result = shell('cpu=amd64; xray_dependencies(){ return 0; }; '
                   'xray_download(){ cp "$TASK_HOME/release.json" "$2"; }; upxray', ok=False)
    assert result.returncode != 0
    assert (root / 'agsbx/xray').read_bytes() == before_core and config.read_bytes() == before_config
    print('PASS: unexpected release URL rejected without replacing installed files')
