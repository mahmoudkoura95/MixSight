"""Pytest configuration for the MixSight API test suite.

§7.19 part 2 enforcement: any test using an authenticated fixture must carry
`@pytest.mark.tenancy_isolated` and include the cross-tenant case (a second
user from a different org cannot access the resource → 403/404). The marker
is registered in `pyproject.toml`; the hook below catches missing markers at
collection time.

Transactional test fixture per the Week 1 /code-review carry-over: each test
that touches the DB runs inside a SAVEPOINT bound to an outer transaction
which rolls back on fixture exit. SQLAlchemy's `after_transaction_end` event
re-opens a SAVEPOINT after any inner commit so multi-commit tests still see
their writes during the test body but leave no rows behind.

Auth-using fixtures (`authenticated_client_a`, `user_a_in_org_1`, etc.) ship
with Week 3 Day 3 alongside the first authenticated route. They bypass
Clerk JWT verification by overriding the `current_user` dependency with a
fixture-built `User` row; the `get_db` dep is overridden to the SAVEPOINT-
bound session so route writes participate in the test transaction. Two
(user, org) pairs let cross-tenant assertions run trivially per §7.19.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import httpx
import pytest
import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession

# Side-effect import: registers the SQLAlchemy event hooks + runs the
# tenancy audit on app startup. Tests that hit the engine still need this.
import mixsight.main  # noqa: F401
from mixsight.auth.dependencies import current_user
from mixsight.db import engine, get_db
from mixsight.main import app
from mixsight.models import Organization, User

AUTH_FIXTURES: frozenset[str] = frozenset(
    {
        "authenticated_client",
        "authenticated_client_a",
        "authenticated_client_b",
        "user_a_in_org_1",
        "user_b_in_org_2",
        "bearer_token_for",
    }
)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    violations: list[str] = []
    for item in items:
        if not isinstance(item, pytest.Function):
            continue
        if AUTH_FIXTURES.isdisjoint(item.fixturenames):
            continue
        if item.get_closest_marker("tenancy_isolated") is None:
            violations.append(item.nodeid)
    if violations:
        msg = (
            "§7.19 violation: tests using authenticated fixtures must carry "
            "@pytest.mark.tenancy_isolated and include a cross-tenant case:\n  - "
            + "\n  - ".join(violations)
        )
        raise pytest.UsageError(msg)


@pytest_asyncio.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    """Async session that rolls back at the end of every test.

    Pattern: open a connection, begin an outer transaction, bind an
    `AsyncSession` to that connection, open a SAVEPOINT. Inside the test,
    `session.commit()` commits the SAVEPOINT (so reads-after-write work);
    the `after_transaction_end` listener re-opens a fresh SAVEPOINT so
    follow-on writes stay nested. On fixture teardown the outer
    `connection.rollback()` undoes the whole sequence.
    """
    async with engine.connect() as connection:
        await connection.begin()
        async with AsyncSession(bind=connection, expire_on_commit=False) as session:
            await session.begin_nested()

            @event.listens_for(session.sync_session, "after_transaction_end")
            def _restart_savepoint(sess, trans):  # type: ignore[no-untyped-def]
                if trans.nested and not trans._parent.nested:
                    sess.begin_nested()

            yield session
        await connection.rollback()


async def _make_user(db: AsyncSession, *, suffix: str, role: str = "admin") -> User:
    """Build an Organization + linked User row anchored to the SAVEPOINT session."""
    org = Organization(name=f"Test Org {suffix}", clerk_organization_id=f"test_org_{suffix}")
    db.add(org)
    await db.commit()
    await db.refresh(org)
    user = User(
        organization_id=org.id,
        clerk_user_id=f"test_user_{suffix}",
        email=f"{suffix}@example.test",
        role=role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def user_a_in_org_1(db_session: AsyncSession) -> User:
    return await _make_user(db_session, suffix="a", role="admin")


@pytest_asyncio.fixture
async def user_b_in_org_2(db_session: AsyncSession) -> User:
    return await _make_user(db_session, suffix="b", role="admin")


async def _client_for_user(db: AsyncSession, user: User) -> AsyncIterator[httpx.AsyncClient]:
    """Build an httpx ASGI client whose `current_user` resolves to `user` and
    whose `get_db` reuses the SAVEPOINT-bound session so route writes share
    the test transaction (and roll back on teardown).

    The `current_user` override is re-set on every outbound request via an
    httpx event hook. Without this, two parallel `authenticated_client_*`
    fixtures (a + b) would both write to `app.dependency_overrides[current_user]`
    at fixture-setup time and the second would silently win for the entire
    test body — making cross-tenant assertions impossible.
    """

    async def _override_db() -> AsyncIterator[AsyncSession]:
        yield db

    async def _set_current_user_for_request(_request: httpx.Request) -> None:
        async def _override_user() -> User:
            return user

        app.dependency_overrides[current_user] = _override_user

    app.dependency_overrides[get_db] = _override_db
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://test",
            event_hooks={"request": [_set_current_user_for_request]},
        ) as client:
            yield client
    finally:
        app.dependency_overrides.pop(current_user, None)
        app.dependency_overrides.pop(get_db, None)


@pytest_asyncio.fixture
async def authenticated_client_a(
    db_session: AsyncSession, user_a_in_org_1: User
) -> AsyncIterator[httpx.AsyncClient]:
    async for client in _client_for_user(db_session, user_a_in_org_1):
        yield client


@pytest_asyncio.fixture
async def authenticated_client_b(
    db_session: AsyncSession, user_b_in_org_2: User
) -> AsyncIterator[httpx.AsyncClient]:
    async for client in _client_for_user(db_session, user_b_in_org_2):
        yield client
