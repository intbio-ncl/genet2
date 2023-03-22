import types
from app.enhancer.seeder.datasets.cello import Cello
from app.enhancer.seeder.datasets.igem import IGEM
from app.enhancer.seeder.datasets.vpr import VPR
from app.enhancer.seeder.aligner import Aligner


def _add_dataset(obj, ds):
    e_name = f'enable_{ds.__class__.__name__}'.lower()
    d_name = f'disable_{ds.__class__.__name__}'.lower()

    def produce_add_ds(datasource):
        def produce_add_ds_inner(self):
            self._datasets[datasource] = True
        return produce_add_ds_inner

    def produce_remove_ds(datasource):
        def produce_remove_ds_inner(self):
            self._datasets[datasource] = False
        return produce_remove_ds_inner
    obj.__dict__[e_name] = types.MethodType(produce_add_ds(ds), obj)
    obj.__dict__[d_name] = types.MethodType(produce_remove_ds(ds), obj)


datasets = [IGEM,Cello,VPR]
class Seeder:
    def __init__(self, graph, miner):
        self._alinger = Aligner()
        self._datasets = {s(graph, miner, self._alinger)
                            : False for s in datasets}
        self._threshold = 0.8
        for p in self._datasets:
            _add_dataset(self, p)

    def enable_all(self):
        for d in self._datasets:
            self._datasets[d] = True

    def disable_all(self):
        for d in self._datasets:
            self._datasets[d] = False

    def build(self):
        for ds, enabled in self._datasets.items():
            if enabled:
                ds.build()
        e_seqs = {}
        e_ints = {}
        e_ndna = {}
        for ds, enabled in self._datasets.items():
            if enabled:
                e_seqs, e_ints, e_ndna = ds.integrate(self._threshold,
                                                      existing_seqs=e_seqs,
                                                      existing_ints=e_ints,
                                                      existing_non_dna=e_ndna)