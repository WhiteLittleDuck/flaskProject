from multiprocessing import cpu_count, pool, Manager
import string

__all__ = ['CountingProcessPool', 'CPU_NUM']


CPU_NUM = cpu_count()


_DUMMY = lambda *x: None


class _counter_dec(object):
    def __init__(self, func):
        self.func = func

    def __call__(self, lock, counter, *args, **kwargs):
        with lock:
            counter.value += 1
            print(f'>> Task #{counter.value} finished <<')
        return self.func(*args, **kwargs)


class _cb_counter_dec(object):
    def __init__(self, func, lock, counter):
        self.func = func if func else _DUMMY
        self.lock = lock
        self.counter = counter

    def __call__(self, *args, **kwargs):
        ret = self.func(*args, **kwargs)
        with self.lock:
            self.counter.value += 1
            print(f'>> Task #{self.counter.value} finished <<')
        return ret


class _errcb_counter_dec(object):
    def __init__(self, err_func, args, kwargs, lock, counter):
        self.err_func = err_func if err_func else _DUMMY
        self.args = args
        self.kwargs = kwargs
        self.lock = lock
        self.counter = counter

    def __call__(self, ex):
        err = f'On input position {self.args} keyword {self.kwargs}\n'
        err += repr(ex)
        with self.lock:
            self.counter.value += 1
            print(err)
            print(f'>> Task #{self.counter.value} error <<')
        self.err_func(ex)


class CountingProcessPool(pool.Pool):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._manager = Manager()
        self.lock = self._manager.Lock()
        self.counter = self._manager.Value('i', 0)

    def args_app(self, iterable):
        for args in iterable:
            try:
                assert not isinstance(args, str)
                yield (self.lock, self.counter) + tuple(args)
            except (TypeError, AssertionError):
                yield (self.lock, self.counter) + (args,)

    def _map_async(self, func, iterable, mapper, chunksize=None, callback=None, error_callback=None):
        dec_func = _counter_dec(func)
        app_iter = self.args_app(iterable)
        return super(CountingProcessPool, self)._map_async(dec_func, app_iter, mapper, chunksize, callback, error_callback)

    def apply_async(self, func, args=(), kwds={}, callback=None, error_callback=None):
        dec_cb = _cb_counter_dec(callback, self.lock, self.counter)
        dec_errcb = _errcb_counter_dec(error_callback, args, kwds, self.lock, self.counter)
        return super(CountingProcessPool, self).apply_async(func, args, kwds, dec_cb, dec_errcb)

    def execute(self):
        self.close()
        self.join()



def example(a):
    if a in string.punctuation:
        raise ValueError('no punctuation')
    ret = str(a) * 10
    print(ret)
    return ret

if __name__ == '__main__':
    # Usage: pool creation and execution should be in the main block
    with CountingProcessPool(CPU_NUM) as pool:
        rs = [pool.apply_async(example, (r,)) for r in string.printable]
        pool.execute()
        # [res.get() for res in rs]   # may raise error
