import React, { useState } from 'react';
import { 
  Box, 
  AppBar, 
  Toolbar, 
  Typography, 
  Drawer, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText, 
  IconButton,
  Container,
  Button,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Snackbar,
  Alert
} from '@mui/material';
import FitnessCenterIcon from '@mui/icons-material/FitnessCenter';
import MenuIcon from '@mui/icons-material/Menu';
import StarIcon from '@mui/icons-material/Star';
import BookmarkIcon from '@mui/icons-material/Bookmark';
import PersonIcon from '@mui/icons-material/Person';
import LogoutIcon from '@mui/icons-material/Logout';
import AddIcon from '@mui/icons-material/Add';
import ExerciseList from '../components/ExerciseList';
import ExerciseForm from '../components/ExerciseForm';
import { authService } from '../services/auth';
import { useNavigate } from 'react-router-dom';

// Set drawer width
const drawerWidth = 240;

const DashboardPage = () => {
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [anchorEl, setAnchorEl] = useState(null);
  const [formOpen, setFormOpen] = useState(false);
  const [editExerciseId, setEditExerciseId] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [refreshKey, setRefreshKey] = useState(0); // Used to trigger refetch in ExerciseList
  
  const open = Boolean(anchorEl);

  // Handle drawer toggle
  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  // Handle user menu open
  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  // Handle user menu close
  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  // Handle logout
  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  // Tab selection handler
  const handleTabChange = (tab) => {
    setActiveTab(tab);
    setMobileOpen(false);
  };

  // Open exercise form for creating a new exercise
  const handleNewExercise = () => {
    setEditExerciseId(null);
    setFormOpen(true);
  };

  // Open exercise form for editing
  const handleEditExercise = (exerciseId) => {
    setEditExerciseId(exerciseId);
    setFormOpen(true);
  };

  // Close exercise form
  const handleFormClose = () => {
    setFormOpen(false);
  };

  // Handle exercise saved (created or updated)
  const handleExerciseSaved = (exercise) => {
    // Show success notification
    setNotification({
      open: true,
      message: `Exercise ${editExerciseId ? 'updated' : 'created'} successfully`,
      severity: 'success'
    });
    
    // Refresh exercise list
    setRefreshKey(prevKey => prevKey + 1);
  };

  // Handle notification close
  const handleNotificationClose = () => {
    setNotification({ ...notification, open: false });
  };

  // Create drawer content
  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Exercise Manager
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        <ListItem 
          button 
          selected={activeTab === 'all'} 
          onClick={() => handleTabChange('all')}
        >
          <ListItemIcon>
            <FitnessCenterIcon color={activeTab === 'all' ? 'primary' : 'inherit'} />
          </ListItemIcon>
          <ListItemText primary="All Exercises" />
        </ListItem>
        <ListItem 
          button 
          selected={activeTab === 'my'} 
          onClick={() => handleTabChange('my')}
        >
          <ListItemIcon>
            <PersonIcon color={activeTab === 'my' ? 'primary' : 'inherit'} />
          </ListItemIcon>
          <ListItemText primary="My Exercises" />
        </ListItem>
        <ListItem 
          button 
          selected={activeTab === 'favorites'} 
          onClick={() => handleTabChange('favorites')}
        >
          <ListItemIcon>
            <StarIcon color={activeTab === 'favorites' ? 'primary' : 'inherit'} />
          </ListItemIcon>
          <ListItemText primary="Favorites" />
        </ListItem>
        <ListItem 
          button 
          selected={activeTab === 'saved'} 
          onClick={() => handleTabChange('saved')}
        >
          <ListItemIcon>
            <BookmarkIcon color={activeTab === 'saved' ? 'primary' : 'inherit'} />
          </ListItemIcon>
          <ListItemText primary="Saved" />
        </ListItem>
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {activeTab === 'all' && 'All Exercises'}
            {activeTab === 'my' && 'My Exercises'}
            {activeTab === 'favorites' && 'Favorite Exercises'}
            {activeTab === 'saved' && 'Saved Exercises'}
          </Typography>
          <Button 
            variant="contained" 
            color="secondary" 
            sx={{ mr: 2 }}
            startIcon={<AddIcon />}
            onClick={handleNewExercise}
          >
            New Exercise
          </Button>
          <IconButton
            onClick={handleMenuOpen}
            size="small"
            sx={{ ml: 2 }}
          >
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
              <PersonIcon />
            </Avatar>
          </IconButton>
          <Menu
            anchorEl={anchorEl}
            open={open}
            onClose={handleMenuClose}
            onClick={handleMenuClose}
          >
            <MenuItem onClick={handleLogout}>
              <ListItemIcon>
                <LogoutIcon fontSize="small" />
              </ListItemIcon>
              <ListItemText>Logout</ListItemText>
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      {/* Sidebar Drawer */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        
        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main content */}
      <Box
        component="main"
        sx={{ 
          flexGrow: 1, 
          p: 3, 
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: '64px'
        }}
      >
        <Container maxWidth="xl">
          <ExerciseList 
            key={refreshKey}
            tabType={activeTab} 
            onEditExercise={handleEditExercise} 
          />
        </Container>
      </Box>

      {/* Exercise Form Dialog */}
      <ExerciseForm
        open={formOpen}
        onClose={handleFormClose}
        exerciseId={editExerciseId}
        onSaved={handleExerciseSaved}
      />

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
  );
};

export default DashboardPage; 