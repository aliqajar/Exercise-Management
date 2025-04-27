import { authService } from './auth';

/**
 * Service for exercise-related API calls
 */

// Get all exercises with optional filtering
const getExercises = async (filters = {}) => {
  // Build query string from filters
  const queryParams = new URLSearchParams();
  
  if (filters.name) queryParams.append('name', filters.name);
  if (filters.description) queryParams.append('description', filters.description);
  if (filters.difficulty_level) queryParams.append('difficulty_level', filters.difficulty_level);
  if (filters.sort_by_difficulty) queryParams.append('sort_by_difficulty', 'true');
  
  const queryString = queryParams.toString() ? `?${queryParams.toString()}` : '';
  
  try {
    const response = await authService.authFetch(`/exercises${queryString}`);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to fetch exercises');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error in getExercises:', error);
    throw error;
  }
};

// Get a single exercise by ID
const getExercise = async (id) => {
  try {
    const response = await authService.authFetch(`/exercises/${id}`);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Exercise not found');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error in getExercise:', error);
    throw error;
  }
};

// Get personal exercises (favorites or saved)
const getPersonalExercises = async (type = null) => {
  try {
    const queryString = type ? `?type=${type}` : '';
    const response = await authService.authFetch(`/exercises/personal${queryString}`);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to fetch personal exercises');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error in getPersonalExercises:', error);
    throw error;
  }
};

// Create a new exercise
const createExercise = async (exerciseData) => {
  try {
    console.log('Creating exercise with data:', JSON.stringify(exerciseData));
    
    const response = await authService.authFetch('/exercises', {
      method: 'POST',
      body: JSON.stringify(exerciseData),
    });
    
    console.log('Create exercise response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error response text:', errorText);
      
      const errorData = JSON.parse(errorText);
      throw new Error(errorData.detail || 'Failed to create exercise');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error in createExercise:', error);
    throw error;
  }
};

// Update an exercise
const updateExercise = async (id, exerciseData) => {
  try {
    // Ensure we're authenticated before making the request
    if (!authService.isAuthenticated()) {
      // Try to refresh the token first
      const refreshResult = await authService.refreshToken();
      if (!refreshResult) {
        throw new Error('Authentication required. Please log in again.');
      }
    }
    
    const response = await authService.authFetch(`/exercises/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(exerciseData),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to update exercise');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error in updateExercise:', error);
    
    // Special handling for auth-related errors
    if (error.message.includes('Authentication') || 
        error.message.includes('login again')) {
      // Force a new login
      authService.logout();
      throw new Error('Your session has expired. Please log in again.');
    }
    
    throw error;
  }
};

// Delete an exercise
const deleteExercise = async (id) => {
  try {
    const response = await authService.authFetch(`/exercises/${id}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to delete exercise');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error in deleteExercise:', error);
    throw error;
  }
};

// Favorite an exercise
const favoriteExercise = async (id) => {
  try {
    const response = await authService.authFetch(`/exercises/${id}/favorite`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to favorite exercise');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error in favoriteExercise:', error);
    throw error;
  }
};

// Unfavorite an exercise
const unfavoriteExercise = async (id) => {
  try {
    const response = await authService.authFetch(`/exercises/${id}/favorite`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to unfavorite exercise');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error in unfavoriteExercise:', error);
    throw error;
  }
};

// Save an exercise
const saveExercise = async (id) => {
  try {
    const response = await authService.authFetch(`/exercises/${id}/save`, {
      method: 'POST',
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to save exercise');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error in saveExercise:', error);
    throw error;
  }
};

// Unsave an exercise
const unsaveExercise = async (id) => {
  try {
    const response = await authService.authFetch(`/exercises/${id}/save`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to unsave exercise');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error in unsaveExercise:', error);
    throw error;
  }
};

// Rate an exercise
const rateExercise = async (id, rating) => {
  try {
    const response = await authService.authFetch(`/exercises/${id}/rate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ value: rating }),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to rate exercise');
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error in rateExercise:', error);
    throw error;
  }
};

export const exerciseService = {
  getExercises,
  getExercise,
  getPersonalExercises,
  createExercise,
  updateExercise,
  deleteExercise,
  favoriteExercise,
  unfavoriteExercise,
  saveExercise,
  unsaveExercise,
  rateExercise,
}; 