import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Button,
  IconButton,
  Card,
  CardContent,
  CardActions,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControlLabel,
  Switch,
  Snackbar,
  Alert,
  Rating,
  CircularProgress,
  Chip,
  Divider,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Menu,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Tabs,
  Tab,
  AppBar,
  Toolbar,
  Badge
} from '@mui/material';
import {
  Add as AddIcon,
  FitnessCenter as FitnessCenterIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon, 
  Bookmark as BookmarkIcon,
  BookmarkBorder as BookmarkBorderIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  FilterList as FilterListIcon,
  Sort as SortIcon,
  Public as PublicIcon,
  FilterAlt as FilterAltIcon,
  PersonOutline as PersonOutlineIcon,
  Dashboard as DashboardIcon
} from '@mui/icons-material';
import { exerciseService } from '../services/exercise';
import { authService } from '../services/auth';
import axios from 'axios';

// Set drawer width
const drawerWidth = 240;

const ExerciseLandingPage = () => {
  const navigate = useNavigate();
  
  // State for exercises
  const [exercises, setExercises] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // State for filtering and sorting
  const [filterAnchorEl, setFilterAnchorEl] = useState(null);
  const [nameFilter, setNameFilter] = useState('');
  const [difficultyFilter, setDifficultyFilter] = useState('');
  const [sortByDifficulty, setSortByDifficulty] = useState(false);
  
  // State for view modes
  const [viewMode, setViewMode] = useState('all'); // 'all', 'my', 'favorites', 'saved'
  const [showOnlyPublic, setShowOnlyPublic] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [tabValue, setTabValue] = useState(0);
  
  // State for exercise form
  const [formOpen, setFormOpen] = useState(false);
  const [formTitle, setFormTitle] = useState('Create New Exercise');
  const [currentExercise, setCurrentExercise] = useState(null);
  const [exerciseName, setExerciseName] = useState('');
  const [exerciseDescription, setExerciseDescription] = useState('');
  const [exerciseDifficulty, setExerciseDifficulty] = useState(3);
  const [exerciseIsPublic, setExerciseIsPublic] = useState(true);
  
  // State for feedback
  const [notification, setNotification] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  // Load exercises when component mounts or filters change
  useEffect(() => {
    fetchExercises();
  }, [viewMode, nameFilter, difficultyFilter, sortByDifficulty, showOnlyPublic]);

  // Handle fetch exercises based on current view mode and filters
  const fetchExercises = async () => {
    setLoading(true);
    try {
      let data;
      
      // Apply filters based on view mode
      if (viewMode === 'my') {
        // Get personal exercises created by the user
        const filters = {};
        if (nameFilter) filters.name = nameFilter;
        if (difficultyFilter) filters.difficulty_level = difficultyFilter;
        if (sortByDifficulty) filters.sort_by_difficulty = true;
        
        data = await exerciseService.getExercises(filters);
        // Filter to only show exercises created by current user
        const currentUsername = authService.getCurrentUsername();
        if (currentUsername) {
          data = data.filter(exercise => {
            // The exercise.creator_id might be the user ID or username depending on backend
            // Try both for robustness
            return exercise.creator_id === currentUsername || 
                   exercise.creator?.username === currentUsername;
          });
        }
      } else if (viewMode === 'favorites' || viewMode === 'saved') {
        // Get favorites or saved exercises
        data = await exerciseService.getPersonalExercises(viewMode);
      } else {
        // Get all exercises with filtering
        const filters = {};
        if (nameFilter) filters.name = nameFilter;
        if (difficultyFilter) filters.difficulty_level = difficultyFilter;
        if (sortByDifficulty) filters.sort_by_difficulty = true;
        
        data = await exerciseService.getExercises(filters);
      }
      
      // Apply public/private filter if needed
      if (showOnlyPublic) {
        data = data.filter(exercise => exercise.is_public);
      }
      
      setExercises(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching exercises:', err);
      setError(err.message || 'Failed to load exercises');
      if (err.message.includes('Authentication') || err.message.includes('login again')) {
        // Authentication issue - redirect to login
        authService.logout();
        navigate('/login');
      }
    } finally {
      setLoading(false);
    }
  };

  // Handle drawer toggle
  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    if (newValue === 0) {
      setViewMode('all');
    } else {
      setViewMode('my');
    }
  };

  // Handle view mode change
  const handleViewModeChange = (mode) => {
    setViewMode(mode);
    setMobileOpen(false);
  };

  // Filter menu handlers
  const handleFilterOpen = (event) => {
    setFilterAnchorEl(event.currentTarget);
  };

  const handleFilterClose = () => {
    setFilterAnchorEl(null);
  };

  const handleFilterApply = () => {
    handleFilterClose();
    fetchExercises();
  };

  const handleFilterReset = () => {
    setNameFilter('');
    setDifficultyFilter('');
    setSortByDifficulty(false);
    setShowOnlyPublic(false);
    handleFilterClose();
  };

  // Exercise form handlers
  const handleFormOpen = (exercise = null) => {
    if (exercise) {
      setCurrentExercise(exercise);
      setExerciseName(exercise.name);
      setExerciseDescription(exercise.description);
      setExerciseDifficulty(exercise.difficulty_level);
      setExerciseIsPublic(exercise.is_public);
      setFormTitle('Edit Exercise');
    } else {
      setCurrentExercise(null);
      setExerciseName('');
      setExerciseDescription('');
      setExerciseDifficulty(3);
      setExerciseIsPublic(true);
      setFormTitle('Create New Exercise');
    }
    setFormOpen(true);
  };

  const handleFormClose = () => {
    setFormOpen(false);
  };

  const handleFormSubmit = async () => {
    try {
      const exerciseData = {
        name: exerciseName,
        description: exerciseDescription,
        difficulty_level: exerciseDifficulty,
        is_public: exerciseIsPublic
      };
      
      if (currentExercise) {
        // Update existing exercise
        await exerciseService.updateExercise(currentExercise.id, exerciseData);
        setNotification({
          open: true,
          message: 'Exercise updated successfully',
          severity: 'success'
        });
      } else {
        // Create new exercise
        const result = await exerciseService.createExercise(exerciseData);
        console.log('Exercise created:', result);
        setNotification({
          open: true,
          message: 'Exercise created successfully',
          severity: 'success'
        });
      }
      
      setFormOpen(false);
      fetchExercises();
    } catch (err) {
      console.error('Error saving exercise:', err);
      setNotification({
        open: true,
        message: err.message || 'Failed to save exercise',
        severity: 'error'
      });
      
      if (err.message.includes('Authentication') || err.message.includes('login again')) {
        // Authentication issue - redirect to login
        authService.logout();
        navigate('/login');
      }
    }
  };

  // Exercise interaction handlers
  const handleFavorite = async (exercise) => {
    try {
      if (exercise.is_favorited) {
        await exerciseService.unfavoriteExercise(exercise.id);
      } else {
        await exerciseService.favoriteExercise(exercise.id);
      }
      fetchExercises();
    } catch (err) {
      console.error('Error toggling favorite:', err);
      setNotification({
        open: true,
        message: err.message || 'Failed to update favorite status',
        severity: 'error'
      });
    }
  };

  const handleSave = async (exercise) => {
    try {
      if (exercise.is_saved) {
        await exerciseService.unsaveExercise(exercise.id);
      } else {
        await exerciseService.saveExercise(exercise.id);
      }
      fetchExercises();
    } catch (err) {
      console.error('Error toggling save:', err);
      setNotification({
        open: true,
        message: err.message || 'Failed to update save status',
        severity: 'error'
      });
    }
  };

  const handleDelete = async (exerciseId) => {
    if (window.confirm('Are you sure you want to delete this exercise?')) {
      try {
        await exerciseService.deleteExercise(exerciseId);
        setNotification({
          open: true,
          message: 'Exercise deleted successfully',
          severity: 'success'
        });
        fetchExercises();
      } catch (err) {
        console.error('Error deleting exercise:', err);
        setNotification({
          open: true,
          message: err.message || 'Failed to delete exercise',
          severity: 'error'
        });
      }
    }
  };

  // Notification handler
  const handleNotificationClose = () => {
    setNotification({ ...notification, open: false });
  };

  // Logout handler
  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  // Sidebar drawer content
  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap>
          Filters
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        <ListItem button onClick={() => handleViewModeChange('all')} selected={viewMode === 'all'}>
          <ListItemIcon>
            <DashboardIcon color={viewMode === 'all' ? 'primary' : 'inherit'} />
          </ListItemIcon>
          <ListItemText primary="All Exercises" />
        </ListItem>
        <ListItem button onClick={() => handleViewModeChange('my')} selected={viewMode === 'my'}>
          <ListItemIcon>
            <PersonOutlineIcon color={viewMode === 'my' ? 'primary' : 'inherit'} />
          </ListItemIcon>
          <ListItemText primary="My Exercises" />
        </ListItem>
        <ListItem button onClick={() => handleViewModeChange('favorites')} selected={viewMode === 'favorites'}>
          <ListItemIcon>
            <FavoriteIcon color={viewMode === 'favorites' ? 'primary' : 'inherit'} />
          </ListItemIcon>
          <ListItemText primary="Favorites" />
        </ListItem>
        <ListItem button onClick={() => handleViewModeChange('saved')} selected={viewMode === 'saved'}>
          <ListItemIcon>
            <BookmarkIcon color={viewMode === 'saved' ? 'primary' : 'inherit'} />
          </ListItemIcon>
          <ListItemText primary="Saved" />
        </ListItem>
      </List>
      <Divider />
      <List>
        <ListItem>
          <FormControlLabel
            control={
              <Switch
                checked={showOnlyPublic}
                onChange={(e) => setShowOnlyPublic(e.target.checked)}
              />
            }
            label="Public Only"
          />
        </ListItem>
        <ListItem>
          <FormControlLabel
            control={
              <Switch
                checked={sortByDifficulty}
                onChange={(e) => setSortByDifficulty(e.target.checked)}
              />
            }
            label="Sort by Difficulty"
          />
        </ListItem>
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <FilterAltIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1, display: 'flex', alignItems: 'center' }}>
            <FitnessCenterIcon sx={{ mr: 1 }} />
            Exercise Management
          </Typography>
          <Button 
            variant="contained" 
            color="secondary"
            startIcon={<AddIcon />}
            onClick={() => handleFormOpen()}
            sx={{ mr: 2 }}
          >
            New Exercise
          </Button>
          <Button 
            variant="outlined"
            color="inherit"
            onClick={handleLogout}
          >
            Logout
          </Button>
        </Toolbar>
        <Box sx={{ bgcolor: 'background.paper' }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            indicatorColor="primary"
            textColor="primary"
            centered
          >
            <Tab label="All Exercises" />
            <Tab label="My Exercises" />
          </Tabs>
        </Box>
      </AppBar>

      {/* Sidebar Drawer */}
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        sx={{
          display: { xs: 'block', sm: 'none' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
        }}
      >
        {drawer}
      </Drawer>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          flexShrink: 0,
          display: { xs: 'none', sm: 'block' },
          '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
        }}
      >
        {drawer}
      </Drawer>

      {/* Main Content */}
      <Box component="main" sx={{ 
        flexGrow: 1, 
        bgcolor: 'background.default',
        p: 3,
        width: { sm: `calc(100% - ${drawerWidth}px)` }, 
        ml: { sm: `${drawerWidth}px` },
        mt: '100px'
      }}>
        {/* Filter Controls */}
        <Paper sx={{ mb: 3, p: 2 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">
              {viewMode === 'all' && 'All Exercises'}
              {viewMode === 'my' && 'My Exercises'}
              {viewMode === 'favorites' && 'Favorite Exercises'}
              {viewMode === 'saved' && 'Saved Exercises'}
            </Typography>
            <TextField
              placeholder="Search by name..."
              size="small"
              value={nameFilter}
              onChange={(e) => setNameFilter(e.target.value)}
              sx={{ width: '250px' }}
            />
          </Box>
        </Paper>

        {/* Exercise List */}
        <Grid container spacing={3}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', width: '100%', mt: 4 }}>
              <CircularProgress />
            </Box>
          ) : error ? (
            <Box sx={{ width: '100%', mt: 2 }}>
              <Alert severity="error">{error}</Alert>
            </Box>
          ) : exercises.length === 0 ? (
            <Box sx={{ width: '100%', mt: 2, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary">No exercises found</Typography>
              <Button 
                variant="contained" 
                sx={{ mt: 2 }}
                startIcon={<AddIcon />}
                onClick={() => handleFormOpen()}
              >
                Create Your First Exercise
              </Button>
            </Box>
          ) : (
            exercises.map(exercise => (
              <Grid item xs={12} sm={6} md={4} key={exercise.id}>
                <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
                  <CardContent sx={{ flexGrow: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="h6" component="div">
                        {exercise.name}
                      </Typography>
                      <Chip 
                        label={exercise.is_public ? "Public" : "Private"} 
                        size="small"
                        color={exercise.is_public ? "success" : "default"}
                        variant="outlined"
                      />
                    </Box>
                    <Box sx={{ mb: 1.5 }}>
                      <Rating 
                        value={exercise.difficulty_level} 
                        readOnly 
                        max={5}
                        size="small"
                      />
                      <Typography variant="body2" color="text.secondary" component="span" sx={{ ml: 1 }}>
                        Difficulty: {exercise.difficulty_level}/5
                      </Typography>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                      {exercise.description}
                    </Typography>
                  </CardContent>
                  <Divider />
                  <CardActions sx={{ justifyContent: 'space-between', px: 2 }}>
                    <Box>
                      <IconButton 
                        size="small" 
                        onClick={() => handleFavorite(exercise)}
                        color={exercise.is_favorited ? "error" : "default"}
                      >
                        {exercise.is_favorited ? <FavoriteIcon /> : <FavoriteBorderIcon />}
                      </IconButton>
                      <IconButton 
                        size="small" 
                        onClick={() => handleSave(exercise)}
                        color={exercise.is_saved ? "primary" : "default"}
                      >
                        {exercise.is_saved ? <BookmarkIcon /> : <BookmarkBorderIcon />}
                      </IconButton>
                    </Box>
                    <Box>
                      <IconButton 
                        size="small" 
                        onClick={() => handleFormOpen(exercise)}
                      >
                        <EditIcon />
                      </IconButton>
                      <IconButton 
                        size="small" 
                        onClick={() => handleDelete(exercise.id)}
                        color="error"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Box>
                  </CardActions>
                </Card>
              </Grid>
            ))
          )}
        </Grid>

        {/* Exercise Form Dialog */}
        <Dialog open={formOpen} onClose={handleFormClose} maxWidth="sm" fullWidth>
          <DialogTitle>{formTitle}</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              id="name"
              label="Exercise Name"
              type="text"
              fullWidth
              variant="outlined"
              value={exerciseName}
              onChange={(e) => setExerciseName(e.target.value)}
              required
            />
            <TextField
              margin="dense"
              id="description"
              label="Description"
              type="text"
              fullWidth
              variant="outlined"
              multiline
              rows={3}
              value={exerciseDescription}
              onChange={(e) => setExerciseDescription(e.target.value)}
              required
            />
            <Box sx={{ mt: 2 }}>
              <Typography component="legend">Difficulty Level</Typography>
              <Rating
                name="difficulty"
                value={exerciseDifficulty}
                onChange={(event, newValue) => {
                  setExerciseDifficulty(newValue);
                }}
              />
            </Box>
            <FormControlLabel
              control={
                <Switch
                  checked={exerciseIsPublic}
                  onChange={(e) => setExerciseIsPublic(e.target.checked)}
                />
              }
              label="Public Exercise"
              sx={{ mt: 2 }}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleFormClose}>Cancel</Button>
            <Button 
              onClick={handleFormSubmit} 
              variant="contained"
              disabled={!exerciseName || !exerciseDescription}
            >
              Save
            </Button>
          </DialogActions>
        </Dialog>

        {/* Notification Snackbar */}
        <Snackbar
          open={notification.open}
          autoHideDuration={6000}
          onClose={handleNotificationClose}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert 
            onClose={handleNotificationClose} 
            severity={notification.severity} 
            sx={{ width: '100%' }}
          >
            {notification.message}
          </Alert>
        </Snackbar>
      </Box>
    </Box>
  );
};

export default ExerciseLandingPage; 