import React, { useState } from 'react';
import TaskForm from './components/TaskForm';
import TaskList from './components/TaskList';
import './App.css';

const App = () => {
  const [refresh, setRefresh] = useState(false);
  const triggerRefresh = () => setRefresh(!refresh);

  return (
    <div>
      <h1>📝 Task Manager App</h1>
      <TaskForm fetchTasks={triggerRefresh} />
      <TaskList refresh={refresh} />
    </div>
  );
};

export default App;
