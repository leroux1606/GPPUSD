import React, { useEffect, useRef, useState } from 'react';
import { createChart, IChartApi, ISeriesApi, CandlestickData, Time, ColorType } from 'lightweight-charts';
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
  const indicatorSeriesRef = useRef<Map<string, ISeriesApi<'Line'>>>(new Map());

  const { selectedTimeframe } = useUIStore();
  const { historicalData, livePrice, indicators } = useDataStore();
  const { data, isLoading, error, fetchData } = useHistoricalData(selectedTimeframe);

  const [chartReady, setChartReady] = useState(false);

  // Initialize chart
  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      width: chartContainerRef.current.clientWidth,
      height: height,
      layout: {
        background: { type: ColorType.Solid, color: '#1e1e1e' },
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

    // Small delay ensures the chart DOM is fully laid out before setting data
    const timer = setTimeout(() => {
      try {
        if (!candlestickSeriesRef.current || !volumeSeriesRef.current) return;

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
    }, 50);

    return () => clearTimeout(timer);
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

  // Render indicator lines on the chart
  useEffect(() => {
    if (!chartReady || !chartRef.current || !data || data.length === 0) return;

    const chart = chartRef.current;
    const existingSeries = indicatorSeriesRef.current;

    // Remove series for indicators that were deleted
    for (const [key, series] of existingSeries) {
      const indicatorName = key.split('__')[0];
      if (!indicators[indicatorName]) {
        chart.removeSeries(series);
        existingSeries.delete(key);
      }
    }

    // Separate scale colours for non-overlay indicators
    const MULTI_COLORS: { [key: string]: string[] } = {
      macd:        ['#2196f3', '#ff9800', '#ef5350'],
      stochastic:  ['#9c27b0', '#e91e63'],
      bollinger_bands: ['#e91e6980', '#e91e63', '#e91e6980'],
      aroon:       ['#4caf50', '#f44336'],
      dmi:         ['#4caf50', '#f44336'],
      keltner_channels: ['#00bcd480', '#00bcd4', '#00bcd480'],
      donchian_channels: ['#ff572280', '#ff5722', '#ff572280'],
      ichimoku:    ['#26a69a', '#ef5350', '#26a69a80', '#ef535080', '#9ca3af'],
    };

    const timestamps = data.map((c) => (new Date(c.timestamp).getTime() / 1000) as Time);

    // Check if any separate indicators are active
    const hasSeparate = Object.values(indicators).some((ind) => ind.type === 'separate');

    // Reserve bottom 25% for separate indicators; restore when none active
    chart.applyOptions({
      rightPriceScale: {
        scaleMargins: { top: 0.05, bottom: hasSeparate ? 0.28 : 0.12 },
      },
    });

    const makeLine = (key: string, color: string, scaleId: string) => {
      if (existingSeries.has(key)) return existingSeries.get(key)!;
      const s = chart.addLineSeries({
        color,
        lineWidth: 2,
        priceLineVisible: false,
        lastValueVisible: true,
        crosshairMarkerVisible: false,
        priceScaleId: scaleId,
      });
      if (scaleId === 'separate') {
        // Use bottom 22% with a small gap at bottom for the border
        s.priceScale().applyOptions({ scaleMargins: { top: 0.78, bottom: 0.02 } });
      }
      existingSeries.set(key, s);
      return s;
    };

    for (const [name, indicator] of Object.entries(indicators)) {
      const scaleId = indicator.type === 'overlay' ? 'right' : 'separate';
      const baseColor = indicator.color || '#2196f3';

      if (Array.isArray(indicator.values)) {
        // Single series (SMA, EMA, RSI, ATR, etc.)
        const s = makeLine(name, baseColor, scaleId);
        const pts = timestamps
          .map((t, i) => ({ time: t, value: (indicator.values as (number | null)[])[i] }))
          .filter((p) => p.value != null) as { time: Time; value: number }[];
        s.setData(pts);
      } else if (typeof indicator.values === 'object') {
        // Multi-series DataFrame (MACD, Bollinger Bands, Stochastic, etc.)
        const cols = Object.keys(indicator.values);
        const palette = MULTI_COLORS[name] || cols.map((_, i) => `hsl(${(i * 60 + 200) % 360},70%,55%)`);
        cols.forEach((col, i) => {
          const key = `${name}__${col}`;
          const color = palette[i] || baseColor;
          const s = makeLine(key, color, scaleId);
          const colVals = (indicator.values as { [k: string]: (number | null)[] })[col];
          const pts = timestamps
            .map((t, j) => ({ time: t, value: colVals[j] }))
            .filter((p) => p.value != null) as { time: Time; value: number }[];
          s.setData(pts);
        });
      }
    }
  }, [indicators, data, chartReady]);

  const hasSeparateIndicator = Object.values(indicators).some((ind) => ind.type === 'separate');

  return (
    <div
      className="trading-chart-container"
      style={{ position: 'relative' }}
      data-has-separate={hasSeparateIndicator || undefined}
    >
      <div ref={chartContainerRef} style={{ width: '100%', height }} />
      {isLoading && data.length === 0 && (
        <div className="chart-loading" style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <LoadingSpinner message="Loading chart data..." />
        </div>
      )}
      {error && data.length === 0 && !isLoading && (
        <div className="chart-error" style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <p>Error loading chart: {error}</p>
          <button onClick={() => fetchData(selectedTimeframe)}>Retry</button>
        </div>
      )}
    </div>
  );
}
