"""empty message

Revision ID: cb8c900ce13
Revises: 5105a88a56fe
Create Date: 2015-03-27 15:08:39.492282

"""

# revision identifiers, used by Alembic.
revision = 'cb8c900ce13'
down_revision = '5105a88a56fe'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
   pass
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('savedforlater', sa.Column('weight_user_hunch', sa.FLOAT(), nullable=True))
    op.add_column('prediction_modules', sa.Column('default_weight', sa.FLOAT(), nullable=True))
    op.add_column('messages', sa.Column('author_id', sa.INTEGER(), nullable=True))
    op.drop_constraint(None, 'messages', type_='foreignkey')
    op.create_foreign_key(None, 'messages', 'users', ['author_id'], ['id'])
    op.add_column('matches', sa.Column('played', sa.BOOLEAN(), nullable=True))
    op.add_column('matches', sa.Column('match_ft_score', sa.VARCHAR(length=8), nullable=True))
    op.add_column('matches', sa.Column('actual_winner', sa.INTEGER(), nullable=True))
    op.create_foreign_key(None, 'matches', 'teams', ['actual_winner'], ['id'])
    ### end Alembic commands ###
