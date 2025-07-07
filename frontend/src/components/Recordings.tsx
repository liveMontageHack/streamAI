import React, { useState, useEffect } from 'react';
import { 
  Video, 
  Play, 
  Edit3, 
  Download, 
  Share2, 
  Trash2, 
  Clock, 
  Eye, 
  MessageCircle,
  Scissors,
  Wand2,
  FileText,
  Sparkles,
  Calendar,
  Filter,
  Search,
  MoreVertical,
  ChevronDown,
  Upload,
  Image,
  X,
  Plus,
  Pause,
  SkipBack,
  SkipForward,
  Volume2,
  Maximize,
  Settings,
  Tag,
  Check,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { videoProcessingAPI, TaskStatus, UploadOptions } from '../services/videoProcessingAPI';
import { recordingsService } from '../services/recordingsService';
import { Recording } from '../types/Recording';
import ProcessingProgress from './ProcessingProgress';
import ProcessedResults from './ProcessedResults';

const Recordings: React.FC = () => {
  const [recordings, setRecordings] = useState<Recording[]>([]);
  const [isLoadingRecordings, setIsLoadingRecordings] = useState(true);

  const [selectedRecording, setSelectedRecording] = useState<Recording | null>(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterCategory, setFilterCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showVideoPlayer, setShowVideoPlayer] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  // AutoMontage states
  const [processingStates, setProcessingStates] = useState<Record<string, {
    isProcessing: boolean;
    taskStatus: TaskStatus | null;
    uploadProgress: number;
    estimatedTime?: string;
    showProgress: boolean;
    showResults: boolean;
    stopPolling?: () => void;
  }>>({});
  const [apiConnected, setApiConnected] = useState<boolean | null>(null);

  // Upload form state
  const [uploadForm, setUploadForm] = useState({
    title: '',
    categories: [] as string[],
    thumbnail: '',
    file: null as File | null
  });

  const [availableCategories] = useState([
    'Gaming', 'Just Chatting', 'Music', 'Art', 'Programming', 'Education', 
    'Sports', 'Travel & Outdoors', 'Food & Drink', 'Science & Technology',
    'Politics', 'ASMR', 'Fitness & Health', 'Beauty & Makeup', 'Entertainment',
    'Community', 'Technology'
  ]);

  const [thumbnailOptions] = useState([
    'https://images.pexels.com/photos/442576/pexels-photo-442576.jpeg?auto=compress&cs=tinysrgb&w=400',
    'https://images.pexels.com/photos/1181673/pexels-photo-1181673.jpeg?auto=compress&cs=tinysrgb&w=400',
    'https://images.pexels.com/photos/1181677/pexels-photo-1181677.jpeg?auto=compress&cs=tinysrgb&w=400',
    'https://images.pexels.com/photos/1181244/pexels-photo-1181244.jpeg?auto=compress&cs=tinysrgb&w=400',
    'https://images.pexels.com/photos/1181316/pexels-photo-1181316.jpeg?auto=compress&cs=tinysrgb&w=400',
    'https://images.pexels.com/photos/1181406/pexels-photo-1181406.jpeg?auto=compress&cs=tinysrgb&w=400'
  ]);

  const getAllCategories = () => {
    const recordingCategories = recordings.flatMap(r => r.categories);
    return [...new Set([...availableCategories, ...recordingCategories])];
  };

  const filteredRecordings = recordings.filter(recording => {
    const matchesSearch = recording.title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === 'all' || recording.status === filterStatus;
    const matchesCategory = filterCategory === 'all' || recording.categories.includes(filterCategory);
    return matchesSearch && matchesStatus && matchesCategory;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready': return 'bg-green-600/20 text-green-400';
      case 'processing': return 'bg-yellow-600/20 text-yellow-400';
      case 'editing': return 'bg-blue-600/20 text-blue-400';
      default: return 'bg-gray-600/20 text-gray-400';
    }
  };

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case 'Twitch': return 'bg-purple-600/20 text-purple-400';
      case 'YouTube': return 'bg-red-600/20 text-red-400';
      case 'Discord': return 'bg-blue-600/20 text-blue-400';
      default: return 'bg-gray-600/20 text-gray-400';
    }
  };

  const handleCategoryToggle = (category: string) => {
    setUploadForm(prev => ({
      ...prev,
      categories: prev.categories.includes(category)
        ? prev.categories.filter(c => c !== category)
        : [...prev.categories, category]
    }));
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadForm(prev => ({ ...prev, file }));
    }
  };

  const handleUploadSubmit = () => {
    if (uploadForm.title && uploadForm.file) {
      const newRecording: Recording = {
        id: Date.now().toString(),
        title: uploadForm.title,
        date: new Date().toISOString().split('T')[0],
        duration: '0:00:00',
        size: `${(uploadForm.file.size / (1024 * 1024 * 1024)).toFixed(1)} GB`,
        views: 0,
        thumbnail: uploadForm.thumbnail || thumbnailOptions[0],
        platforms: ['Manual Upload'],
        status: 'processing',
        hasTranscription: false,
        hasHighlights: false,
        hasShorts: false,
        categories: uploadForm.categories,
        isManualUpload: true
      };

      setRecordings(prev => [newRecording, ...prev]);
      setUploadForm({ title: '', categories: [], thumbnail: '', file: null });
      setShowUploadModal(false);
    }
  };

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Load recordings on component mount
  useEffect(() => {
    const loadRecordings = async () => {
      try {
        setIsLoadingRecordings(true);
        const realRecordings = await recordingsService.getRecordings();
        setRecordings(realRecordings);
      } catch (error) {
        console.error('Failed to load recordings:', error);
        // Keep demo recordings if API fails
      } finally {
        setIsLoadingRecordings(false);
      }
    };

    loadRecordings();
  }, []);

  // AutoMontage functions
  React.useEffect(() => {
    // Test API connection on component mount
    const testConnection = async () => {
      try {
        const connected = await videoProcessingAPI.testConnection();
        setApiConnected(connected);
      } catch (error) {
        console.error('Failed to test API connection:', error);
        setApiConnected(false);
      }
    };

    testConnection();
  }, []);

  const handleAutoMontage = async (recording: Recording) => {
    if (!recording) return;

    // Check if already processing
    if (processingStates[recording.id]?.isProcessing) {
      return;
    }

    // For demo purposes, we'll simulate uploading the video file
    // In a real scenario, you'd need to get the actual video file
    const demoVideoFile = new File(['demo video content'], `${recording.title}.mp4`, {
      type: 'video/mp4'
    });

    try {
      // Initialize processing state
      setProcessingStates(prev => ({
        ...prev,
        [recording.id]: {
          isProcessing: true,
          taskStatus: null,
          uploadProgress: 0,
          estimatedTime: videoProcessingAPI.estimateProcessingTime(demoVideoFile.size),
          showProgress: true,
          showResults: false
        }
      }));

      // Simulate upload progress
      const uploadInterval = setInterval(() => {
        setProcessingStates(prev => {
          const current = prev[recording.id];
          if (!current || current.uploadProgress >= 100) {
            clearInterval(uploadInterval);
            return prev;
          }
          return {
            ...prev,
            [recording.id]: {
              ...current,
              uploadProgress: Math.min(current.uploadProgress + 10, 100)
            }
          };
        });
      }, 200);

      // Upload video for processing
      const uploadResponse = await videoProcessingAPI.uploadVideoForProcessing(demoVideoFile, {
        subtitle_model: 'base',
        priority: 1
      });

      clearInterval(uploadInterval);

      // Update state with upload response
      setProcessingStates(prev => ({
        ...prev,
        [recording.id]: {
          ...prev[recording.id],
          uploadProgress: 100,
          taskStatus: {
            task_id: uploadResponse.task_id,
            status: 'uploaded',
            filename: uploadResponse.filename,
            size: uploadResponse.size,
            config: uploadResponse.config
          } as TaskStatus
        }
      }));

      // Start polling for progress
      const stopPolling = await videoProcessingAPI.pollTaskProgress(
        uploadResponse.task_id,
        // onProgress
        (status: TaskStatus) => {
          setProcessingStates(prev => ({
            ...prev,
            [recording.id]: {
              ...prev[recording.id],
              taskStatus: status
            }
          }));
        },
        // onComplete
        (status: TaskStatus) => {
          setProcessingStates(prev => ({
            ...prev,
            [recording.id]: {
              ...prev[recording.id],
              isProcessing: false,
              taskStatus: status,
              showProgress: false,
              showResults: true
            }
          }));

          // Update recording to show it has highlights
          setRecordings(prevRecordings => 
            prevRecordings.map(r => 
              r.id === recording.id 
                ? { ...r, hasHighlights: true, hasTranscription: true }
                : r
            )
          );
        },
        // onError
        (error: Error) => {
          console.error('Processing error:', error);
          setProcessingStates(prev => ({
            ...prev,
            [recording.id]: {
              ...prev[recording.id],
              isProcessing: false,
              taskStatus: {
                task_id: uploadResponse.task_id,
                status: 'error',
                message: error.message
              } as TaskStatus
            }
          }));
        }
      );

      // Store stop polling function
      setProcessingStates(prev => ({
        ...prev,
        [recording.id]: {
          ...prev[recording.id],
          stopPolling
        }
      }));

    } catch (error) {
      console.error('AutoMontage error:', error);
      setProcessingStates(prev => ({
        ...prev,
        [recording.id]: {
          isProcessing: false,
          taskStatus: {
            task_id: '',
            status: 'error',
            message: error instanceof Error ? error.message : 'Unknown error'
          } as TaskStatus,
          uploadProgress: 0,
          showProgress: false,
          showResults: false
        }
      }));
    }
  };

  const handleCancelProcessing = (recordingId: string) => {
    const processingState = processingStates[recordingId];
    if (processingState?.stopPolling) {
      processingState.stopPolling();
    }

    setProcessingStates(prev => ({
      ...prev,
      [recordingId]: {
        ...prev[recordingId],
        isProcessing: false,
        showProgress: false
      }
    }));
  };

  const handleCloseProgress = (recordingId: string) => {
    setProcessingStates(prev => ({
      ...prev,
      [recordingId]: {
        ...prev[recordingId],
        showProgress: false
      }
    }));
  };

  const handleCloseResults = (recordingId: string) => {
    setProcessingStates(prev => ({
      ...prev,
      [recordingId]: {
        ...prev[recordingId],
        showResults: false
      }
    }));
  };

  const getAutoMontageButtonState = (recording: Recording) => {
    const processingState = processingStates[recording.id];
    
    if (processingState?.isProcessing) {
      return {
        text: 'Traitement...',
        disabled: true,
        icon: <Loader2 className="w-4 h-4 animate-spin" />
      };
    }
    
    if (processingState?.taskStatus?.status === 'completed' || processingState?.taskStatus?.status === 'completed_simple') {
      return {
        text: 'Voir résultats',
        disabled: false,
        icon: <Check className="w-4 h-4" />
      };
    }
    
    if (recording.hasHighlights) {
      return {
        text: 'Régénérer',
        disabled: false,
        icon: <Scissors className="w-4 h-4" />
      };
    }
    
    return {
      text: 'Lancer AutoMontage',
      disabled: apiConnected === false,
      icon: <Scissors className="w-4 h-4" />
    };
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Recordings</h2>
          <p className="text-gray-400">Manage and edit your recorded streams with AI-powered tools</p>
        </div>
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setShowUploadModal(true)}
            className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2"
          >
            <Upload className="w-5 h-5" />
            <span>Upload Video</span>
          </button>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search recordings..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-white/10 border border-white/20 text-white pl-10 pr-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 w-64"
            />
          </div>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="bg-white/10 border border-white/20 text-white px-4 py-2 rounded-lg hover:bg-white/20 transition-all duration-200 flex items-center space-x-2"
          >
            <Filter className="w-4 h-4" />
            <span>Filters</span>
            <ChevronDown className={`w-4 h-4 transition-transform duration-200 ${showFilters ? 'rotate-180' : ''}`} />
          </button>
        </div>
      </div>

      {/* Enhanced Filters */}
      {showFilters && (
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-white font-medium mb-4">Filter by Status</h3>
              <div className="flex flex-wrap gap-2">
                {['all', 'ready', 'processing', 'editing'].map((status) => (
                  <button
                    key={status}
                    onClick={() => setFilterStatus(status)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      filterStatus === status
                        ? 'bg-purple-600 text-white'
                        : 'bg-white/10 text-gray-400 hover:bg-white/20 hover:text-white'
                    }`}
                  >
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <h3 className="text-white font-medium mb-4">Filter by Category</h3>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setFilterCategory('all')}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    filterCategory === 'all'
                      ? 'bg-purple-600 text-white'
                      : 'bg-white/10 text-gray-400 hover:bg-white/20 hover:text-white'
                  }`}
                >
                  All Categories
                </button>
                {getAllCategories().slice(0, 6).map((category) => (
                  <button
                    key={category}
                    onClick={() => setFilterCategory(category)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                      filterCategory === category
                        ? 'bg-purple-600 text-white'
                        : 'bg-white/10 text-gray-400 hover:bg-white/20 hover:text-white'
                    }`}
                  >
                    {category}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Recordings Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredRecordings.map((recording) => (
          <div key={recording.id} className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl overflow-hidden hover:bg-white/15 transition-all duration-200">
            {/* Thumbnail */}
            <div className="relative">
              <img 
                src={recording.thumbnail} 
                alt={recording.title}
                className="w-full h-48 object-cover"
              />
              <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity duration-200">
                <button 
                  onClick={() => {
                    setSelectedRecording(recording);
                    setShowVideoPlayer(true);
                  }}
                  className="bg-white/20 backdrop-blur-md border border-white/30 text-white p-3 rounded-full hover:bg-white/30 transition-all duration-200"
                >
                  <Play className="w-6 h-6" />
                </button>
              </div>
              <div className="absolute bottom-2 right-2 bg-black/70 text-white px-2 py-1 rounded text-sm">
                {recording.duration}
              </div>
              <div className={`absolute top-2 left-2 px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(recording.status)}`}>
                {recording.status.charAt(0).toUpperCase() + recording.status.slice(1)}
              </div>
              {recording.isManualUpload && (
                <div className="absolute top-2 right-2 bg-blue-600/80 text-white px-2 py-1 rounded-full text-xs font-medium">
                  Manual Upload
                </div>
              )}
            </div>

            {/* Content */}
            <div className="p-6">
              <h3 className="text-white font-semibold mb-2 line-clamp-2">{recording.title}</h3>
              
              <div className="flex items-center space-x-4 text-sm text-gray-400 mb-4">
                <div className="flex items-center space-x-1">
                  <Calendar className="w-4 h-4" />
                  <span>{new Date(recording.date).toLocaleDateString()}</span>
                </div>
                <div className="flex items-center space-x-1">
                  <Eye className="w-4 h-4" />
                  <span>{recording.views}</span>
                </div>
              </div>

              {/* Categories */}
              <div className="flex flex-wrap gap-1 mb-3">
                {recording.categories.map((category) => (
                  <span key={category} className="bg-orange-600/20 text-orange-400 px-2 py-1 rounded-full text-xs">
                    {category}
                  </span>
                ))}
              </div>

              {/* Platforms */}
              <div className="flex flex-wrap gap-1 mb-4">
                {recording.platforms.map((platform) => (
                  <span key={platform} className={`px-2 py-1 rounded-full text-xs ${getPlatformColor(platform)}`}>
                    {platform}
                  </span>
                ))}
              </div>

              {/* AI Features Status */}
              <div className="grid grid-cols-3 gap-2 mb-4">
                <div className={`flex items-center space-x-1 text-xs p-2 rounded-lg ${recording.hasTranscription ? 'bg-green-600/20 text-green-400' : 'bg-gray-600/20 text-gray-400'}`}>
                  <FileText className="w-3 h-3" />
                  <span>Transcript</span>
                </div>
                <div className={`flex items-center space-x-1 text-xs p-2 rounded-lg ${recording.hasHighlights ? 'bg-purple-600/20 text-purple-400' : 'bg-gray-600/20 text-gray-400'}`}>
                  <Sparkles className="w-3 h-3" />
                  <span>Highlights</span>
                </div>
                <div className={`flex items-center space-x-1 text-xs p-2 rounded-lg ${recording.hasShorts ? 'bg-orange-600/20 text-orange-400' : 'bg-gray-600/20 text-gray-400'}`}>
                  <Scissors className="w-3 h-3" />
                  <span>Shorts</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between">
                <button
                  onClick={() => setSelectedRecording(recording)}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2"
                >
                  <Edit3 className="w-4 h-4" />
                  <span>Edit</span>
                </button>
                <div className="flex items-center space-x-2">
                  <button className="bg-white/10 hover:bg-white/20 border border-white/20 text-white p-2 rounded-lg transition-all duration-200">
                    <Download className="w-4 h-4" />
                  </button>
                  <button className="bg-white/10 hover:bg-white/20 border border-white/20 text-white p-2 rounded-lg transition-all duration-200">
                    <Share2 className="w-4 h-4" />
                  </button>
                  <button className="bg-white/10 hover:bg-white/20 border border-white/20 text-white p-2 rounded-lg transition-all duration-200">
                    <MoreVertical className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-6">
          <div className="bg-gray-900/95 backdrop-blur-md border border-white/20 rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-white">Upload Video</h3>
                <button
                  onClick={() => setShowUploadModal(false)}
                  className="bg-white/10 hover:bg-white/20 border border-white/20 text-white p-2 rounded-lg transition-all duration-200"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="space-y-6">
                {/* File Upload */}
                <div>
                  <label className="block text-white font-medium mb-2">Video File</label>
                  <div className="border-2 border-dashed border-white/20 rounded-xl p-8 text-center hover:border-white/40 transition-all duration-200">
                    <input
                      type="file"
                      accept="video/*"
                      onChange={handleFileUpload}
                      className="hidden"
                      id="video-upload"
                    />
                    <label htmlFor="video-upload" className="cursor-pointer">
                      <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <p className="text-white mb-2">
                        {uploadForm.file ? uploadForm.file.name : 'Click to upload or drag and drop'}
                      </p>
                      <p className="text-gray-400 text-sm">MP4, MOV, AVI up to 10GB</p>
                    </label>
                  </div>
                </div>

                {/* Title */}
                <div>
                  <label className="block text-white font-medium mb-2">Title</label>
                  <input
                    type="text"
                    value={uploadForm.title}
                    onChange={(e) => setUploadForm(prev => ({ ...prev, title: e.target.value }))}
                    placeholder="Enter video title..."
                    className="w-full bg-white/5 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                </div>

                {/* Categories */}
                <div>
                  <label className="block text-white font-medium mb-2">Categories</label>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {uploadForm.categories.map((category) => (
                      <span key={category} className="bg-purple-600/20 text-purple-400 px-3 py-1 rounded-full text-sm flex items-center space-x-2">
                        <span>{category}</span>
                        <button
                          onClick={() => handleCategoryToggle(category)}
                          className="hover:text-red-400 transition-colors duration-200"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    {availableCategories.filter(cat => !uploadForm.categories.includes(cat)).slice(0, 9).map((category) => (
                      <button
                        key={category}
                        onClick={() => handleCategoryToggle(category)}
                        className="bg-white/10 hover:bg-white/20 border border-white/20 text-white px-3 py-2 rounded-lg text-sm transition-all duration-200"
                      >
                        {category}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Thumbnail Selection */}
                <div>
                  <label className="block text-white font-medium mb-2">Choose Thumbnail</label>
                  <div className="grid grid-cols-3 gap-4">
                    {thumbnailOptions.map((thumb, index) => (
                      <button
                        key={index}
                        onClick={() => setUploadForm(prev => ({ ...prev, thumbnail: thumb }))}
                        className={`relative rounded-lg overflow-hidden border-2 transition-all duration-200 ${
                          uploadForm.thumbnail === thumb
                            ? 'border-purple-500 ring-2 ring-purple-500/50'
                            : 'border-white/20 hover:border-white/40'
                        }`}
                      >
                        <img src={thumb} alt={`Thumbnail ${index + 1}`} className="w-full h-20 object-cover" />
                        {uploadForm.thumbnail === thumb && (
                          <div className="absolute inset-0 bg-purple-500/20 flex items-center justify-center">
                            <Check className="w-6 h-6 text-white" />
                          </div>
                        )}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Submit Button */}
                <div className="flex items-center justify-end space-x-4 pt-6 border-t border-white/10">
                  <button
                    onClick={() => setShowUploadModal(false)}
                    className="bg-white/10 hover:bg-white/20 border border-white/20 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleUploadSubmit}
                    disabled={!uploadForm.title || !uploadForm.file}
                    className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-8 py-3 rounded-lg font-medium transition-all duration-200"
                  >
                    Upload Video
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Video Player with Timeline */}
      {showVideoPlayer && selectedRecording && (
        <div className="fixed inset-0 bg-black/90 backdrop-blur-sm z-50 flex items-center justify-center p-6">
          <div className="bg-gray-900/95 backdrop-blur-md border border-white/20 rounded-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-white">{selectedRecording.title}</h3>
                <button
                  onClick={() => setShowVideoPlayer(false)}
                  className="bg-white/10 hover:bg-white/20 border border-white/20 text-white p-2 rounded-lg transition-all duration-200"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Video Player */}
              <div className="relative bg-black rounded-xl overflow-hidden mb-6">
                <video 
                  controls
                  className="w-full h-96 object-contain"
                  src={`http://localhost:5001/api/recordings/${selectedRecording.id}/file`}
                  poster={selectedRecording.thumbnail}
                  onLoadedMetadata={(e) => {
                    const video = e.target as HTMLVideoElement;
                    console.log('Video duration:', video.duration);
                  }}
                >
                  Votre navigateur ne supporte pas la lecture vidéo.
                </video>
                
                {/* Video Controls Overlay */}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
                  <div className="flex items-center space-x-4 text-white">
                    <button className="hover:text-purple-400 transition-colors duration-200">
                      <SkipBack className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => setIsPlaying(!isPlaying)}
                      className="hover:text-purple-400 transition-colors duration-200"
                    >
                      {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
                    </button>
                    <button className="hover:text-purple-400 transition-colors duration-200">
                      <SkipForward className="w-5 h-5" />
                    </button>
                    <div className="flex items-center space-x-2">
                      <Volume2 className="w-4 h-4" />
                      <div className="w-20 h-1 bg-white/30 rounded-full">
                        <div className="w-3/4 h-full bg-white rounded-full"></div>
                      </div>
                    </div>
                    <span className="text-sm">{formatTime(currentTime)} / {selectedRecording.duration}</span>
                    <div className="flex-1"></div>
                    <button className="hover:text-purple-400 transition-colors duration-200">
                      <Settings className="w-5 h-5" />
                    </button>
                    <button className="hover:text-purple-400 transition-colors duration-200">
                      <Maximize className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Timeline */}
              <div className="bg-white/5 border border-white/10 rounded-xl p-6 mb-6">
                <h4 className="text-white font-medium mb-4 flex items-center space-x-2">
                  <Clock className="w-5 h-5" />
                  <span>Video Timeline</span>
                </h4>
                
                {/* Timeline Bar */}
                <div className="relative mb-4">
                  <div className="w-full h-2 bg-white/20 rounded-full">
                    <div 
                      className="h-full bg-gradient-to-r from-purple-600 to-blue-600 rounded-full transition-all duration-200"
                      style={{ width: `${(currentTime / 9252) * 100}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-xs text-gray-400 mt-2">
                    <span>0:00</span>
                    <span>30:00</span>
                    <span>1:00:00</span>
                    <span>1:30:00</span>
                    <span>2:00:00</span>
                    <span>2:34:12</span>
                  </div>
                </div>

                {/* Timeline Markers */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all duration-200 cursor-pointer">
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-white text-sm">Stream Start</span>
                    </div>
                    <span className="text-gray-400 text-sm">0:00:00</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all duration-200 cursor-pointer">
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                      <span className="text-white text-sm">High Engagement Moment</span>
                    </div>
                    <span className="text-gray-400 text-sm">0:24:15</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all duration-200 cursor-pointer">
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                      <span className="text-white text-sm">Highlight Clip</span>
                    </div>
                    <span className="text-gray-400 text-sm">1:12:30</span>
                  </div>
                  <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-all duration-200 cursor-pointer">
                    <div className="flex items-center space-x-3">
                      <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                      <span className="text-white text-sm">Peak Viewers</span>
                    </div>
                    <span className="text-gray-400 text-sm">1:45:22</span>
                  </div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <button className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2">
                    <Scissors className="w-4 h-4" />
                    <span>Create Clip</span>
                  </button>
                  <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2">
                    <Sparkles className="w-4 h-4" />
                    <span>AI Highlights</span>
                  </button>
                  <button className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2">
                    <FileText className="w-4 h-4" />
                    <span>Transcription</span>
                  </button>
                </div>
                <button
                  onClick={() => setShowVideoPlayer(false)}
                  className="bg-white/10 hover:bg-white/20 border border-white/20 text-white px-6 py-2 rounded-lg font-medium transition-all duration-200"
                >
                  Close Player
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal (existing code) */}
      {selectedRecording && !showVideoPlayer && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-6">
          <div className="bg-gray-900/95 backdrop-blur-md border border-white/20 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-8">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-2xl font-bold text-white">Edit Recording</h3>
                <button
                  onClick={() => setSelectedRecording(null)}
                  className="bg-white/10 hover:bg-white/20 border border-white/20 text-white p-2 rounded-lg transition-all duration-200"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Video Preview */}
                <div className="space-y-6">
                  <div className="relative">
                    <img 
                      src={selectedRecording.thumbnail} 
                      alt={selectedRecording.title}
                      className="w-full h-64 object-cover rounded-xl"
                    />
                    <div className="absolute inset-0 bg-black/40 flex items-center justify-center rounded-xl">
                      <button 
                        onClick={() => setShowVideoPlayer(true)}
                        className="bg-white/20 backdrop-blur-md border border-white/30 text-white p-4 rounded-full hover:bg-white/30 transition-all duration-200"
                      >
                        <Play className="w-8 h-8" />
                      </button>
                    </div>
                  </div>

                  <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                    <h4 className="text-white font-medium mb-2">Recording Details</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Duration:</span>
                        <span className="text-white">{selectedRecording.duration}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Size:</span>
                        <span className="text-white">{selectedRecording.size}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Views:</span>
                        <span className="text-white">{selectedRecording.views}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Date:</span>
                        <span className="text-white">{new Date(selectedRecording.date).toLocaleDateString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Categories:</span>
                        <div className="flex flex-wrap gap-1">
                          {selectedRecording.categories.map((cat) => (
                            <span key={cat} className="bg-orange-600/20 text-orange-400 px-2 py-1 rounded-full text-xs">
                              {cat}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* AI Tools */}
                <div className="space-y-6">
                  <h4 className="text-xl font-semibold text-white flex items-center space-x-2">
                    <Wand2 className="w-5 h-5" />
                    <span>AI-Powered Tools</span>
                  </h4>

                  {/* Auto Montage */}
                  <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
                          <Scissors className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <h5 className="text-white font-medium">Automatic Montage</h5>
                          <p className="text-gray-400 text-sm">AI creates highlight reels automatically</p>
                        </div>
                      </div>
                      <button 
                        onClick={() => {
                          const buttonState = getAutoMontageButtonState(selectedRecording);
                          if (buttonState.text === 'Voir résultats') {
                            setProcessingStates(prev => ({
                              ...prev,
                              [selectedRecording.id]: {
                                ...prev[selectedRecording.id],
                                showResults: true
                              }
                            }));
                          } else {
                            handleAutoMontage(selectedRecording);
                          }
                        }}
                        disabled={getAutoMontageButtonState(selectedRecording).disabled}
                        className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 flex items-center space-x-2"
                      >
                        {getAutoMontageButtonState(selectedRecording).icon}
                        <span>{getAutoMontageButtonState(selectedRecording).text}</span>
                      </button>
                    </div>
                    <div className="text-gray-400 text-sm">
                      Status: {(() => {
                        const processingState = processingStates[selectedRecording.id];
                        if (processingState?.isProcessing) return 'Traitement en cours...';
                        if (processingState?.taskStatus?.status === 'completed' || processingState?.taskStatus?.status === 'completed_simple') return 'Traitement terminé';
                        if (processingState?.taskStatus?.status === 'error') return 'Erreur de traitement';
                        if (selectedRecording.hasHighlights) return 'Ready';
                        if (apiConnected === false) return 'API non disponible';
                        return 'Not generated';
                      })()}
                    </div>
                    {apiConnected === false && (
                      <div className="mt-2 p-2 bg-red-600/10 border border-red-600/20 rounded-lg">
                        <div className="flex items-center space-x-2">
                          <AlertCircle className="w-4 h-4 text-red-400" />
                          <span className="text-red-400 text-xs">Impossible de se connecter à l'API de traitement vidéo</span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Transcription */}
                  <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-lg flex items-center justify-center">
                          <FileText className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <h5 className="text-white font-medium">AI Transcription</h5>
                          <p className="text-gray-400 text-sm">Full transcript with subtitles</p>
                        </div>
                      </div>
                      <button className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200">
                        {selectedRecording.hasTranscription ? 'View' : 'Generate'}
                      </button>
                    </div>
                    <div className="text-gray-400 text-sm">
                      Status: {selectedRecording.hasTranscription ? 'Complete with subtitles' : 'Not generated'}
                    </div>
                  </div>

                  {/* Short Clips */}
                  <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-r from-orange-600 to-red-600 rounded-lg flex items-center justify-center">
                          <Sparkles className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <h5 className="text-white font-medium">Best Moments Shorts</h5>
                          <p className="text-gray-400 text-sm">AI extracts viral-worthy clips</p>
                        </div>
                      </div>
                      <button className="bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200">
                        Create Shorts
                      </button>
                    </div>
                    <div className="text-gray-400 text-sm">
                      Status: {selectedRecording.hasShorts ? '5 shorts generated' : 'Not generated'}
                    </div>
                  </div>

                  {/* Manual Editing */}
                  <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gradient-to-r from-green-600 to-teal-600 rounded-lg flex items-center justify-center">
                          <Edit3 className="w-5 h-5 text-white" />
                        </div>
                        <div>
                          <h5 className="text-white font-medium">Manual Editor</h5>
                          <p className="text-gray-400 text-sm">Advanced editing tools</p>
                        </div>
                      </div>
                      <button className="bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200">
                        Open Editor
                      </button>
                    </div>
                    <div className="text-gray-400 text-sm">
                      Timeline-based editing with AI assistance
                    </div>
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-between mt-8 pt-6 border-t border-white/10">
                <div className="flex items-center space-x-4">
                  <button className="bg-white/10 hover:bg-white/20 border border-white/20 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2">
                    <Download className="w-4 h-4" />
                    <span>Download Original</span>
                  </button>
                  <button className="bg-white/10 hover:bg-white/20 border border-white/20 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2">
                    <Share2 className="w-4 h-4" />
                    <span>Share</span>
                  </button>
                </div>
                <button
                  onClick={() => setSelectedRecording(null)}
                  className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-8 py-3 rounded-lg font-medium transition-all duration-200"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoadingRecordings && (
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-12 text-center">
          <Loader2 className="w-16 h-16 text-gray-400 mx-auto mb-4 animate-spin" />
          <h3 className="text-xl font-semibold text-white mb-2">Chargement des enregistrements...</h3>
          <p className="text-gray-400">Récupération des vidéos depuis le système de fichiers</p>
        </div>
      )}

      {/* Empty State */}
      {!isLoadingRecordings && filteredRecordings.length === 0 && (
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-12 text-center">
          <Video className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-white mb-2">No recordings found</h3>
          <p className="text-gray-400 mb-6">
            {searchTerm || filterStatus !== 'all' || filterCategory !== 'all'
              ? 'Try adjusting your search or filters' 
              : 'Start streaming to create your first recording or upload a video manually'}
          </p>
          {!searchTerm && filterStatus === 'all' && filterCategory === 'all' && (
            <div className="flex items-center justify-center space-x-4">
              <button className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200">
                Start Your First Stream
              </button>
              <button
                onClick={() => setShowUploadModal(true)}
                className="bg-white/10 hover:bg-white/20 border border-white/20 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2"
              >
                <Upload className="w-4 h-4" />
                <span>Upload Video</span>
              </button>
            </div>
          )}
        </div>
      )}

      {/* Processing Progress Modals */}
      {Object.entries(processingStates).map(([recordingId, state]) => {
        if (!state.showProgress) return null;
        
        return (
          <ProcessingProgress
            key={`progress-${recordingId}`}
            isOpen={state.showProgress}
            onClose={() => handleCloseProgress(recordingId)}
            taskStatus={state.taskStatus}
            uploadProgress={state.uploadProgress}
            estimatedTime={state.estimatedTime}
            onCancel={() => handleCancelProcessing(recordingId)}
          />
        );
      })}

      {/* Processing Results Modals */}
      {Object.entries(processingStates).map(([recordingId, state]) => {
        if (!state.showResults || !state.taskStatus) return null;
        
        return (
          <div key={`results-${recordingId}`} className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-6">
            <div className="bg-gray-900/95 backdrop-blur-md border border-white/20 rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-8">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-2xl font-bold text-white">Résultats AutoMontage</h3>
                  <button
                    onClick={() => handleCloseResults(recordingId)}
                    className="bg-white/10 hover:bg-white/20 border border-white/20 text-white p-2 rounded-lg transition-all duration-200"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>
                
                <ProcessedResults
                  taskStatus={state.taskStatus}
                  onClose={() => handleCloseResults(recordingId)}
                />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default Recordings;
