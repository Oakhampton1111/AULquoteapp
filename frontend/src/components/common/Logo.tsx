import React from 'react';
import styled from 'styled-components';
import auLogistics from '../../assets/images/aulogistics-logo.svg';

const LogoWrapper = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: #fff;
  img {
    max-width: 100%;
    height: auto;
  }
`;

export const Logo: React.FC = () => (
  <LogoWrapper>
    <img src={auLogistics} alt="AU Logistics" />
  </LogoWrapper>
);
