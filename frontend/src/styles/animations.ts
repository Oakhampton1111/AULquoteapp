import { keyframes } from 'styled-components';

// Fade animations
export const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`;

export const fadeOut = keyframes`
  from { opacity: 1; }
  to { opacity: 0; }
`;

// Slide animations
export const slideInFromRight = keyframes`
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
`;

export const slideInFromLeft = keyframes`
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
`;

// Page transition animations
export const pageTransitionEnter = keyframes`
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

export const pageTransitionExit = keyframes`
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-10px);
  }
`;

// Loading animations
export const spin = keyframes`
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
`;

export const pulse = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
`;

// Helper function to create animation CSS
export const createAnimation = (
  animation: ReturnType<typeof keyframes>,
  duration = '0.3s',
  timingFunction = 'ease',
  delay = '0s',
  iterationCount = '1',
  fillMode = 'forwards'
) => `
  animation: ${animation} ${duration} ${timingFunction} ${delay} ${iterationCount} ${fillMode};
`;

// Common animation presets
export const animations = {
  fadeIn: createAnimation(fadeIn),
  fadeOut: createAnimation(fadeOut),
  slideInRight: createAnimation(slideInFromRight),
  slideInLeft: createAnimation(slideInFromLeft),
  pageEnter: createAnimation(pageTransitionEnter),
  pageExit: createAnimation(pageTransitionExit),
  spin: createAnimation(spin, '1s', 'linear', '0s', 'infinite'),
  pulse: createAnimation(pulse, '1.5s', 'ease-in-out', '0s', 'infinite'),
};
