from collections.abc import Mapping


class CorsHeaders(Mapping):
    def __init__(self):
        self.headers = {}

    def __getitem__(self, key):
        return self.headers[key]

    def __iter__(self):
        return iter(self.headers)

    def __len__(self):
        return len(self.headers)

    def __setitem__(self, key, value):
        # Implement any custom logic if needed
        self.headers[key] = value

    def __delitem__(self, key):
        del self.headers[key]


cors_headers = CorsHeaders()
cors_headers["Access-Control-Allow-Origin"] = "*"
cors_headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
cors_headers["Access-Control-Allow-Headers"] = "Content-Type"
cors_headers["Access-Control-Max-Age"] = "3600"
