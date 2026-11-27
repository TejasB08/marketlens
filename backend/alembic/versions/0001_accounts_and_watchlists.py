"""Create accounts, watchlist membership, and authentication storage."""

from alembic import op
import sqlalchemy as sa


revision = "0001_accounts_and_watchlists"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("google_sub", sa.Text(), nullable=False),
        sa.Column("email", sa.Text()),
        sa.Column("display_name", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("google_sub", name="uq_users_google_sub"),
    )
    op.create_table(
        "watchlist_items",
        sa.Column("user_id", sa.Uuid(), primary_key=True),
        sa.Column("ticker", sa.Text(), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_watchlist_items_user_id", ondelete="CASCADE"),
        sa.CheckConstraint(
            "ticker <> '' AND ticker = upper(ticker) AND ticker !~ '[[:space:]]'",
            name="ck_watchlist_items_normalized_ticker",
        ),
    )
    op.create_table(
        "auth_sessions",
        sa.Column("token_hash", sa.LargeBinary(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name="fk_auth_sessions_user_id", ondelete="CASCADE"),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
    op.create_index("ix_auth_sessions_expires_at", "auth_sessions", ["expires_at"])
    op.create_table(
        "oauth_login_attempts",
        sa.Column("state_hash", sa.LargeBinary(), primary_key=True),
        sa.Column("browser_binding_hash", sa.LargeBinary(), nullable=False),
        sa.Column("nonce", sa.Text(), nullable=False),
        sa.Column("pkce_verifier", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_oauth_login_attempts_expires_at", "oauth_login_attempts", ["expires_at"])


def downgrade() -> None:
    op.drop_table("oauth_login_attempts")
    op.drop_table("auth_sessions")
    op.drop_table("watchlist_items")
    op.drop_table("users")
