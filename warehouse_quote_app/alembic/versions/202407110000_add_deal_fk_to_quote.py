"""Add deal relationship to quote"""

from alembic import op
import sqlalchemy as sa

revision = "202407110000"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('quote', sa.Column('deal_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_quote_deal_id_deal', 'quote', 'deal', ['deal_id'], ['id'])


def downgrade():
    op.drop_constraint('fk_quote_deal_id_deal', 'quote', type_='foreignkey')
    op.drop_column('quote', 'deal_id')

