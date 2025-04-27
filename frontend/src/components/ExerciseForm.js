import React, { useState, useEffect } from 'react';
import {
  Button,
  TextField,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  FormControlLabel,
  Switch,
  Box,
  Rating,
  Typography,
  CircularProgress,
  Alert
} from '@mui/material';
import { exerciseService } from '../services/exercise';

const defaultExercise = {
  name: '',
  description: '',
  difficulty_level: 3,
  is_public: true
};

const ExerciseForm = ({ open, onClose, exerciseId = null, onSaved }) => {
  const [exercise, setExercise] = useState(defaultExercise);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [saving, setSaving] = useState(false);
  const isEditMode = !!exerciseId;

  useEffect(() => {
    // Reset form when dialog opens/closes
    if (open) {
      setError('');
      
      if (isEditMode) {
        // Fetch exercise data for editing
        setLoading(true);
        exerciseService.getExercise(exerciseId)
          .then(data => {
            setExercise(data);
            setLoading(false);
          })
          .catch(err => {
            setError('Failed to load exercise data');
            setLoading(false);
          });
      } else {
        // Reset to defaults for new exercise
        setExercise(defaultExercise);
      }
    }
  }, [open, exerciseId, isEditMode]);

  const handleInputChange = (e) => {
    const { name, value, checked } = e.target;
    setExercise({
      ...exercise,
      [name]: name === 'is_public' ? checked : value
    });
  };

  const handleDifficultyChange = (_, newValue) => {
    setExercise({
      ...exercise,
      difficulty_level: newValue
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    try {
      let savedExercise;
      
      if (isEditMode) {
        // Update existing exercise
        savedExercise = await exerciseService.updateExercise(exerciseId, exercise);
      } else {
        // Create new exercise
        savedExercise = await exerciseService.createExercise(exercise);
      }
      
      // Close form and notify parent component
      onSaved(savedExercise);
      onClose();
    } catch (err) {
      console.error('Error saving exercise:', err);
      setError(`Failed to ${isEditMode ? 'update' : 'create'} exercise. Please try again.`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
      <DialogTitle>{isEditMode ? 'Edit Exercise' : 'New Exercise'}</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          {loading ? (
            <Box display="flex" justifyContent="center" my={4}>
              <CircularProgress />
            </Box>
          ) : (
            <>
              <DialogContentText>
                {isEditMode 
                  ? 'Update exercise details below.' 
                  : 'Fill in the details to create a new exercise.'}
              </DialogContentText>
              
              <TextField
                margin="normal"
                name="name"
                label="Exercise Name"
                type="text"
                fullWidth
                required
                value={exercise.name}
                onChange={handleInputChange}
                disabled={saving}
              />
              
              <TextField
                margin="normal"
                name="description"
                label="Description"
                type="text"
                fullWidth
                multiline
                rows={4}
                value={exercise.description}
                onChange={handleInputChange}
                disabled={saving}
              />
              
              <Box sx={{ mt: 2, mb: 1 }}>
                <Typography component="legend">Difficulty Level</Typography>
                <Rating
                  name="difficulty_level"
                  value={exercise.difficulty_level}
                  onChange={handleDifficultyChange}
                  precision={1}
                  disabled={saving}
                />
                <Typography variant="body2" color="text.secondary">
                  {exercise.difficulty_level} - 
                  {exercise.difficulty_level === 1 && ' Very Easy'}
                  {exercise.difficulty_level === 2 && ' Easy'}
                  {exercise.difficulty_level === 3 && ' Moderate'}
                  {exercise.difficulty_level === 4 && ' Hard'}
                  {exercise.difficulty_level === 5 && ' Very Hard'}
                </Typography>
              </Box>
              
              <FormControlLabel
                control={
                  <Switch
                    name="is_public"
                    checked={exercise.is_public}
                    onChange={handleInputChange}
                    disabled={saving}
                  />
                }
                label="Public (visible to all users)"
                sx={{ mt: 2 }}
              />
            </>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button 
            type="submit" 
            variant="contained" 
            color="primary"
            disabled={loading || saving}
          >
            {saving ? <CircularProgress size={24} /> : (isEditMode ? 'Update' : 'Create')}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default ExerciseForm; 