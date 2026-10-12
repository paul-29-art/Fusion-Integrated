import React from 'react';
import { Route, Routes } from 'react-router-dom';
import LeaveApplicationForm from './pages/LeaveApplicationForm';
import EmployeeLeaveBalance from './pages/EmployeeLeaveBalance';
import ApproverActionPortal from './pages/ApproverActionPortal';

const ELMRoutes = () => {
  return (
    <Routes>
      <Route path="apply" element={<LeaveApplicationForm />} />
      <Route path="balance" element={<EmployeeLeaveBalance />} />
      <Route path="approver" element={<ApproverActionPortal />} />
    </Routes>
  );
};

export default ELMRoutes;