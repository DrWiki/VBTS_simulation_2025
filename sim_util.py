
from pathlib import Path
from time import perf_counter as now


########################################
# Timer                                #
########################################
class Timer():
    """Convenience class for measuring and displaying elapsed time."""

    def __init__(self, margin=4, padding=12):
        self.t0 = None
        self.margin = margin
        self.padding = padding

    def start(self, step):
        """Starts timing a step, displaying its name."""
        print(' '*self.margin + f'{step:{self.padding}}', end='', flush=True)
        self.t0 = now()

    def cancel(self, reason=''):
        """Cancels timing the step, displaying the reason."""
        print(reason, flush=True)

    def stop(self):
        """Stops timing the step, displaying the elapsed time."""
        elapsed = now() - self.t0
        print(f'{elapsed:.1f} seconds', flush=True)

def X_2(x):
    return x*x/200

def degree_K(c):
    return c+273.15