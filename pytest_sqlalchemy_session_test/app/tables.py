import sqlalchemy as sa

metadata = sa.MetaData()

sample_table = sa.Table(
    "sample_table",
    metadata,
    sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
)
