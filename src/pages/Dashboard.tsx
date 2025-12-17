import React, { useEffect, useState } from 'react';
import { Box, Paper, Typography, Card, CardContent } from '@mui/material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import {
  TrendingUp,
  Timer,
  Error as ErrorIcon,
  AttachMoney,
} from '@mui/icons-material';
import { dashboardService } from '../services/api';
import type { TokenUsage, LatencyData, ErrorData, DashboardStats } from '../types';

const COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#00f2fe'];

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [tokenUsage, setTokenUsage] = useState<TokenUsage[]>([]);
  const [latencyData, setLatencyData] = useState<LatencyData[]>([]);
  const [errorData, setErrorData] = useState<ErrorData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, tokenData, latData, errData] = await Promise.all([
          dashboardService.getStats(),
          dashboardService.getTokenUsage(),
          dashboardService.getLatencyData(),
          dashboardService.getErrorData(),
        ]);
        setStats(statsData);
        setTokenUsage(tokenData);
        setLatencyData(latData);
        setErrorData(errData);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    icon: React.ReactNode;
    color: string;
  }> = ({ title, value, icon, color }) => (
    <Card elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <Box
            sx={{
              bgcolor: `${color}20`,
              color,
              p: 1,
              borderRadius: 1,
              display: 'flex',
              mr: 2,
            }}
          >
            {icon}
          </Box>
          <Typography variant="body2" color="text.secondary">
            {title}
          </Typography>
        </Box>
        <Typography variant="h4" fontWeight="bold">
          {value}
        </Typography>
      </CardContent>
    </Card>
  );

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <Typography>Loading dashboard...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        Dashboard Overview
      </Typography>

      {/* Stats Cards */}
      <Box
        sx={{
          display: 'grid',
          gap: 3,
          mb: 3,
          gridTemplateColumns: {
            xs: '1fr',
            sm: '1fr 1fr',
            md: 'repeat(4, 1fr)',
          },
        }}
      >
          <StatCard
            title="Total Tokens"
            value={stats?.totalTokens.toLocaleString() || '0'}
            icon={<TrendingUp />}
            color="#667eea"
          />
        <StatCard
          title="Total Cost"
          value={`$${stats?.totalCost.toFixed(2) || '0'}`}
          icon={<AttachMoney />}
          color="#764ba2"
        />
        <StatCard
          title="Avg Latency"
          value={`${stats?.averageLatency || '0'}ms`}
          icon={<Timer />}
          color="#4facfe"
        />
        <StatCard
          title="Error Rate"
          value={`${stats?.errorRate.toFixed(2) || '0'}%`}
          icon={<ErrorIcon />}
          color="#f093fb"
        />
      </Box>

      {/* Charts */}
      <Box
        sx={{
          display: 'grid',
          gap: 3,
          gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' },
        }}
      >
        {/* Token Usage Over Time */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Token Usage Over Time
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={tokenUsage}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="tokens"
                stroke="#667eea"
                strokeWidth={2}
                name="Tokens"
              />
              <Line
                yAxisId="right"
                type="monotone"
                dataKey="cost"
                stroke="#764ba2"
                strokeWidth={2}
                name="Cost ($)"
              />
            </LineChart>
          </ResponsiveContainer>
        </Paper>

        {/* Latency Distribution */}
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Latency Distribution
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={latencyData as any}
                dataKey="count"
                nameKey="range"
                cx="50%"
                cy="50%"
                outerRadius={80}
                label
              >
                {latencyData.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </Paper>
      </Box>
        {/* Error Rate Over Time */}
        <Paper sx={{ p: 3, mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            Error Rate Trend
          </Typography>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={errorData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="errorRate" fill="#f093fb" name="Error Rate (%)" />
            </BarChart>
          </ResponsiveContainer>
        </Paper>
    </Box>
  );
};

export default Dashboard;
