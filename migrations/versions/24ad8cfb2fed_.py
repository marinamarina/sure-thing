"""empty message

Revision ID: 24ad8cfb2fed
Revises: 239eed8ebbba
Create Date: 2014-12-20 17:00:07.017902

"""

# revision identifiers, used by Alembic.
revision = '24ad8cfb2fed'
down_revision = '239eed8ebbba'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_performance')
    op.add_column('users', sa.Column('loss_points', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('lsp', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('win_points', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'win_points')
    op.drop_column('users', 'lsp')
    op.drop_column('users', 'loss_points')
    op.create_table('user_performance',
    sa.Column('user_id', sa.INTEGER(), nullable=False),
    sa.Column('win_points', sa.INTEGER(), nullable=True),
    sa.Column('loss_points', sa.INTEGER(), nullable=True),
    sa.Column('lsp', sa.FLOAT(), nullable=True),
    sa.Column('id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], [u'users.id'], ),
    sa.PrimaryKeyConstraint('user_id')
    )
    ### end Alembic commands ###
