"""EDIT agree flag

Revision ID: 19b79563dccf
Revises: 433d1f53c5e3
Create Date: 2021-10-19 00:05:15.812985

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '19b79563dccf'
down_revision = '433d1f53c5e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'agree_over_fourteen',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False)
    op.alter_column('user', 'agree_privacy_policy',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('user', 'agree_privacy_policy',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True)
    op.alter_column('user', 'agree_over_fourteen',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True)
    # ### end Alembic commands ###