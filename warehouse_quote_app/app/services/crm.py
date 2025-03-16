"""CRM service layer."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import and_, or_, func, case
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from app.models.customer import Customer
from app.models.crm import CustomerInteraction, Deal, InteractionType, DealStage
from app.services.base import BaseService
from app.core.security import get_current_user
from app.schemas.crm import (
    InteractionCreate,
    InteractionUpdate,
    DealCreate,
    DealUpdate,
    PipelineStats,
    CustomerCRMStats,
    CustomerWithCRMStats
)

class CRMService(BaseService):
    """Service for managing CRM operations."""

    def __init__(self, db: Session):
        """Initialize CRM service."""
        self.db = db

    async def create_interaction(
        self,
        customer_id: int,
        interaction: InteractionCreate,
        agent_id: int
    ) -> CustomerInteraction:
        """Create a new customer interaction."""
        customer = await self.db.get(Customer, customer_id)
        if not customer:
            raise ValueError("Customer not found")

        db_interaction = await customer.add_interaction(
            type=interaction.type,
            description=interaction.description,
            agent_id=agent_id,
            metadata=interaction.metadata
        )
        await self.db.flush()
        return db_interaction

    async def create_deal(
        self,
        customer_id: int,
        deal: DealCreate,
        agent_id: int
    ) -> Deal:
        """Create a new deal."""
        customer = await self.db.get(Customer, customer_id)
        if not customer:
            raise ValueError("Customer not found")

        db_deal = await customer.create_deal(
            title=deal.title,
            description=deal.description,
            value=deal.value,
            probability=deal.probability,
            expected_close_date=deal.expected_close_date,
            metadata=deal.metadata
        )
        db_deal.created_by = agent_id
        await self.db.flush()
        return db_deal

    async def update_deal_stage(
        self,
        deal_id: int,
        stage: DealStage,
        agent_id: int,
        metadata: Optional[Dict] = None
    ) -> Deal:
        """Update a deal's stage."""
        deal = await self.db.get(Deal, deal_id)
        if not deal:
            raise ValueError("Deal not found")

        old_stage = deal.stage
        deal.stage = stage
        
        # Update timestamps and metadata based on stage
        if stage == DealStage.CLOSED_WON:
            deal.actual_close_date = datetime.utcnow()
            deal.completed_by = agent_id
        elif stage == DealStage.CLOSED_LOST:
            deal.actual_close_date = datetime.utcnow()
            deal.rejected_by = agent_id

        if metadata:
            deal.metadata.update(metadata)

        # Update customer metrics
        await deal.customer.update_metrics()
        await self.db.flush()
        return deal

    async def get_pipeline_stats(self) -> PipelineStats:
        """Get statistics for the deal pipeline."""
        result = await self.db.execute(
            select(
                Deal.stage,
                func.count(Deal.id).label('count'),
                func.sum(Deal.value).label('value')
            )
            .group_by(Deal.stage)
        )
        stats = result.all()

        return PipelineStats(
            stages=[{
                'stage': stage,
                'count': count,
                'value': value or 0
            } for stage, count, value in stats],
            total_deals=sum(s[1] for s in stats),
            total_value=sum(s[2] or 0 for s in stats),
            win_rate=self._calculate_win_rate(stats)
        )

    async def get_customer_crm_stats(self, customer_id: int) -> CustomerCRMStats:
        """Get CRM statistics for a specific customer."""
        customer = await self.db.get(Customer, customer_id)
        if not customer:
            raise ValueError("Customer not found")

        active_deals = customer.get_active_deals()
        won_deals = customer.get_won_deals()

        return CustomerCRMStats(
            total_interactions=len(customer.interactions),
            last_interaction=max(
                (i.created_at for i in customer.interactions),
                default=None
            ) if customer.interactions else None,
            active_deals=len(active_deals),
            total_deal_value=sum(d.value or 0 for d in customer.deals),
            active_deal_value=sum(d.value or 0 for d in active_deals),
            won_deal_value=sum(d.value or 0 for d in won_deals),
            success_rate=customer.calculate_success_rate()
        )

    async def get_recent_interactions(
        self,
        customer_id: Optional[int] = None,
        days: int = 30,
        interaction_type: Optional[InteractionType] = None
    ) -> List[CustomerInteraction]:
        """Get recent interactions, optionally filtered by customer and type."""
        query = select(CustomerInteraction).where(
            CustomerInteraction.created_at >= func.now() - func.interval(f'{days} days')
        )

        if customer_id:
            query = query.where(CustomerInteraction.customer_id == customer_id)
        if interaction_type:
            query = query.where(CustomerInteraction.type == interaction_type)

        query = query.order_by(CustomerInteraction.created_at.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    def _calculate_win_rate(self, stats: List[tuple]) -> float:
        """Calculate the win rate from pipeline stats."""
        closed_deals = sum(
            count for stage, count, _ in stats
            if stage in (DealStage.CLOSED_WON, DealStage.CLOSED_LOST)
        )
        if not closed_deals:
            return 0.0

        won_deals = next(
            (count for stage, count, _ in stats if stage == DealStage.CLOSED_WON),
            0
        )
        return (won_deals / closed_deals) * 100

    def get_customers_with_crm_stats(self, skip: int = 0, limit: int = 100) -> List[CustomerWithCRMStats]:
        """
        Get all customers with their CRM statistics.
        """
        # Get base customer query
        customers = self.db.query(Customer).offset(skip).limit(limit).all()
        
        customer_stats = {}
        customer_ids = [c.id for c in customers]
        
        if not customer_ids:
            return []

        # Get deal statistics for all customers
        deal_stats = (
            self.db.query(
                Deal.customer_id,
                func.sum(Deal.value).label('total_value'),
                func.sum(
                    case([(Deal.stage.in_([DealStage.CLOSED_WON]), Deal.value)], else_=0)
                ).label('won_value'),
                func.count(Deal.id).label('total_deals'),
                func.sum(
                    case([(Deal.stage.notin_([DealStage.CLOSED_WON, DealStage.CLOSED_LOST]), 1)], else_=0)
                ).label('active_deals'),
                func.sum(
                    case([(Deal.stage == DealStage.CLOSED_WON, 1)], else_=0)
                ).label('won_deals'),
            )
            .filter(Deal.customer_id.in_(customer_ids))
            .group_by(Deal.customer_id)
            .all()
        )
        
        # Get last interaction for all customers
        last_interactions = (
            self.db.query(
                CustomerInteraction.customer_id,
                func.max(CustomerInteraction.created_at).label('last_interaction')
            )
            .filter(CustomerInteraction.customer_id.in_(customer_ids))
            .group_by(CustomerInteraction.customer_id)
            .all()
        )
        
        # Process deal statistics
        for stats in deal_stats:
            customer_stats[stats.customer_id] = {
                'total_deal_value': float(stats.total_value or 0),
                'won_deal_value': float(stats.won_value or 0),
                'total_deals': stats.total_deals,
                'active_deals': stats.active_deals,
                'success_rate': (stats.won_deals / stats.total_deals * 100) if stats.total_deals > 0 else 0
            }
        
        # Process last interactions
        for interaction in last_interactions:
            if interaction.customer_id in customer_stats:
                customer_stats[interaction.customer_id]['last_interaction'] = interaction.last_interaction
            else:
                customer_stats[interaction.customer_id] = {
                    'last_interaction': interaction.last_interaction,
                    'total_deal_value': 0,
                    'won_deal_value': 0,
                    'total_deals': 0,
                    'active_deals': 0,
                    'success_rate': 0
                }
        
        # Combine customer data with stats
        result = []
        for customer in customers:
            stats = customer_stats.get(customer.id, {
                'total_deal_value': 0,
                'won_deal_value': 0,
                'total_deals': 0,
                'active_deals': 0,
                'success_rate': 0,
                'last_interaction': None
            })
            
            result.append(CustomerWithCRMStats(
                id=customer.id,
                name=customer.name,
                company=customer.company,
                email=customer.email,
                phone=customer.phone,
                total_deal_value=stats['total_deal_value'],
                won_deal_value=stats['won_deal_value'],
                active_deals=stats['active_deals'],
                success_rate=stats['success_rate'],
                last_interaction=stats['last_interaction']
            ))
        
        return result
