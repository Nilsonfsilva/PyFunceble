"""Initial Version

Revision ID: a32ac5d66eee
Revises:
Create Date: 2022-12-28 07:20:50.310072

"""
import sqlalchemy as sa
from alembic import op

# pylint: skip-file

# revision identifiers, used by Alembic.
revision = "a32ac5d66eee"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "pyfunceble_continue",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.Column("idna_subject", sa.Text(), nullable=False),
        sa.Column("checker_type", sa.String(length=50), nullable=False),
        sa.Column("destination", sa.Text(), nullable=False),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("tested_at", sa.DateTime(), nullable=False),
        sa.Column("session_id", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "pyfunceble_inactive",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.Column("idna_subject", sa.Text(), nullable=False),
        sa.Column("checker_type", sa.String(length=50), nullable=False),
        sa.Column("destination", sa.Text(), nullable=False),
        sa.Column("tested_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "pyfunceble_whois_record",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("modified_at", sa.DateTime(), nullable=True),
        sa.Column("subject", sa.Text(), nullable=False),
        sa.Column("idna_subject", sa.Text(), nullable=True),
        sa.Column("expiration_date", sa.Text(), nullable=False),
        sa.Column("epoch", sa.Integer(), nullable=False),
        sa.Column("registrar", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("subject"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("pyfunceble_whois_record")
    op.drop_table("pyfunceble_inactive")
    op.drop_table("pyfunceble_continue")
    # ### end Alembic commands ###
