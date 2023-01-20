import subprocess


def fake_check_output(*_popen_args, _timeout=None, **_kwargs):
    """"Raise an exception asking developer to mock a function.

    Args:
        _popen_args: ...
        _timeout: ...
        _kwargs: ...
    """
    raise RuntimeError('DEV ERROR: Need to mock m.core.subprocess.eval_cmd!!!')


subprocess.check_output = fake_check_output
