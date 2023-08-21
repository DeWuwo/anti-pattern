class Degree:
    in_degree: int
    out_degree: int

    def __init__(self):
        self.in_degree = -1
        self.out_degree = -1

    def handle_set_degree(self, **kwargs):
        for key, val in kwargs.items():
            method = getattr(self, f'handle_set_{key}', None)
            method(val)

    def handle_set_in_degree(self, in_degree: int):
        self.in_degree = in_degree

    def handle_set_out_degree(self, out_degree: int):
        self.out_degree = out_degree
