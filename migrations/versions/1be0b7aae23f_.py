"""empty message

Revision ID: 1be0b7aae23f
Revises: 27570cccdafb
Create Date: 2014-12-09 11:11:24.931394

"""

# revision identifiers, used by Alembic.
revision = '1be0b7aae23f'
down_revision = '27570cccdafb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    ### end Alembic commands ###
    pass


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('moduleusersettings', sa.Column('module_id', sa.INTEGER(), nullable=False))
    op.drop_column('moduleusersettings', 'moduleName')
    ### end Alembic commands ###
