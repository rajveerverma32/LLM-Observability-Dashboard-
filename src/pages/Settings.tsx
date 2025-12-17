import React, { useEffect, useState } from 'react';
import { Box, Paper, Typography, Switch, FormControlLabel, TextField, Button, Divider, Alert, Snackbar } from '@mui/material';
import { Save } from '@mui/icons-material';
import { settingsService } from '../services/api';
import type { SystemSettings } from '../types';

const Settings: React.FC = () => {
  const [settings, setSettings] = useState<SystemSettings>({
    claudeHaiku45Enabled: false,
    maxTokensPerRequest: 4096,
    enableCaching: true,
  });
  const [loading, setLoading] = useState(true);
  const [saveSuccess, setSaveSuccess] = useState(false);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const data = await settingsService.getSettings();
        setSettings(data);
      } catch (error) {
        console.error('Failed to fetch settings:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSettings();
  }, []);

  const handleSave = async () => {
    try {
      await settingsService.updateSettings(settings);
      setSaveSuccess(true);
    } catch (error) {
      console.error('Failed to save settings:', error);
    }
  };

  const handleChange = (field: keyof SystemSettings, value: boolean | number) => {
    setSettings((prev) => ({ ...prev, [field]: value }));
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <Typography>Loading settings...</Typography>
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" fontWeight="bold" gutterBottom>
        System Settings
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Configure system-wide settings for all clients
      </Typography>

      <Paper sx={{ p: 3 }}>
        <Box sx={{ display: 'grid', gap: 3 }}>
          {/* Claude Haiku 4.5 Toggle */}
          <Box>
            <Box
              sx={{
                p: 2,
                borderRadius: 1,
                bgcolor: settings.claudeHaiku45Enabled ? 'primary.50' : 'grey.50',
                border: '1px solid',
                borderColor: settings.claudeHaiku45Enabled ? 'primary.main' : 'grey.300',
              }}
            >
              <FormControlLabel
                control={
                  <Switch
                    checked={settings.claudeHaiku45Enabled}
                    onChange={(e) => handleChange('claudeHaiku45Enabled', e.target.checked)}
                    color="primary"
                  />
                }
                label={
                  <Box>
                    <Typography variant="subtitle1" fontWeight="bold">
                      Enable Claude Haiku 4.5 for All Clients
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      When enabled, all clients will have access to Claude Haiku 4.5 model for faster
                      and more cost-effective responses.
                    </Typography>
                  </Box>
                }
              />
            </Box>
          </Box>

          <Box>
            <Divider />
          </Box>

          {/* Max Tokens */}
          <Box>
            <Typography variant="subtitle2" gutterBottom>
              Max Tokens Per Request
            </Typography>
            <TextField
              fullWidth
              type="number"
              value={settings.maxTokensPerRequest}
              onChange={(e) => handleChange('maxTokensPerRequest', parseInt(e.target.value))}
              slotProps={{
                htmlInput: { min: 1, max: 32000 },
              }}
              helperText="Maximum tokens allowed per API request (1-32000)"
            />
          </Box>

          {/* Enable Caching */}
          <Box>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.enableCaching}
                  onChange={(e) => handleChange('enableCaching', e.target.checked)}
                />
              }
              label={
                <Box>
                  <Typography variant="subtitle2">Enable Response Caching</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Cache responses to reduce latency and costs
                  </Typography>
                </Box>
              }
            />
          </Box>

          <Box>
            <Divider />
          </Box>

          {/* Save Button */}
          <Box>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
              <Button
                variant="contained"
                startIcon={<Save />}
                onClick={handleSave}
                size="large"
              >
                Save Settings
              </Button>
            </Box>
          </Box>
        </Box>

        {/* Info Alert */}
        <Alert severity="info" sx={{ mt: 3 }}>
          <Typography variant="body2">
            <strong>Note:</strong> Changes to these settings will be applied immediately to all
            active clients and future requests.
          </Typography>
        </Alert>
      </Paper>

      {/* Success Snackbar */}
      <Snackbar
        open={saveSuccess}
        autoHideDuration={3000}
        onClose={() => setSaveSuccess(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert severity="success" onClose={() => setSaveSuccess(false)}>
          Settings saved successfully!
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Settings;
