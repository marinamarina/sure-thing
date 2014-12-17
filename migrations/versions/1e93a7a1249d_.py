"""empty message

Revision ID: 1e93a7a1249d
Revises: 416d2601dbc
Create Date: 2014-12-17 16:27:27.891530

"""

# revision identifiers, used by Alembic.
revision = '1e93a7a1249d'
down_revision = '416d2601dbc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('teams', 'league_position')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('teams', sa.Column('league_position', sa.INTEGER(), nullable=True))
    ### end Alembic commands ###
