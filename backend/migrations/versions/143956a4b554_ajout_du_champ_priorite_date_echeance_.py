"""Ajout du champ priorite, date_echeance, progrssion et reorganisation de statut en ENUM Taches

Revision ID: 143956a4b554
Revises: 0329ac676522
Create Date: 2024-11-16 18:08:27.256553

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '143956a4b554'
down_revision = '0329ac676522'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('taches', schema=None) as batch_op:
        batch_op.add_column(sa.Column('priorite', sa.String(length=20), nullable=False))
        batch_op.add_column(sa.Column('date_echeance', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('progression', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('statut', sa.Enum('A_FAIRE', 'EN_COURS', 'EN_ATTENTE', 'BLOQUEE', 'COMPLETEE', name='statuttache'), nullable=False))
        batch_op.drop_column('status')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('taches', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.VARCHAR(length=50), nullable=False))
        batch_op.drop_column('statut')
        batch_op.drop_column('progression')
        batch_op.drop_column('date_echeance')
        batch_op.drop_column('priorite')

    # ### end Alembic commands ###
