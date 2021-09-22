import threading 


class TestableThread(threading.Thread):
    """
    Wrapper around `threading.Thread` that propagates exceptions.

    REF: https://gist.github.com/sbrugman/59b3535ebcd5aa0e2598293cfa58b6ab
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exc = None

    def run(self):
        try:
            super().run()
        except BaseException as e:
            self.exc = e
        finally:
            del self._target, self._args, self._kwargs

    def join(self, timeout=None):
        super().join(timeout)
        if self.exc:
            raise self.exc
