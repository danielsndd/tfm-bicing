import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Container, 
  Grid, 
  Paper, 
  Typography,
  CircularProgress
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  AreaChart,
  Area,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell
} from 'recharts';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('http://localhost:5000/api/station-data');
        console.log('Received data:', response.data);
        setData(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return (
    <Container style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <CircularProgress />
    </Container>
  );

  if (error) return (
    <Container>
      <Typography color="error">Error: {error}</Typography>
    </Container>
  );

  if (!data) return (
    <Container>
      <Typography>No data available</Typography>
    </Container>
  );

  // Calculate prediction accuracy for pie chart
  const accuracyData = [
    { name: 'Accurate Predictions', value: data.predictions?.filter((p, i) => Math.abs(p - data.actualValues[i]) <= 2).length || 0 },
    { name: 'Inaccurate Predictions', value: data.predictions?.filter((p, i) => Math.abs(p - data.actualValues[i]) > 2).length || 0 }
  ];

  return (
    <Container maxWidth="lg" style={{ marginTop: '2rem' }}>
      <Typography variant="h4" gutterBottom>
        Bike Sharing Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Station Availability Chart */}
        <Grid item xs={12} md={6}>
          <Paper style={{ padding: '1rem', height: '400px' }}>
            <Typography variant="h6">Station Availability Over Time</Typography>
            <ResponsiveContainer>
              <LineChart data={data.availability}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="last_reported" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="num_bikes_available" stroke="#8884d8" name="Available Bikes" />
                <Line type="monotone" dataKey="num_docks_available" stroke="#82ca9d" name="Available Docks" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Hourly Usage Chart */}
        <Grid item xs={12} md={6}>
          <Paper style={{ padding: '1rem', height: '400px' }}>
            <Typography variant="h6">Average Hourly Usage</Typography>
            <ResponsiveContainer>
              <AreaChart data={data.hourlyUsage}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Area type="monotone" dataKey="num_bikes_available" stroke="#8884d8" fill="#8884d8" name="Average Bikes Available" />
              </AreaChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Prediction Accuracy Pie Chart */}
        <Grid item xs={12} md={6}>
          <Paper style={{ padding: '1rem', height: '400px' }}>
            <Typography variant="h6">Prediction Accuracy</Typography>
            <ResponsiveContainer>
              <PieChart>
                <Pie
                  data={accuracyData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                  outerRadius={150}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {accuracyData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Time Series Forecast Chart */}
        <Grid item xs={12} md={6}>
          <Paper style={{ padding: '1rem', height: '400px' }}>
            <Typography variant="h6">Time Series Forecast</Typography>
            <ResponsiveContainer>
              <LineChart data={data.forecast}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="timestamp" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="predicted" stroke="#8884d8" name="Predicted" />
                <Line type="monotone" dataKey="actual" stroke="#82ca9d" name="Actual" />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default App;