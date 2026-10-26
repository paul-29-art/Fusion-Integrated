import React, { useState, useEffect } from 'react';
import axios from 'axios';

const EmployeeLeaveBalance = () => {
  const [leaveBalance, setLeaveBalance] = useState([]);
  const [requestHistory, setRequestHistory] = useState([]);

  useEffect(() => {
    const fetchLeaveBalance = async () => {
      try {
        const response = await axios.get('/api/elm/leave-balance/');
        setLeaveBalance(response.data);
      } catch (error) {
        console.error('Error fetching leave balance:', error);
      }
    };

    const fetchRequestHistory = async () => {
      try {
        const response = await axios.get('/api/elm/request-history/');
        setRequestHistory(response.data);
      } catch (error) {
        console.error('Error fetching request history:', error);
      }
    };

    fetchLeaveBalance();
    fetchRequestHistory();
  }, []);

  return (
    <div>
      <h2>Leave Balance</h2>
      <ul>
        {leaveBalance.map((balance) => (
          <li key={balance.id}>
            {balance.category}: {balance.balance}
          </li>
        ))}
      </ul>
      <h2>Request History</h2>
      <ul>
        {requestHistory.map((request) => (
          <li key={request.id}>
            {request.category} from {request.startDate} to {request.endDate}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default EmployeeLeaveBalance;
