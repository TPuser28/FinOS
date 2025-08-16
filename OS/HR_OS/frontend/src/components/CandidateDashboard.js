import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Mail, 
  Building, 
  Briefcase, 
  CheckCircle, 
  XCircle, 
  Clock, 
  ExternalLink,
  RefreshCw,
  Search,
  Filter,
  Eye,
  X
} from 'lucide-react';
import './CandidateDashboard.css';

const CandidateDashboard = () => {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all'); // all, pending, screened, passed, failed
  const [selectedCandidate, setSelectedCandidate] = useState(null); // For summary modal

  // Fetch candidates from API
  const fetchCandidates = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/candidates');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setCandidates(data.candidates || []);
    } catch (err) {
      console.error('Error fetching candidates:', err);
      setError('Failed to load candidates. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Load candidates on component mount
  useEffect(() => {
    fetchCandidates();
  }, []);

  // Generate invite link for PreScreen Bot
  const generateInviteLink = (candidateId, candidateName) => {
    const baseUrl = window.location.origin;
    return `${baseUrl}/prescreen?candidate=${encodeURIComponent(candidateName)}&id=${candidateId}`;
  };

  // Copy invite link to clipboard
  const copyInviteLink = async (candidate) => {
    const link = generateInviteLink(candidate.id, candidate.fields['Full Name']);
    try {
      await navigator.clipboard.writeText(link);
      alert(`Invite link copied to clipboard for ${candidate.fields['Full Name']}`);
    } catch (err) {
      console.error('Failed to copy link:', err);
      // Fallback: show the link in a prompt
      prompt('Copy this invite link:', link);
    }
  };

  // Open summary modal
  const openSummaryModal = (candidate) => {
    setSelectedCandidate(candidate);
  };

  // Close summary modal
  const closeSummaryModal = () => {
    setSelectedCandidate(null);
  };

  // Filter candidates based on search and status
  const filteredCandidates = candidates.filter(candidate => {
    const fields = candidate.fields || {};
    const name = fields['Full Name'] || '';
    const email = fields['Email'] || '';
    const department = fields['Department'] || '';
    const position = fields['Position'] || '';
    
    // Search filter
    const matchesSearch = searchTerm === '' || 
      name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      department.toLowerCase().includes(searchTerm.toLowerCase()) ||
      position.toLowerCase().includes(searchTerm.toLowerCase());

    // Status filter
    const didScreening = fields['DidScreening'];
    const passedScreening = fields['PassedScreening'];
    
    let matchesStatus = true;
    if (filterStatus === 'pending') {
      matchesStatus = !didScreening;
    } else if (filterStatus === 'screened') {
      matchesStatus = didScreening === true;
    } else if (filterStatus === 'passed') {
      matchesStatus = didScreening === true && passedScreening === true;
    } else if (filterStatus === 'failed') {
      matchesStatus = didScreening === true && passedScreening === false;
    }

    return matchesSearch && matchesStatus;
  });

  // Get status info for a candidate
  const getStatusInfo = (candidate) => {
    const fields = candidate.fields || {};
    const didScreening = fields['DidScreening'];
    const passedScreening = fields['PassedScreening'];

    if (!didScreening) {
      return { status: 'pending', label: 'Pending Screening', color: 'orange', icon: Clock };
    } else if (passedScreening === true) {
      return { status: 'passed', label: 'Passed Screening', color: 'green', icon: CheckCircle };
    } else if (passedScreening === false) {
      return { status: 'failed', label: 'Failed Screening', color: 'red', icon: XCircle };
    } else {
      return { status: 'screened', label: 'Screened', color: 'blue', icon: CheckCircle };
    }
  };

  // Get statistics
  const getStats = () => {
    const total = candidates.length;
    const pending = candidates.filter(c => !c.fields?.['DidScreening']).length;
    const screened = candidates.filter(c => c.fields?.['DidScreening']).length;
    const passed = candidates.filter(c => c.fields?.['DidScreening'] && c.fields?.['PassedScreening']).length;
    const failed = candidates.filter(c => c.fields?.['DidScreening'] && c.fields?.['PassedScreening'] === false).length;

    return { total, pending, screened, passed, failed };
  };

  const stats = getStats();

  if (loading) {
    return (
      <div className="dashboard-loading">
        <RefreshCw className="loading-spinner" size={32} />
        <p>Loading candidates...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <XCircle size={48} className="error-icon" />
        <h3>Error Loading Candidates</h3>
        <p>{error}</p>
        <button onClick={fetchCandidates} className="retry-button">
          <RefreshCw size={16} />
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className="candidate-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-title">
          <Users size={24} />
          <h2>Candidate Dashboard</h2>
        </div>
        <button onClick={fetchCandidates} className="refresh-button" title="Refresh data">
          <RefreshCw size={16} />
          Refresh
        </button>
      </div>

      {/* Statistics */}
      <div className="dashboard-stats">
        <div className="stat-card">
          <div className="stat-number">{stats.total}</div>
          <div className="stat-label">Total Candidates</div>
        </div>
        <div className="stat-card pending">
          <div className="stat-number">{stats.pending}</div>
          <div className="stat-label">Pending Screening</div>
        </div>
        <div className="stat-card screened">
          <div className="stat-number">{stats.screened}</div>
          <div className="stat-label">Screened</div>
        </div>
        <div className="stat-card passed">
          <div className="stat-number">{stats.passed}</div>
          <div className="stat-label">Passed</div>
        </div>
        <div className="stat-card failed">
          <div className="stat-number">{stats.failed}</div>
          <div className="stat-label">Failed</div>
        </div>
      </div>

      {/* Filters */}
      <div className="dashboard-filters">
        <div className="search-box">
          <Search size={16} />
          <input
            type="text"
            placeholder="Search candidates..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <div className="filter-box">
          <Filter size={16} />
          <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
            <option value="all">All Candidates</option>
            <option value="pending">Pending Screening</option>
            <option value="screened">Screened</option>
            <option value="passed">Passed</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {/* Candidates Table */}
      <div className="candidates-table-container">
        {filteredCandidates.length === 0 ? (
          <div className="no-candidates">
            <Users size={48} className="no-candidates-icon" />
            <h3>No candidates found</h3>
            <p>
              {searchTerm || filterStatus !== 'all' 
                ? 'Try adjusting your search or filter criteria.'
                : 'No candidates have been added yet.'
              }
            </p>
          </div>
        ) : (
          <table className="candidates-table">
            <thead>
              <tr>
                <th>Candidate</th>
                <th>Department</th>
                <th>Position</th>
                <th>Status</th>
                <th>Summary</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredCandidates.map((candidate) => {
                const fields = candidate.fields || {};
                const statusInfo = getStatusInfo(candidate);
                const StatusIcon = statusInfo.icon;

                return (
                  <tr key={candidate.id}>
                    <td>
                      <div className="candidate-info">
                        <div className="candidate-name">{fields['Full Name'] || 'N/A'}</div>
                        <div className="candidate-email">
                          <Mail size={12} />
                          {fields['Email'] || 'N/A'}
                        </div>
                      </div>
                    </td>
                    <td>
                      <div className="department-info">
                        <Building size={14} />
                        {fields['Department'] || 'N/A'}
                      </div>
                    </td>
                    <td>
                      <div className="position-info">
                        <Briefcase size={14} />
                        {fields['Position'] || 'N/A'}
                      </div>
                    </td>
                    <td>
                      <div className={`status-badge status-${statusInfo.status}`}>
                        <StatusIcon size={14} />
                        {statusInfo.label}
                      </div>
                    </td>
                    <td>
                      <div className="summary-cell">
                        {fields['Summary'] ? (
                          <div className="summary-content">
                            <div className="summary-text" title={fields['Summary']}>
                              {fields['Summary'].length > 100 
                                ? `${fields['Summary'].substring(0, 100)}...`
                                : fields['Summary']
                              }
                            </div>
                            <button
                              onClick={() => openSummaryModal(candidate)}
                              className="view-summary-button"
                              title="View full summary"
                            >
                              <Eye size={14} />
                            </button>
                          </div>
                        ) : (
                          <span className="no-summary">No summary available</span>
                        )}
                      </div>
                    </td>
                    <td>
                      <div className="actions-cell">
                        {!fields['DidScreening'] ? (
                          <button
                            onClick={() => copyInviteLink(candidate)}
                            className="invite-button"
                            title="Copy invite link for pre-screening"
                          >
                            <ExternalLink size={14} />
                            Invite
                          </button>
                        ) : (
                          <span className="completed-text">Completed</span>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Summary Modal */}
      {selectedCandidate && (
        <div className="modal-overlay" onClick={closeSummaryModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Candidate Summary</h3>
              <button onClick={closeSummaryModal} className="modal-close-button">
                <X size={20} />
              </button>
            </div>
            <div className="modal-body">
              <div className="candidate-details">
                <div className="detail-row">
                  <strong>Name:</strong> {selectedCandidate.fields['Full Name'] || 'N/A'}
                </div>
                <div className="detail-row">
                  <strong>Email:</strong> {selectedCandidate.fields['Email'] || 'N/A'}
                </div>
                <div className="detail-row">
                  <strong>Department:</strong> {selectedCandidate.fields['Department'] || 'N/A'}
                </div>
                <div className="detail-row">
                  <strong>Position:</strong> {selectedCandidate.fields['Position'] || 'N/A'}
                </div>
                <div className="detail-row">
                  <strong>Status:</strong> 
                  <span className={`status-badge status-${getStatusInfo(selectedCandidate).status}`}>
                    {getStatusInfo(selectedCandidate).label}
                  </span>
                </div>
              </div>
              <div className="summary-section">
                <h4>Summary</h4>
                <div className="full-summary">
                  {selectedCandidate.fields['Summary'] || 'No summary available'}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CandidateDashboard;
