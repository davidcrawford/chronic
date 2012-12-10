class Signal:
    def __init__(self, name):
        self.name = name
        self.callbacks = []

    def connect(self, callback):
        self.callbacks.append(callback)

    def disconnect(self, callback):
        for index, cb in enumerate(self.callbacks):
            if callback == cb:
                del self.callbacks[index]
                break

    def emit(self, *args, **kws):
        for callback in self.callbacks[:]:
            callback(*args, **kws)
