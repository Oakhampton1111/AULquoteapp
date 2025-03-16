import React, { useEffect, useState } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { Card, Typography, message, Text } from 'antd';
import styled from 'styled-components';
import { appTheme } from '../../../styles/theme';
import { animations } from '../../../styles/animations';
import { crmApi, Deal, PipelineStats } from '../../../services/api/crm';
import { DealStage } from '../../../services/api/types';

const { Title } = Typography;

const BoardContainer = styled.div`
  display: flex;
  gap: 1rem;
  padding: 1rem;
  overflow-x: auto;
  min-height: 600px;
  background: ${appTheme.token.colorBgLayout};
`;

const StageColumn = styled(Card)`
  min-width: 300px;
  background: ${appTheme.token.colorBgContainer};
  border-radius: ${appTheme.token.borderRadius}px;
  ${animations.fadeIn}
`;

const ItemCard = styled(Card)`
  margin-bottom: 0.5rem;
  cursor: pointer;
  &:hover {
    box-shadow: ${appTheme.token.boxShadow};
  }
  ${animations.fadeIn}
`;

export const KanbanBoard: React.FC = () => {
  const [stages, setStages] = useState<Record<DealStage, Deal[]>>({
    [DealStage.LEAD]: [],
    [DealStage.CONTACT]: [],
    [DealStage.QUOTE_REQUESTED]: [],
    [DealStage.QUOTE_SENT]: [],
    [DealStage.NEGOTIATION]: [],
    [DealStage.CLOSED_WON]: [],
    [DealStage.CLOSED_LOST]: []
  });
  const [stats, setStats] = useState<PipelineStats | null>(null);

  useEffect(() => {
    loadPipelineData();
  }, []);

  const loadPipelineData = async () => {
    try {
      const pipelineStats = await crmApi.getPipelineStats();
      setStats(pipelineStats);
      
      // TODO: Add API endpoint to get all deals and organize by stage
      // For now, using stats to show placeholder cards
      const newStages = { ...stages };
      pipelineStats.stages.forEach(stageStats => {
        newStages[stageStats.stage] = Array(stageStats.count).fill({
          id: 'placeholder',
          title: 'Loading...',
          customer: 'Loading...',
          value: 0
        });
      });
      setStages(newStages);
    } catch (error) {
      message.error('Failed to load pipeline data');
    }
  };

  const handleDragEnd = async (result: any) => {
    if (!result.destination) return;
    
    const sourceStage = result.source.droppableId as DealStage;
    const destStage = result.destination.droppableId as DealStage;
    const dealId = result.draggableId;
    
    try {
      await crmApi.updateDeal(parseInt(dealId), { stage: destStage });
      
      // Update local state
      const newStages = { ...stages };
      const [movedDeal] = newStages[sourceStage].splice(result.source.index, 1);
      newStages[destStage].splice(result.destination.index, 0, movedDeal);
      setStages(newStages);
      
      // Refresh pipeline stats
      await loadPipelineData();
    } catch (error) {
      message.error('Failed to update deal stage');
    }
  };

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <BoardContainer>
        {Object.entries(stages).map(([stage, deals]) => (
          <StageColumn 
            key={stage} 
            title={
              <div>
                <Title level={5}>{stage}</Title>
                {stats && (
                  <Text type="secondary">
                    {stats.stages.find(s => s.stage === stage)?.value.toLocaleString() || 0}
                  </Text>
                )}
              </div>
            }
          >
            <Droppable droppableId={stage}>
              {(provided) => (
                <div
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                >
                  {deals.map((deal, index) => (
                    <Draggable
                      key={deal.id}
                      draggableId={deal.id.toString()}
                      index={index}
                    >
                      {(provided) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                        >
                          <ItemCard size="small">
                            <Title level={5}>{deal.title}</Title>
                            <p>{deal.customer}</p>
                            <p>${deal.value?.toLocaleString() || 0}</p>
                          </ItemCard>
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </StageColumn>
        ))}
      </BoardContainer>
    </DragDropContext>
  );
};
