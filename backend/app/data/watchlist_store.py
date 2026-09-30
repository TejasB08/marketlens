DEFAULT_USER = "local_user"  # placeholder until auth exists


class WatchlistStore:
    """
    In-memory watchlist, keyed by user_id.
    Today everything uses DEFAULT_USER since there's no auth yet —
    but keying by user_id now means swapping in real users later is
    a one-line change in how user_id gets resolved, not a rewrite
    of this class's shape.
    """

    def __init__(self):
        self.watchlists = {}  # user_id -> set of tickers

    def add(self, ticker: str, user_id: str = DEFAULT_USER):
        self.watchlists.setdefault(user_id, set()).add(ticker)

    def remove(self, ticker: str, user_id: str = DEFAULT_USER):
        self.watchlists.get(user_id, set()).discard(ticker)

    def get_all(self, user_id: str = DEFAULT_USER) -> list:
        return sorted(self.watchlists.get(user_id, set()))


watchlist_store = WatchlistStore()