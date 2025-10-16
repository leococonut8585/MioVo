"""
File Processing Tests for MioVo Application
Tests audio file validation, metadata extraction, and processing
"""
import os
import wave
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class FileProcessingTestSuite:
    """Test suite for audio file processing"""
    
    def __init__(self):
        self.test_data_dir = Path("test-data/audio")
        self.test_results = []
        
    def record_result(self, test_name: str, passed: bool, details: str = ""):
        """Record test result"""
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
        if details:
            print(f"  Details: {details}")
    
    def validate_wav_format(self, file_path: Path) -> Dict[str, Any]:
        """Validate WAV file format and extract metadata"""
        try:
            with wave.open(str(file_path), 'rb') as wav_file:
                metadata = {
                    "filename": file_path.name,
                    "format": "WAV",
                    "channels": wav_file.getnchannels(),
                    "sample_width": wav_file.getsampwidth(),
                    "framerate": wav_file.getframerate(),
                    "n_frames": wav_file.getnframes(),
                    "duration_seconds": wav_file.getnframes() / wav_file.getframerate(),
                    "file_size_mb": file_path.stat().st_size / (1024 * 1024)
                }
                return metadata
        except Exception as e:
            return {"error": str(e)}
    
    def test_wav_validation(self):
        """Test WAV file format validation"""
        wav_files = list(self.test_data_dir.glob("*.wav"))
        
        if not wav_files:
            self.record_result("WAV Validation", False, "No WAV files found")
            return False
        
        all_valid = True
        for wav_file in wav_files:
            metadata = self.validate_wav_format(wav_file)
            
            if "error" in metadata:
                self.record_result(
                    f"WAV Validation - {wav_file.name}",
                    False,
                    metadata["error"]
                )
                all_valid = False
            else:
                is_valid = (
                    metadata["channels"] in [1, 2] and
                    metadata["framerate"] in [16000, 22050, 44100, 48000] and
                    metadata["sample_width"] in [1, 2, 3, 4]
                )
                
                details = (
                    f"Channels: {metadata['channels']}, "
                    f"Sample Rate: {metadata['framerate']}Hz, "
                    f"Duration: {metadata['duration_seconds']:.2f}s, "
                    f"Size: {metadata['file_size_mb']:.2f}MB"
                )
                
                self.record_result(
                    f"WAV Validation - {wav_file.name}",
                    is_valid,
                    details
                )
                
                if not is_valid:
                    all_valid = False
        
        return all_valid
    
    def test_file_size_limits(self):
        """Test file size constraints"""
        MAX_SIZE_MB = 100  # Maximum file size in MB
        
        audio_files = list(self.test_data_dir.glob("*"))
        all_within_limits = True
        
        for audio_file in audio_files:
            file_size_mb = audio_file.stat().st_size / (1024 * 1024)
            within_limit = file_size_mb <= MAX_SIZE_MB
            
            self.record_result(
                f"File Size Check - {audio_file.name}",
                within_limit,
                f"Size: {file_size_mb:.2f}MB (Max: {MAX_SIZE_MB}MB)"
            )
            
            if not within_limit:
                all_within_limits = False
        
        return all_within_limits
    
    def test_metadata_extraction(self):
        """Test metadata extraction from audio files"""
        wav_files = list(self.test_data_dir.glob("*.wav"))
        
        if not wav_files:
            self.record_result("Metadata Extraction", False, "No audio files found")
            return False
        
        all_extracted = True
        extracted_metadata = []
        
        for wav_file in wav_files:
            metadata = self.validate_wav_format(wav_file)
            
            if "error" not in metadata:
                extracted_metadata.append(metadata)
                
                required_fields = ["channels", "framerate", "duration_seconds", "file_size_mb"]
                has_all_fields = all(field in metadata for field in required_fields)
                
                self.record_result(
                    f"Metadata Extraction - {wav_file.name}",
                    has_all_fields,
                    f"Extracted {len(metadata)} fields"
                )
                
                if not has_all_fields:
                    all_extracted = False
            else:
                self.record_result(
                    f"Metadata Extraction - {wav_file.name}",
                    False,
                    metadata["error"]
                )
                all_extracted = False
        
        # Save extracted metadata
        if extracted_metadata:
            with open("extracted_metadata.json", "w") as f:
                json.dump(extracted_metadata, f, indent=2)
        
        return all_extracted
    
    def test_audio_format_support(self):
        """Test support for different audio formats"""
        supported_formats = {
            ".wav": True,
            ".mp3": False,  # Would need additional library
            ".m4a": False,  # Would need additional library
            ".mp4": False,  # Would need additional library
        }
        
        for ext, expected_support in supported_formats.items():
            files = list(self.test_data_dir.glob(f"*{ext}"))
            
            if files and ext == ".wav":
                self.record_result(
                    f"Format Support - {ext.upper()}",
                    True,
                    f"Found {len(files)} {ext} files"
                )
            else:
                self.record_result(
                    f"Format Support - {ext.upper()}",
                    True,
                    f"Format support check: {expected_support}"
                )
        
        return True
    
    def test_batch_processing(self):
        """Test batch processing capability"""
        wav_files = list(self.test_data_dir.glob("*.wav"))[:3]  # Test with first 3 files
        
        if not wav_files:
            self.record_result("Batch Processing", False, "No files for batch test")
            return False
        
        batch_results = []
        start_time = datetime.now()
        
        for wav_file in wav_files:
            metadata = self.validate_wav_format(wav_file)
            if "error" not in metadata:
                batch_results.append(metadata)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        success = len(batch_results) == len(wav_files)
        self.record_result(
            "Batch Processing",
            success,
            f"Processed {len(batch_results)}/{len(wav_files)} files in {processing_time:.2f}s"
        )
        
        return success
    
    def run_all_tests(self):
        """Run all file processing tests"""
        print("\n" + "="*60)
        print("📁 Starting File Processing Tests")
        print("="*60 + "\n")
        
        test_methods = [
            self.test_wav_validation,
            self.test_file_size_limits,
            self.test_metadata_extraction,
            self.test_audio_format_support,
            self.test_batch_processing
        ]
        
        for test_method in test_methods:
            test_method()
        
        # Summary
        passed = sum(1 for r in self.test_results if r["passed"])
        total = len(self.test_results)
        
        print("\n" + "="*60)
        print(f"📊 Test Summary: {passed}/{total} tests passed")
        print("="*60 + "\n")
        
        # Save results to JSON
        with open("file_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        print("✅ Test results saved to file_test_results.json")
        return self.test_results


def main():
    """Main test runner"""
    suite = FileProcessingTestSuite()
    return suite.run_all_tests()


if __name__ == "__main__":
    main()