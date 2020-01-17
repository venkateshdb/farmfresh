"""empty message

Revision ID: ea2e4c48287b
Revises: 
Create Date: 2020-01-17 18:39:21.727187

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea2e4c48287b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('verify',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('phone_num', sa.String(), nullable=False),
    sa.Column('otp', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('verify')
    # ### end Alembic commands ###