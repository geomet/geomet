import subprocess

def test_arg():
    result = subprocess.check_output(
        'geomet "POINT (0.99999 0.999999)"',
        shell=True)
    assert result.decode('utf-8').strip() == '{"type": "Point", "coordinates": [0.99999, 0.999999]}'

def test_stdin_implicit():
    result = subprocess.check_output(
        'echo "POINT (0.99999 0.999999)" | geomet',
        shell=True)
    assert result.decode('utf-8').strip() == '{"type": "Point", "coordinates": [0.99999, 0.999999]}'

def test_stdin_explicit():
    result = subprocess.check_output(
        'echo "POINT (0.99999 0.999999)" | geomet -',
        shell=True)
    assert result.decode('utf-8').strip() == '{"type": "Point", "coordinates": [0.99999, 0.999999]}'
