import React, { useState, useEffect } from 'react';

interface EconomicEvent {
  date: string;
  time: string;
  currency: string;
  event: string;
  impact: 'high' | 'medium' | 'low';
}

export function EconomicCalendar() {
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

  return (
    <div className="economic-calendar">
      <h3>Economic Calendar</h3>
      <p className="description">
        Upcoming economic events that may impact GBP/USD. High impact events can cause significant volatility.
      </p>
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
                <th>Date</th>
                <th>Time</th>
                <th>Currency</th>
                <th>Event</th>
                <th>Impact</th>
              </tr>
            </thead>
            <tbody>
              {filteredEvents.map((event, index) => (
                <tr key={index}>
                  <td>{event.date}</td>
                  <td>{event.time}</td>
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

