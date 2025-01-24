class Disposable:
    def release(self):
        pass
    def __del__(self):
        self.release()
