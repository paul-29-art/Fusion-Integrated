import React from 'react';
import { Route, Routes } from 'react-router-dom';
// @ts-ignore
import LeaveApplicationForm from './api/components/pages/LeaveApplicationForm';
// @ts-ignore
import EmployeeLeaveBalance from './api/components/pages/EmployeeLeaveBalance';
// @ts-ignore
import ApproverActionPortal from './api/components/pages/ApproverActionPortal';

const ELMRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="apply" element={<LeaveApplicationForm />} />
      <Route path="balance" element={<EmployeeLeaveBalance />} />
      <Route path="approver" element={<ApproverActionPortal />} />
    </Routes>
  );
};

export default ELMRoutes;
