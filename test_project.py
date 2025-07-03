import pytest
import json
import os
import tempfile
from unittest.mock import patch, mock_open, MagicMock
from project import load_stats, save_stats, parse_and_apply_stat_updates, display_stats, handle_api_error, initialize_gemini_api


class TestLoadStats:
    """Test cases for the load_stats function."""
    
    def test_load_stats_default_when_file_missing(self):
        """Test loading default stats when file doesn't exist."""
        with patch('os.path.exists', return_value=False):
            stats = load_stats()
            expected = {
                "Knowledge": 0,
                "Charm": 0,
                "Guts": 0,
                "Health": 0,
                "Kindness": 0
            }
            assert stats == expected
    
    def test_load_stats_from_existing_file(self):
        """Test loading stats from an existing valid file."""
        test_stats = {
            "Knowledge": 5,
            "Charm": 3,
            "Guts": 2,
            "Health": 4,
            "Kindness": 1
        }
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=json.dumps(test_stats))):
                stats = load_stats()
                assert stats == test_stats
    
    def test_load_stats_corrupted_file(self):
        """Test loading stats when file is corrupted."""
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data="invalid json")):
                stats = load_stats()
                expected = {
                    "Knowledge": 0,
                    "Charm": 0,
                    "Guts": 0,
                    "Health": 0,
                    "Kindness": 0
                }
                assert stats == expected
    
    def test_load_stats_missing_keys(self):
        """Test loading stats when file has missing keys."""
        incomplete_stats = {
            "Knowledge": 5,
            "Charm": 3
        }
        
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=json.dumps(incomplete_stats))):
                stats = load_stats()
                assert stats["Knowledge"] == 5
                assert stats["Charm"] == 3
                assert stats["Guts"] == 0
                assert stats["Health"] == 0
                assert stats["Kindness"] == 0


class TestSaveStats:
    """Test cases for the save_stats function."""
    
    def test_save_stats_success(self):
        """Test successful saving of stats."""
        test_stats = {
            "Knowledge": 5,
            "Charm": 3,
            "Guts": 2,
            "Health": 4,
            "Kindness": 1
        }
        
        with patch('builtins.open', mock_open()) as mock_file:
            result = save_stats(test_stats)
            assert result is True
            mock_file.assert_called_once_with('persona_stats.json', 'w')
    
    def test_save_stats_failure(self):
        """Test saving stats when file operation fails."""
        test_stats = {"Knowledge": 5}
        
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            result = save_stats(test_stats)
            assert result is False


class TestParseAndApplyStatUpdates:
    """Test cases for the parse_and_apply_stat_updates function."""
    
    def test_parse_valid_output(self):
        """Test parsing valid AI output."""
        ai_output = "Knowledge = 2\nCharm = 1"
        initial_stats = {
            "Knowledge": 5,
            "Charm": 3,
            "Guts": 2,
            "Health": 4,
            "Kindness": 1
        }
        
        with patch('builtins.print'):  # Suppress print output during test
            updated_stats = parse_and_apply_stat_updates(ai_output, initial_stats)
            
        assert updated_stats["Knowledge"] == 7
        assert updated_stats["Charm"] == 4
        assert updated_stats["Guts"] == 2  # Unchanged
    
    def test_parse_invalid_stat_name(self):
        """Test parsing output with invalid stat name."""
        ai_output = "InvalidStat = 2\nCharm = 1"
        initial_stats = {
            "Knowledge": 5,
            "Charm": 3,
            "Guts": 2,
            "Health": 4,
            "Kindness": 1
        }
        
        with patch('builtins.print'):
            updated_stats = parse_and_apply_stat_updates(ai_output, initial_stats)
            
        assert updated_stats["Charm"] == 4
        assert updated_stats["Knowledge"] == 5  # Unchanged
    
    def test_parse_invalid_points_value(self):
        """Test parsing output with invalid points value."""
        ai_output = "Knowledge = invalid\nCharm = 1"
        initial_stats = {
            "Knowledge": 5,
            "Charm": 3,
            "Guts": 2,
            "Health": 4,
            "Kindness": 1
        }
        
        with patch('builtins.print'):
            updated_stats = parse_and_apply_stat_updates(ai_output, initial_stats)
            
        assert updated_stats["Charm"] == 4
        assert updated_stats["Knowledge"] == 5  # Unchanged
    
    def test_parse_no_valid_updates(self):
        """Test parsing output with no valid updates."""
        ai_output = "This is just explanatory text\nNo valid stat updates here"
        initial_stats = {
            "Knowledge": 5,
            "Charm": 3,
            "Guts": 2,
            "Health": 4,
            "Kindness": 1
        }
        
        with patch('builtins.print'):
            updated_stats = parse_and_apply_stat_updates(ai_output, initial_stats)
            
        assert updated_stats == initial_stats  # No changes
    
    def test_parse_mixed_valid_invalid(self):
        """Test parsing output with mix of valid and invalid lines."""
        ai_output = "Knowledge = 2\nThis is explanation\nCharm = 1\nInvalidStat = 3"
        initial_stats = {
            "Knowledge": 5,
            "Charm": 3,
            "Guts": 2,
            "Health": 4,
            "Kindness": 1
        }
        
        with patch('builtins.print'):
            updated_stats = parse_and_apply_stat_updates(ai_output, initial_stats)
            
        assert updated_stats["Knowledge"] == 7
        assert updated_stats["Charm"] == 4
        assert updated_stats["Guts"] == 2  # Unchanged


class TestDisplayStats:
    """Test cases for the display_stats function."""
    
    def test_display_stats_output(self):
        """Test that display_stats prints the correct format."""
        test_stats = {
            "Knowledge": 5,
            "Charm": 3,
            "Guts": 2,
            "Health": 4,
            "Kindness": 1
        }
        
        with patch('builtins.print') as mock_print:
            display_stats(test_stats)
            
        # Check that print was called with expected content
        calls = mock_print.call_args_list
        assert len(calls) == 7  # Header + 5 stats + footer
        assert "Current Persona Stats" in calls[0][0][0]
        assert "Knowledge: 5" in calls[1][0][0]
        assert "Charm: 3" in calls[2][0][0]


class TestHandleApiError:
    """Test cases for the handle_api_error function."""
    
    def test_handle_resource_exhausted_error(self):
        """Test handling of rate limit errors."""
        error = Exception("RESOURCE_EXHAUSTED: Rate limit exceeded")
        
        with patch('builtins.print') as mock_print:
            handle_api_error(error)
            
        mock_print.assert_called_with("You might have hit a rate limit. Wait a bit and try again.")
    
    def test_handle_permission_denied_error(self):
        """Test handling of permission denied errors."""
        error = Exception("PERMISSION_DENIED: API key not valid")
        
        with patch('builtins.print') as mock_print:
            handle_api_error(error)
            
        mock_print.assert_called_with("Your API key might have issues. Verify permissions in Google AI Studio.")
    
    def test_handle_model_not_found_error(self):
        """Test handling of model not found errors."""
        error = Exception("model is not found")
        
        with patch('builtins.print') as mock_print:
            handle_api_error(error)
            
        calls = mock_print.call_args_list
        assert any("model" in str(call) and "no longer be available" in str(call) for call in calls)


class TestInitializeGeminiApi:
    """Test cases for the initialize_gemini_api function."""
    
    def test_initialize_missing_api_key(self):
        """Test initialization when API key is missing."""
        with patch('project.load_dotenv'):
            with patch('os.getenv', return_value=None):
                result = initialize_gemini_api()
                assert result is False
    
    def test_initialize_api_success(self):
        """Test successful API initialization."""
        with patch('project.load_dotenv'):
            with patch('os.getenv', return_value='test_api_key'):
                with patch('project.genai.configure'):
                    with patch('project.genai.GenerativeModel'):
                        result = initialize_gemini_api()
                        assert result is True
    
    def test_initialize_api_failure(self):
        """Test API initialization failure."""
        with patch('project.load_dotenv'):
            with patch('os.getenv', return_value='invalid_key'):
                with patch('project.genai.configure', side_effect=Exception("Invalid API key")):
                    result = initialize_gemini_api()
                    assert result is False


if __name__ == "__main__":
    pytest.main([__file__])
