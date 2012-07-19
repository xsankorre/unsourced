"""user tweaks

Revision ID: 57b7d7bbc6aa
Revises: 2955ce09cc6e
Create Date: 2012-04-24 15:02:22.413058

"""

# revision identifiers, used by Alembic.
revision = '57b7d7bbc6aa'
down_revision = '2955ce09cc6e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('useraccount', sa.Column('hashed_password', sa.String(length=128), nullable=True))
    op.add_column('useraccount', sa.Column('verified', sa.Boolean(), nullable=False))
    op.drop_column('useraccount', u'anonymous')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('useraccount', sa.Column(u'anonymous', mysql.TINYINT(display_width=1), nullable=False))
    op.drop_column('useraccount', 'verified')
    op.drop_column('useraccount', 'hashed_password')
    ### end Alembic commands ###