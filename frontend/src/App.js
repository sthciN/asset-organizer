import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
    const backendUrl = 'http://localhost:8000';
    const [status, setStatus] = useState('');
    const [dataList, setDataList] = useState([]);
    const [intervalId, setIntervalId] = useState(null);
    const [isStartButtonDisabled, setIsStartButtonDisabled] = useState(false);
    const [taskId, setTaskId] = useState(null);

    const fetchStatus = () => {
        fetch(`${backendUrl}/task-status/${taskId}`, { method: 'GET' })
            .then(response => response.json())
            .then(data => {
                setStatus(data.detail.status);
            })
            .catch(error => {
                console.error('Error fetching status:', error);
                setStatus('Error');
            });
    };

    const fetchFileList = () => {
        setDataList([]);
        setStatus('Processing...');
        fetch(`${backendUrl}/file-list`, { method: 'GET' })
            .then(response => response.json())
            .then(data => {
                console.log('Response:', typeof (data));
                setDataList(data.detail);
                setStatus('Fetch is done.');
            })
            .catch(error => {
                console.error('Error fetching file list:', error);
                setDataList([]);
            });
    };

    const startProcess = () => {
        // Call the /api/process-pngs endpoint
        fetch(`${backendUrl}/api/process-pngs-background`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log('Process started:', data.detail.message);
                setTaskId(data.detail.task_id);
                setStatus(data.detail.message);
                setIsStartButtonDisabled(true);
            })
            .catch(error => {
                setStatus('Error accured. Please contact the admin...');
                console.error('Error starting process:', error);
            });
    };

    const stopProcess = () => {
        // Stop polling
        if (intervalId) {
            clearInterval(intervalId);
            setIntervalId(null);
        }
    };

    useEffect(() => {
        if (taskId) {
            // Polling the status
            const id = setInterval(() => fetchStatus(taskId), 10000); // Every 10sec
            setIntervalId(id);
            return () => clearInterval(id);
        }
    }, [taskId]);

    useEffect(() => {
        if (status === 'Completed') {
            setIsStartButtonDisabled(false);
            stopProcess(); // Stop polling when the process is completed
        }
    }, [status]);

    const containerStyle = {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        fontFamily: 'Arial, sans-serif',
        backgroundColor: '#f0f0f0',
        padding: '20px'
    };

    const buttonStyle = {
        margin: '10px',
        padding: '10px 20px',
        fontSize: '16px',
        cursor: 'pointer',
        borderRadius: '5px',
        border: 'none',
        backgroundColor: '#007BFF',
        color: 'white',
        transition: 'background-color 0.3s',
    };

    const buttonDisabledStyle = {
        ...buttonStyle,
        backgroundColor: '#6c757d',
        cursor: 'not-allowed',
    };

    const listStyle = {
        overflowY: 'auto',
        listStyleType: 'none',
        padding: '0',
    };
    const listItemStyle = {
        backgroundColor: 'white',
        padding: '10px',
        margin: '5px 0',
        borderRadius: '5px',
        boxShadow: '0 0 5px rgba(0,0,0,0.1)',
    };

    return (
        <div style={containerStyle}>
            <h1>Status: {status}</h1>
            <button
                onClick={startProcess}
                disabled={isStartButtonDisabled}
                style={isStartButtonDisabled ? buttonDisabledStyle : buttonStyle}
            >
                Start
            </button>
            <button onClick={fetchFileList} style={buttonStyle}>Fetch File List</button>
            <ul style={listStyle}>
                {dataList.map((item, index) => (
                    <li key={index} style={listItemStyle}>{item}</li>
                ))}
            </ul>
        </div>
    );
};

export default App;
