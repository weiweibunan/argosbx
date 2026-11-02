#!/usr/bin/env python3
"""Offline geodata regression: test_geodata.py XRAY GEOIP_DAT GEOSITE_DAT."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

source = (Path(__file__).resolve().parents[1] / 'argosbx.sh').read_text()
functions = source[source.index('xray_download(){'):source.index('upsingbox(){')].replace('$HOME', '$TASK_HOME')
with tempfile.TemporaryDirectory() as temp:
    root = Path(temp)
    (root / 'agsbx').mkdir()
    (root / 'fixtures').mkdir()
    core, ip, site = map(lambda p: Path(p).resolve(), sys.argv[1:])
    shutil.copy2(core, root / 'agsbx/xray')
    assets = []
    for name, original in [('geoip-full.dat', ip), ('geosite-expand.dat', site)]:
        shutil.copy2(original, root / 'fixtures' / name)
        assets.append({'name': name, 'browser_download_url': f'https://github.com/XTLS/Xray-rules-dat/releases/download/20261101/{name}',
                       'digest': 'sha256:' + hashlib.sha256(original.read_bytes()).hexdigest()})
    (root / 'fixtures/latest').write_text(json.dumps({'tag_name':'20261101', 'draft':False, 'prerelease':False, 'assets':assets}))
    (root / 'functions.sh').write_text(functions)
    config = root / 'agsbx/xr.json'
    config.write_text(json.dumps({'outbounds':[{'protocol':'freedom','tag':'direct'}], 'routing':{'rules':[
        {'type':'field','domain':['geosite:cn'],'outboundTag':'direct'},
        {'type':'field','ip':['geoip:cn'],'outboundTag':'direct'}]}}))
    original_config = config.read_bytes()

    def shell(body):
        return subprocess.run(['bash','-c','source "$1/functions.sh"; TASK_HOME="$1"; '
            'xray_download(){ cp "$TASK_HOME/fixtures/${1##*/}" "$2"; }; ' + body,
            'test',str(root)], capture_output=True, text=True)

    result = shell('upgeodata')
    assert result.returncode == 0, result.stdout + result.stderr
    assert config.read_bytes() == original_config
    # Verify normal loading from executable directory without an env override.
    subprocess.run([str(root/'agsbx/xray'),'run','-test','-c',str(config)], check=True,capture_output=True)
    print('PASS: both official data formats load; upgeo preserves xr.json byte-for-byte')
    old_ip = (root/'agsbx/geoip.dat').read_bytes()
    old_site = (root/'agsbx/geosite.dat').read_bytes()
    (root/'fixtures/geosite-expand.dat').write_bytes(b'bad download')
    result = shell('upgeodata')
    assert result.returncode != 0
    assert (root/'agsbx/geoip.dat').read_bytes() == old_ip
    assert (root/'agsbx/geosite.dat').read_bytes() == old_site
    assert config.read_bytes() == original_config
    print('PASS: checksum failure preserves both databases and configuration')
    stage = root/'stage'; stage.mkdir()
    (stage/'geoip.dat').write_bytes(b'new ip')
    (stage/'geosite.dat').write_bytes(b'new site')
    result = shell('mv(){ case "$2" in */geosite.dat) return 1;; esac; command mv "$@"; }; '
                   'xray_commit_files "$TASK_HOME/stage" geoip.dat geosite.dat')
    assert result.returncode != 0
    assert (root/'agsbx/geoip.dat').read_bytes() == old_ip
    assert (root/'agsbx/geosite.dat').read_bytes() == old_site
    print('PASS: second-file replacement failure restores both original databases')
