"""suppression de clé primaire id de MembreTache pour clé primaire composite(membre_id, tache_id) 

Revision ID: d9c8ec2a661c
Revises: f253a6bc7420
Create Date: 2024-11-23 04:47:24.307750

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9c8ec2a661c'
down_revision = 'f253a6bc7420'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('membre_taches', schema=None) as batch_op:
        batch_op.drop_column('id')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('membre_taches', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id', sa.INTEGER(), nullable=False))

    # ### end Alembic commands ###
