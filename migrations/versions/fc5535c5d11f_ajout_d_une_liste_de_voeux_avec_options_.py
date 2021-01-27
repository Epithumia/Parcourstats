"""Ajout d'une liste de voeux avec options/specialites

Revision ID: fc5535c5d11f
Revises: a32a544ffb96
Create Date: 2021-01-27 22:05:36.384957

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc5535c5d11f'
down_revision = 'a32a544ffb96'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('optionbac',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nom', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_optionbac'))
    )
    op.create_table('specialitebac',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nom', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_specialitebac'))
    )
    op.create_table('voeu',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nom', sa.String(), nullable=True),
    sa.Column('prenom', sa.String(), nullable=True),
    sa.Column('etablissement', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_voeu'))
    )
    op.create_table('options_voeux',
    sa.Column('id_voeu', sa.Integer(), nullable=True),
    sa.Column('id_optionbac', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_optionbac'], ['optionbac.id'], name=op.f('fk_options_voeux_id_optionbac_optionbac')),
    sa.ForeignKeyConstraint(['id_voeu'], ['voeu.id'], name=op.f('fk_options_voeux_id_voeu_voeu'))
    )
    op.create_table('specialites_voeux',
    sa.Column('id_voeu', sa.Integer(), nullable=True),
    sa.Column('id_specialitebac', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_specialitebac'], ['specialitebac.id'], name=op.f('fk_specialites_voeux_id_specialitebac_specialitebac')),
    sa.ForeignKeyConstraint(['id_voeu'], ['voeu.id'], name=op.f('fk_specialites_voeux_id_voeu_voeu'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('specialites_voeux')
    op.drop_table('options_voeux')
    op.drop_table('voeu')
    op.drop_table('specialitebac')
    op.drop_table('optionbac')
    # ### end Alembic commands ###