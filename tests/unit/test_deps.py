from app.api.v1.deps import get_db


def test_get_db_yields_and_closes():
    gen = get_db()
    db = next(gen)
    assert db is not None
    # simulate request end
    try:
        next(gen)
        assert False, "Generator should have stopped"
    except StopIteration:
        pass
