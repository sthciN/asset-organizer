import React, { useState, useEffect } from 'react';
import { FaSpinner } from 'react-icons/fa';

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
                setStatus('Completed');
            })
            .catch(error => {
                console.error('Error fetching file list:', error);
                setDataList([]);
            });
    };

    const startProcess = () => {
        fetch(`${backendUrl}/api/process-pngs-background`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log('Process started:', data.detail.message);
                setTaskId(data.detail.task_id);
                setStatus(data.detail.message);
                setIsStartButtonDisabled(true);
            })
            .catch(error => {
                setStatus('Error occurred. Please contact the admin...');
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
            stopProcess();
        }
    }, [status]);

    return (
        <div className="App">
            <div className="box">
                <h1>Status: {status}
                    {status.toLowerCase().includes('in progress') && (
                        <FaSpinner className="spinner" />
                    )}
                </h1>
                <div className="button-container">
                    <button
                        onClick={startProcess}
                        disabled={isStartButtonDisabled}
                    >
                        Start
                    </button>
                    <button onClick={fetchFileList}>Fetch File List</button>
                </div>
            </div>
            <ul>
                {dataList.map((item, index) => (
                    <li key={index}>{item}</li>
                ))}
            </ul>
        </div>
    );
};

export default App;
