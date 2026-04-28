import React, { useState, useEffect } from 'react';

interface EconomicEvent {
  date: string;
  time: string;
  currency: string;
  event: string;
  impact: 'high' | 'medium' | 'low';
}

export function EconomicCalendar({ compact }: { compact?: boolean }) {
  const [events, setEvents] = useState<EconomicEvent[]>([]);
  const [filter, setFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');

  useEffect(() => {
    // Mock data - in production, fetch from economic calendar API
    const mockEvents: EconomicEvent[] = [
      {
        date: '2024-01-15',
        time: '08:30 GMT',
        currency: 'GBP',
        event: 'CPI (YoY)',
        impact: 'high',
      },
      {
        date: '2024-01-15',
        time: '13:30 GMT',
        currency: 'USD',
        event: 'Retail Sales',
        impact: 'high',
      },
      {
        date: '2024-01-16',
        time: '09:00 GMT',
        currency: 'GBP',
        event: 'Employment Change',
        impact: 'medium',
      },
      {
        date: '2024-01-17',
        time: '14:00 GMT',
        currency: 'USD',
        event: 'Fed Interest Rate Decision',
        impact: 'high',
      },
    ];
    setEvents(mockEvents);
  }, []);

  const filteredEvents = filter === 'all' 
    ? events 
    : events.filter(e => e.impact === filter);

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high': return '#ef5350';
      case 'medium': return '#ff9800';
      case 'low': return '#26a69a';
      default: return '#9ca3af';
    }
  };

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en', { month: 'short', day: 'numeric' });
  };

  return (
    <div className="economic-calendar">
      {!compact && <h3>Economic Calendar</h3>}
      <div className="calendar-filters">
        <button 
          className={filter === 'all' ? 'active' : ''}
          onClick={() => setFilter('all')}
        >
          All
        </button>
        <button 
          className={filter === 'high' ? 'active' : ''}
          onClick={() => setFilter('high')}
        >
          High Impact
        </button>
        <button 
          className={filter === 'medium' ? 'active' : ''}
          onClick={() => setFilter('medium')}
        >
          Medium Impact
        </button>
        <button 
          className={filter === 'low' ? 'active' : ''}
          onClick={() => setFilter('low')}
        >
          Low Impact
        </button>
      </div>
      <div className="events-list">
        {filteredEvents.length === 0 ? (
          <p>No upcoming events</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th style={{ whiteSpace: 'nowrap' }}>When</th>
                <th>Ccy</th>
                <th>Event</th>
                <th>Impact</th>
              </tr>
            </thead>
            <tbody>
              {filteredEvents.map((event, index) => (
                <tr key={index}>
                  <td style={{ whiteSpace: 'nowrap' }}>
                    <div>{formatDate(event.date)}</div>
                    <div style={{ fontSize: '10px', color: '#6b7280' }}>{event.time}</div>
                  </td>
                  <td>{event.currency}</td>
                  <td>{event.event}</td>
                  <td>
                    <span
                      className="impact-badge"
                      style={{ backgroundColor: getImpactColor(event.impact) }}
                    >
                      {event.impact.toUpperCase()}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

