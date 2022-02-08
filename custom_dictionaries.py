from collections import UserDict


class RegisterDict(UserDict):
    def __init__(self, state, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)
        self.state = state

    def __setitem__(self, key: str, value: str):
        value = f"0x{int(value, 16):02x}"
        if key == "M":
            mem_addr = self.state.get_mem_addr_register_pair("H")
            self.state.memory[mem_addr] = value
        super().__setitem__(key, value)

    def __getitem__(self, key: str):
        if key == "M":
            return self.state.get_register_pair_value("H")
        return super().__getitem__(key)

    def update(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError("update expected at most 1 arguments, got %d" % len(args))
        other = dict(*args, **kwargs)
        for key in other:
            self[key] = other[key]


class MemoryDict(UserDict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update(*args, **kwargs)

    def __setitem__(self, key: str, value: str):
        key = f"0x{int(key, 16):04x}"
        value = f"0x{int(value, 16):02x}"
        super().__setitem__(key, value)

    def __getitem__(self, key: str):
        return super().__getitem__(key)

    def update(self, *args, **kwargs):
        if len(args) > 1:
            raise TypeError("update expected at most 1 arguments, got %d" % len(args))
        other = dict(*args, **kwargs)
        for key in other:
            self[key] = other[key]
