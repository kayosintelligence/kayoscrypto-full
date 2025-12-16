import json
import subprocess

def make_chain(tmp_path, n=3):
    # Create a simple ledger without integrity fields -> verifier runs in informational mode
    chain = []
    for i in range(n):
        rec = {'seq': i, 'data': 'x', 'actor': f'actor{i}', 'action': 'test.event'}
        chain.append(rec)
    p = tmp_path / 'chain.json'
    p.write_text(json.dumps({'history': chain}))
    return str(p)


def test_verify_chain(tmp_path):
    p = make_chain(tmp_path)
    r = subprocess.run(['python3', 'scripts/verify_mpcn_ledger.py', p], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
