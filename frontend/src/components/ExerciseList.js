import React, { useState, useEffect } from 'react';
import { 
  Grid, 
  Paper, 
  Card, 
  CardContent, 
  CardActions, 
  Typography, 
  Button,
  Box,
  Rating,
  Chip,
  IconButton,
  Tooltip,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert
} from '@mui/material';
import StarIcon from '@mui/icons-material/Star';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import BookmarkBorderIcon from '@mui/icons-material/BookmarkBorder';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import { authService } from '../services/auth';
import { exerciseService } from '../services/exercise';

const ExerciseList = ({ tabType, onEditExercise }) => {
  const [exercises, setExercises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [nameFilter, setNameFilter] = useState('');
  const [difficultyFilter, setDifficultyFilter] = useState('');
  const [sortByDifficulty, setSortByDifficulty] = useState(false);

  // Fetch exercises based on the active tab
  useEffect(() => {
    const fetchExercises = async () => {
      setLoading(true);
      setError('');
      
      try {
        let fetchedExercises = [];
        
        if (tabType === 'all') {
          // Fetch all exercises (public + user's private ones)
          fetchedExercises = await exerciseService.getExercises({
            name: nameFilter || undefined,
            difficulty_level: difficultyFilter || undefined,
            sort_by_difficulty: sortByDifficulty
          });
        } else if (tabType === 'my') {
          // Fetch only user's created exercises
          // This would typically be a separate endpoint, but we'll filter client-side for now
          const allExercises = await exerciseService.getExercises();
          fetchedExercises = allExercises.filter(
            exercise => exercise.creator_id === authService.getUserId()
          );
        } else if (tabType === 'favorites' || tabType === 'saved') {
          // Fetch favorited or saved exercises
          fetchedExercises = await exerciseService.getPersonalExercises(tabType);
        }
        
        setExercises(fetchedExercises);
      } catch (err) {
        console.error('Error fetching exercises:', err);
        setError('Failed to load exercises. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchExercises();
  }, [tabType, nameFilter, difficultyFilter, sortByDifficulty]);

  // Handle favorite toggle
  const handleFavoriteToggle = async (exerciseId, isFavorited) => {
    try {
      if (isFavorited) {
        await exerciseService.unfavoriteExercise(exerciseId);
      } else {
        await exerciseService.favoriteExercise(exerciseId);
      }
      
      // Update the exercises list
      setExercises(exercises.map(exercise => 
        exercise.id === exerciseId 
          ? { 
              ...exercise, 
              is_favorited: !isFavorited,
              favorite_count: isFavorited 
                ? exercise.favorite_count - 1 
                : exercise.favorite_count + 1
            } 
          : exercise
      ));
    } catch (err) {
      console.error('Error toggling favorite:', err);
      setError('Failed to update favorite status.');
    }
  };

  // Handle save toggle
  const handleSaveToggle = async (exerciseId, isSaved) => {
    try {
      if (isSaved) {
        await exerciseService.unsaveExercise(exerciseId);
      } else {
        await exerciseService.saveExercise(exerciseId);
      }
      
      // Update the exercises list
      setExercises(exercises.map(exercise => 
        exercise.id === exerciseId 
          ? { 
              ...exercise, 
              is_saved: !isSaved,
              save_count: isSaved 
                ? exercise.save_count - 1 
                : exercise.save_count + 1
            } 
          : exercise
      ));
    } catch (err) {
      console.error('Error toggling save:', err);
      setError('Failed to update save status.');
    }
  };

  // Handle delete exercise
  const handleDelete = async (exerciseId) => {
    if (window.confirm('Are you sure you want to delete this exercise?')) {
      try {
        await exerciseService.deleteExercise(exerciseId);
        // Remove the exercise from the list
        setExercises(exercises.filter(exercise => exercise.id !== exerciseId));
      } catch (err) {
        console.error('Error deleting exercise:', err);
        setError('Failed to delete exercise.');
      }
    }
  };

  // Handle edit exercise
  const handleEdit = (exerciseId) => {
    if (onEditExercise) {
      onEditExercise(exerciseId);
    }
  };

  return (
    <Box>
      {/* Filter controls */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} sm={4}>
            <TextField
              fullWidth
              label="Filter by Name"
              variant="outlined"
              value={nameFilter}
              onChange={(e) => setNameFilter(e.target.value)}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel>Difficulty Level</InputLabel>
              <Select
                value={difficultyFilter}
                label="Difficulty Level"
                onChange={(e) => setDifficultyFilter(e.target.value)}
              >
                <MenuItem value="">Any</MenuItem>
                <MenuItem value="1">1 - Very Easy</MenuItem>
                <MenuItem value="2">2 - Easy</MenuItem>
                <MenuItem value="3">3 - Moderate</MenuItem>
                <MenuItem value="4">4 - Hard</MenuItem>
                <MenuItem value="5">5 - Very Hard</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <Button
                variant={sortByDifficulty ? "contained" : "outlined"}
                onClick={() => setSortByDifficulty(!sortByDifficulty)}
                startIcon={<StarIcon />}
              >
                Sort by Difficulty
              </Button>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Error message */}
      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Loading indicator */}
      {loading ? (
        <Box display="flex" justifyContent="center" my={4}>
          <CircularProgress />
        </Box>
      ) : exercises.length === 0 ? (
        <Alert severity="info" sx={{ mb: 3 }}>
          No exercises found. {tabType !== 'all' && 'Try a different filter or tab.'}
        </Alert>
      ) : (
        <Grid container spacing={3}>
          {exercises.map((exercise) => (
            <Grid item xs={12} sm={6} md={4} key={exercise.id}>
              <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                <CardContent sx={{ flexGrow: 1 }}>
                  <Box 
                    sx={{ 
                      display: 'flex', 
                      justifyContent: 'space-between',
                      alignItems: 'flex-start' 
                    }}
                  >
                    <Typography gutterBottom variant="h5" component="h2">
                      {exercise.name}
                    </Typography>
                    <Chip 
                      label={exercise.is_public ? "Public" : "Private"} 
                      color={exercise.is_public ? "success" : "default"}
                      size="small"
                    />
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <Rating
                      name={`difficulty-${exercise.id}`}
                      value={exercise.difficulty_level}
                      readOnly
                      precision={1}
                      size="small"
                    />
                    <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                      Difficulty: {exercise.difficulty_level}/5
                    </Typography>
                  </Box>
                  <Typography variant="body2" color="text.secondary" paragraph>
                    {exercise.description.length > 120 
                      ? `${exercise.description.substring(0, 120)}...` 
                      : exercise.description}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip 
                      icon={<StarIcon fontSize="small" />} 
                      label={`${exercise.favorite_count} Favorites`}
                      size="small"
                      variant="outlined"
                    />
                    <Chip 
                      icon={<BookmarkIcon fontSize="small" />} 
                      label={`${exercise.save_count} Saves`}
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                </CardContent>
                <CardActions>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', width: '100%' }}>
                    <Box>
                      <Tooltip title={exercise.is_favorited ? "Unfavorite" : "Favorite"}>
                        <IconButton 
                          color={exercise.is_favorited ? "primary" : "default"}
                          onClick={() => handleFavoriteToggle(exercise.id, exercise.is_favorited)}
                        >
                          <StarIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title={exercise.is_saved ? "Unsave" : "Save"}>
                        <IconButton 
                          color={exercise.is_saved ? "primary" : "default"}
                          onClick={() => handleSaveToggle(exercise.id, exercise.is_saved)}
                        >
                          {exercise.is_saved ? <BookmarkIcon /> : <BookmarkBorderIcon />}
                        </IconButton>
                      </Tooltip>
                    </Box>
                    
                    {/* Only show edit/delete for user's own exercises */}
                    {exercise.creator_id === authService.getUserId() && (
                      <Box>
                        <Tooltip title="Edit">
                          <IconButton onClick={() => handleEdit(exercise.id)}>
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton 
                            color="error"
                            onClick={() => handleDelete(exercise.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    )}
                  </Box>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Box>
  );
};

export default ExerciseList; 