import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ApproverActionPortal = () => {
  const [pendingRequests, setPendingRequests] = useState([]);
  const [selectedRequest, setSelectedRequest] = useState(null);

  useEffect(() => {
    const fetchPendingRequests = async () => {
      try {
        const response = await axios.get('/api/elm/pending-requests/');
        setPendingRequests(response.data);
      } catch (error) {
        console.error('Error fetching pending requests:', error);
      }
    };

    fetchPendingRequests();
  }, []);

  const handleApprove = async () => {
    if (selectedRequest) {
      try {
        await axios.post(`/api/elm/requests/${selectedRequest.id}/approve/`);
        console.log('Request approved:', selectedRequest);
        setSelectedRequest(null);
        setPendingRequests(pendingRequests.filter((req) => req.id !== selectedRequest.id));
      } catch (error) {
        console.error('Error approving request:', error);
      }
    }
  };

  const handleReject = async () => {
    if (selectedRequest) {
      try {
        await axios.post(`/api/elm/requests/${selectedRequest.id}/reject/`);
        console.log('Request rejected:', selectedRequest);
        setSelectedRequest(null);
        setPendingRequests(pendingRequests.filter((req) => req.id !== selectedRequest.id));
      } catch (error) {
        console.error('Error rejecting request:', error);
      }
    }
  };

  return (
    <div>
      <h2>Approver Action Portal</h2>
      <ul>
        {pendingRequests.map((request) => (
          <li key={request.id} onClick={() => setSelectedRequest(request)}>
            {request.employee} - {request.category} from {request.startDate} to {request.endDate}
          </li>
        ))}
      </ul>
      {selectedRequest && (
        <div>
          <h3>Selected Request</h3>
          <p>Employee: {selectedRequest.employee}</p>
          <p>Category: {selectedRequest.category}</p>
          <p>Start Date: {selectedRequest.startDate}</p>
          <p>End Date: {selectedRequest.endDate}</p>
          <button onClick={handleApprove}>Approve</button>
          <button onClick={handleReject}>Reject</button>
        </div>
      )}
    </div>
  );
};

export default ApproverActionPortal;
