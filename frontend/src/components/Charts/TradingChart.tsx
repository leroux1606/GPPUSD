import React, { useEffect, useRef, useCallback, useState } from 'react';
import { createChart, IChartApi, ISeriesApi, CandlestickData, Time } from 'lightweight-charts';
import { useDataStore } from '../../store/dataStore';
import { useUIStore } from '../../store/uiStore';
import { useHistoricalData } from '../../hooks/useLiveData';
import { LoadingSpinner } from '../Common/LoadingSpinner';

interface TradingChartProps {
  height?: number;
  showCrosshair?: boolean;
}

export function TradingChart({ height = 500, showCrosshair = true }: TradingChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<'Histogram'> | null>(null);
  
  const { selectedTimeframe } = useUIStore();
  const { historicalData, livePrice } = useDataStore();
  const { data, isLoading, error, fetchData } = useHistoricalData(selectedTimeframe);
  
  const [chartReady, setChartReady] = useState(false);

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: height,
      layout: {
        background: { type: 'solid', color: '#1e1e1e' },
        textColor: '#d1d5db',
      },
      grid: {
        vertLines: { color: '#2b2b43' },
        horzLines: { color: '#2b2b43' },
      },
      crosshair: {
        mode: showCrosshair ? 1 : 0,
        vertLine: {
          color: '#6b7280',
          width: 1,
          style: 2,
          labelBackgroundColor: '#2b2b43',
        },
        horzLine: {
          color: '#6b7280',
          width: 1,
          style: 2,
          labelBackgroundColor: '#2b2b43',
        },
      },
      rightPriceScale: {
        borderColor: '#3b3b4d',
        scaleMargins: {
          top: 0.1,
          bottom: 0.2,
        },
      },
      timeScale: {
        borderColor: '#3b3b4d',
        timeVisible: true,
        secondsVisible: false,
      },
    });

    // Add candlestick series
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });

    // Add volume series
    const volumeSeries = chart.addHistogramSeries({
      color: '#26a69a',
      priceFormat: {
        type: 'volume',
      },
      priceScaleId: '',
    });

    volumeSeries.priceScale().applyOptions({
      scaleMargins: {
        top: 0.85,
        bottom: 0,
      },
    });

    chartRef.current = chart;
    candlestickSeriesRef.current = candlestickSeries;
    volumeSeriesRef.current = volumeSeries;
    setChartReady(true);

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener('resize', handleResize);
    const resizeObserver = new ResizeObserver(handleResize);
    resizeObserver.observe(chartContainerRef.current);

    return () => {
      window.removeEventListener('resize', handleResize);
      resizeObserver.disconnect();
      chart.remove();
      chartRef.current = null;
      candlestickSeriesRef.current = null;
      volumeSeriesRef.current = null;
      setChartReady(false);
    };
  }, [height, showCrosshair]);

  // Update chart data when historical data changes
  useEffect(() => {
    if (!chartReady || !candlestickSeriesRef.current || !volumeSeriesRef.current) return;
    if (!data || data.length === 0) return;

    try {
      const candleData: CandlestickData[] = data.map((candle) => ({
        time: (new Date(candle.timestamp).getTime() / 1000) as Time,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
      }));

      const volumeData = data.map((candle) => ({
        time: (new Date(candle.timestamp).getTime() / 1000) as Time,
        value: candle.volume,
        color: candle.close >= candle.open ? '#26a69a80' : '#ef535080',
      }));

      candlestickSeriesRef.current.setData(candleData);
      volumeSeriesRef.current.setData(volumeData);

      // Fit content
      chartRef.current?.timeScale().fitContent();
    } catch (err) {
      console.error('Error updating chart data:', err);
    }
  }, [data, chartReady]);

  // Update last candle with live price
  useEffect(() => {
    if (!chartReady || !candlestickSeriesRef.current || !livePrice) return;
    if (!data || data.length === 0) return;

    try {
      const lastCandle = data[data.length - 1];
      const lastTime = (new Date(lastCandle.timestamp).getTime() / 1000) as Time;

      // Update the last candle's close with live price
      candlestickSeriesRef.current.update({
        time: lastTime,
        open: lastCandle.open,
        high: Math.max(lastCandle.high, livePrice.mid),
        low: Math.min(lastCandle.low, livePrice.mid),
        close: livePrice.mid,
      });
    } catch (err) {
      // Ignore update errors
    }
  }, [livePrice, data, chartReady]);

  // Fetch data when timeframe changes
  useEffect(() => {
    fetchData(selectedTimeframe);
  }, [selectedTimeframe, fetchData]);

  if (isLoading && data.length === 0) {
    return (
      <div className="chart-loading" style={{ height }}>
        <LoadingSpinner message="Loading chart data..." />
      </div>
    );
  }

  if (error && data.length === 0) {
    return (
      <div className="chart-error" style={{ height }}>
        <p>Error loading chart: {error}</p>
        <button onClick={() => fetchData(selectedTimeframe)}>Retry</button>
      </div>
    );
  }

  return (
    <div className="trading-chart-container">
      <div ref={chartContainerRef} style={{ width: '100%', height }} />
      {data.length === 0 && !isLoading && (
        <div className="chart-no-data">
          <p>No data available for this timeframe</p>
          <button onClick={() => fetchData(selectedTimeframe)}>Load Data</button>
        </div>
      )}
    </div>
  );
}
