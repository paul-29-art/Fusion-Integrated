import React, { useState } from 'react';
import axios from 'axios';

const LeaveApplicationForm = () => {
  const [category, setCategory] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [stationLeave, setStationLeave] = useState('');
  const [substitute, setSubstitute] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/api/elm/apply/', {
        category,
        startDate,
        endDate,
        stationLeave,
        substitute,
      });
      console.log('Leave application submitted successfully:', response.data);
    } catch (error) {
      console.error('Error submitting leave application:',
error);
    }
  };

  return (
    <div>
      <h2>Leave Application Form</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Category:</label>
          <select value={category} onChange={(e) =>
setCategory(e.target.value)}>
            <option value="Annual">Annual</option>
            <option value="Casual">Casual</option>
            {/* Add more categories as needed */}
          </select>
        </div>
        <div>
          <label>Start Date:</label>
          <input type="date" value={startDate} onChange={(e)
    <setStartDate(e.target.value)} />
        </div>
        <div>
          <label>End Date:</label>
          <input type="date" value={endDate} onChange={(e)
    <setEndDate(e.target.value)} />
        </div>
        <div>
          <label>Station Leave:</label>
          <input type="text" value={stationLeave}
onChange={(e) => setStationLeave(e.target.value)} />
        </div>
        <div>
          <label>Substitute:</label>
          <input type="text" value={substitute}
onChange={(e) => setSubstitute(e.target.value)} />
        </div>
        <button type="submit">Submit</button>
      </form>
    </div>
  );
};

export default LeaveApplicationForm;