import subprocess


def test_arg():
    result = subprocess.check_output(
        'geomet "POINT (0.99999 0.999999)"',
        shell=True)
    expected = '{"coordinates": [0.99999, 0.999999], "type": "Point"}'
    assert result.decode('utf-8').strip() == expected


def test_stdin_implicit():
    result = subprocess.check_output(
        'echo "POINT (0.99999 0.999999)" | geomet',
        shell=True)
    expected = '{"coordinates": [0.99999, 0.999999], "type": "Point"}'
    assert result.decode('utf-8').strip() == expected


def test_stdin_explicit():
    result = subprocess.check_output(
        'echo "POINT (0.99999 0.999999)" | geomet -',
        shell=True)
    expected = '{"coordinates": [0.99999, 0.999999], "type": "Point"}'
    assert result.decode('utf-8').strip() == expected
