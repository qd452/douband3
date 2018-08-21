"""empty message

Revision ID: 94696a473aed
Revises: 79281d95305d
Create Date: 2018-08-19 16:03:39.047585

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '94696a473aed'
down_revision = '79281d95305d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_collection', sa.Column('rating_my', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_collection', 'rating_my')
    # ### end Alembic commands ###
