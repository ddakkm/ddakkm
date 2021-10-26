"""ADD agree flag to user model

Revision ID: 433d1f53c5e3
Revises: d85679684fc5
Create Date: 2021-10-19 00:03:59.489347

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '433d1f53c5e3'
down_revision = 'd85679684fc5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('agree_over_fourteen', sa.Boolean(), nullable=True))
    op.add_column('user', sa.Column('agree_privacy_policy', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'agree_privacy_policy')
    op.drop_column('user', 'agree_over_fourteen')
    # ### end Alembic commands ###