/**
 * Utility functions for performance monitoring
 */

/**
 * Measures the time it takes to execute a function
 * @param name The name of the measurement
 * @param fn The function to measure
 * @returns The result of the function
 */
export const measurePerformance = async <T>(name: string, fn: () => Promise<T>): Promise<T> => {
  // Start performance measurement
  performance.mark(`${name}-start`);
  
  try {
    // Execute the function
    const result = await fn();
    
    // End performance measurement
    performance.mark(`${name}-end`);
    performance.measure(name, `${name}-start`, `${name}-end`);
    
    // Log performance in development
    if (process.env.NODE_ENV !== 'production') {
      const measure = performance.getEntriesByName(name)[0];
      console.log(`Performance: ${name} took ${measure.duration.toFixed(2)}ms`);
    }
    
    return result;
  } catch (error) {
    // End performance measurement even if there's an error
    performance.mark(`${name}-end`);
    performance.measure(`${name}-error`, `${name}-start`, `${name}-end`);
    
    // Log error performance in development
    if (process.env.NODE_ENV !== 'production') {
      const measure = performance.getEntriesByName(`${name}-error`)[0];
      console.error(`Performance Error: ${name} failed after ${measure.duration.toFixed(2)}ms`);
    }
    
    throw error;
  }
};

/**
 * Measures the time it takes to render a component
 * @param componentName The name of the component
 * @returns An object with start and end functions
 */
export const measureComponentRender = (componentName: string) => {
  const markName = `render-${componentName}`;
  
  return {
    start: () => {
      performance.mark(`${markName}-start`);
    },
    end: () => {
      performance.mark(`${markName}-end`);
      performance.measure(markName, `${markName}-start`, `${markName}-end`);
      
      // Log performance in development
      if (process.env.NODE_ENV !== 'production') {
        const measure = performance.getEntriesByName(markName)[0];
        console.log(`Component Render: ${componentName} took ${measure.duration.toFixed(2)}ms`);
      }
    },
  };
};

/**
 * Creates a performance observer to monitor specific performance metrics
 * @param entryTypes The types of performance entries to observe
 * @param callback The callback function to execute when entries are observed
 * @returns The performance observer
 */
export const createPerformanceObserver = (
  entryTypes: string[],
  callback: (entries: PerformanceObserverEntryList) => void
): PerformanceObserver | undefined => {
  if (typeof PerformanceObserver === 'undefined') {
    return undefined;
  }
  
  const observer = new PerformanceObserver(callback);
  observer.observe({ entryTypes });
  
  return observer;
};

/**
 * Monitors web vitals metrics
 */
export const monitorWebVitals = (): void => {
  if (typeof PerformanceObserver === 'undefined') {
    return;
  }
  
  // Monitor LCP (Largest Contentful Paint)
  createPerformanceObserver(['largest-contentful-paint'], (entries) => {
    const lastEntry = entries.getEntries().pop();
    if (lastEntry) {
      const lcp = lastEntry.startTime;
      console.log(`LCP: ${lcp.toFixed(2)}ms`);
      
      // Send to analytics in production
      if (process.env.NODE_ENV === 'production') {
        // Example: sendToAnalytics({ name: 'LCP', value: lcp });
      }
    }
  });
  
  // Monitor FID (First Input Delay)
  createPerformanceObserver(['first-input'], (entries) => {
    const firstInput = entries.getEntries()[0];
    if (firstInput) {
      const fid = firstInput.processingStart - firstInput.startTime;
      console.log(`FID: ${fid.toFixed(2)}ms`);
      
      // Send to analytics in production
      if (process.env.NODE_ENV === 'production') {
        // Example: sendToAnalytics({ name: 'FID', value: fid });
      }
    }
  });
  
  // Monitor CLS (Cumulative Layout Shift)
  let clsValue = 0;
  let clsEntries: PerformanceEntry[] = [];
  
  createPerformanceObserver(['layout-shift'], (entries) => {
    for (const entry of entries.getEntries()) {
      // Only count layout shifts without recent user input
      if (!(entry as any).hadRecentInput) {
        clsValue += (entry as any).value;
        clsEntries.push(entry);
      }
    }
    
    console.log(`Current CLS: ${clsValue.toFixed(3)}`);
    
    // Send to analytics in production
    if (process.env.NODE_ENV === 'production') {
      // Example: sendToAnalytics({ name: 'CLS', value: clsValue });
    }
  });
};
