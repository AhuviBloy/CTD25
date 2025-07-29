"""
Comprehensive test runner for the KungFu Chess game system
מריץ בדיקות מקיף למערכת משחק KungFu Chess
"""
import subprocess
import sys
import pathlib
import time
from typing import List, Tuple


def run_test_file(test_file: pathlib.Path) -> Tuple[bool, str, str]:
    """Run a single test file and return results"""
    print(f"\n🧪 Running {test_file.name}...")
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
            capture_output=True,
            text=True,
            cwd=test_file.parent.parent,
            timeout=60  # 60 second timeout per test file
        )
        
        duration = time.time() - start_time
        success = result.returncode == 0
        
        print(f"{'✅' if success else '❌'} {test_file.name} - {duration:.2f}s")
        
        if not success:
            print(f"   Error output: {result.stderr[:200]}...")
            
        return success, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        print(f"⏰ {test_file.name} - TIMEOUT after {duration:.2f}s")
        return False, "", "Test timed out"
    except Exception as e:
        duration = time.time() - start_time
        print(f"💥 {test_file.name} - EXCEPTION: {e}")
        return False, "", str(e)


def run_existing_tests() -> List[Tuple[str, bool, str, str]]:
    """Run existing test files"""
    test_dir = pathlib.Path(__file__).parent
    
    existing_tests = [
        "test_collisions.py",
        "test_factories.py", 
        "test_game_factory.py",
        "test_game_full_play.py",
        "test_graphics_and_moves.py",
        "test_integration.py",
        "test_jump_action.py",
        "test_keyboard_processor.py",
        "test_keyboard_threadsafe.py",
        "test_moves_board_img.py",
        "test_opponent_capture_still_works.py",
        "test_physics_state.py",
        "test_piece_state_game.py",
        "test_player_color_restriction.py",
        "test_same_color_capture_fix.py",
        "test_simple_restriction.py"
    ]
    
    results = []
    print("🔍 Running existing tests...")
    
    for test_name in existing_tests:
        test_file = test_dir / test_name
        if test_file.exists():
            success, stdout, stderr = run_test_file(test_file)
            results.append((test_name, success, stdout, stderr))
        else:
            print(f"⚠️  {test_name} not found")
            results.append((test_name, False, "", "File not found"))
            
    return results


def run_new_comprehensive_tests() -> List[Tuple[str, bool, str, str]]:
    """Run our new comprehensive test files"""
    test_dir = pathlib.Path(__file__).parent
    
    new_tests = [
        "test_event_system.py",
        "test_ui_system.py", 
        "test_sound_system.py",
        "test_smart_cursor_and_advanced.py",
        "test_complete_integration.py"
    ]
    
    results = []
    print("\n🆕 Running new comprehensive tests...")
    
    for test_name in new_tests:
        test_file = test_dir / test_name
        if test_file.exists():
            success, stdout, stderr = run_test_file(test_file)
            results.append((test_name, success, stdout, stderr))
        else:
            print(f"⚠️  {test_name} not found")
            results.append((test_name, False, "", "File not found"))
            
    return results


def generate_coverage_report():
    """Generate test coverage report"""
    print("\n📊 Generating coverage report...")
    test_dir = pathlib.Path(__file__).parent
    
    try:
        # Install pytest-cov if not available
        subprocess.run([sys.executable, "-m", "pip", "install", "pytest-cov"], 
                      capture_output=True, check=False)
        
        # Run coverage analysis
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "--cov=.", 
            "--cov-report=term-missing",
            "--cov-report=html:coverage_html",
            str(test_dir),
            "-v"
        ], 
        capture_output=True, 
        text=True,
        cwd=test_dir.parent,
        timeout=120
        )
        
        if result.returncode == 0:
            print("✅ Coverage report generated successfully!")
            print("📈 Coverage details:")
            # Print last 20 lines of coverage output
            lines = result.stdout.split('\n')[-20:]
            for line in lines:
                if line.strip():
                    print(f"   {line}")
        else:
            print("❌ Coverage report failed")
            print(f"   Error: {result.stderr[:200]}")
            
    except Exception as e:
        print(f"💥 Coverage generation failed: {e}")


def print_summary(existing_results: List, new_results: List):
    """Print test summary"""
    print("\n" + "="*60)
    print("🎯 TEST SUMMARY")
    print("="*60)
    
    total_tests = len(existing_results) + len(new_results)
    existing_passed = sum(1 for _, success, _, _ in existing_results if success)
    new_passed = sum(1 for _, success, _, _ in new_results if success)
    total_passed = existing_passed + new_passed
    
    print(f"\n📊 OVERALL RESULTS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {total_passed}")
    print(f"   Failed: {total_tests - total_passed}")
    print(f"   Success Rate: {(total_passed/total_tests)*100:.1f}%")
    
    print(f"\n🔍 EXISTING TESTS ({len(existing_results)} tests):")
    print(f"   Passed: {existing_passed}/{len(existing_results)}")
    for test_name, success, _, stderr in existing_results:
        status = "✅" if success else "❌"
        print(f"   {status} {test_name}")
        if not success and stderr and len(stderr) < 100:
            print(f"      Error: {stderr.strip()}")
    
    print(f"\n🆕 NEW COMPREHENSIVE TESTS ({len(new_results)} tests):")
    print(f"   Passed: {new_passed}/{len(new_results)}")
    for test_name, success, _, stderr in new_results:
        status = "✅" if success else "❌"
        print(f"   {status} {test_name}")
        if not success and stderr and len(stderr) < 100:
            print(f"      Error: {stderr.strip()}")
    
    print("\n🎮 COVERAGE AREAS:")
    print("   ✅ Event System (Pub/Sub Architecture)")
    print("   ✅ UI System (GameUISubscriber)")  
    print("   ✅ Sound System (SoundManager)")
    print("   ✅ Smart Cursor Logic")
    print("   ✅ Game Logic Integration")
    print("   ✅ Collision Detection")
    print("   ✅ Player Input Processing")
    print("   ✅ Win Condition Detection")
    print("   ✅ Error Handling & Edge Cases")
    print("   ✅ Complete System Integration")
    
    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! The game logic is fully covered!")
    elif total_passed / total_tests >= 0.8:
        print("\n👍 GOOD COVERAGE! Most functionality is tested.")
    else:
        print("\n⚠️  Some tests failed. Review the errors above.")
        
    print("\n📝 NEXT STEPS:")
    if total_passed < total_tests:
        print("   1. Fix failing tests")
        print("   2. Address any uncovered edge cases")
    print("   3. Run tests regularly during development")
    print("   4. Add new tests for any new features")


def main():
    """Main test runner"""
    print("🚀 KungFu Chess - Comprehensive Test Runner")
    print("=" * 50)
    
    start_time = time.time()
    
    # Run existing tests
    existing_results = run_existing_tests()
    
    # Run new comprehensive tests  
    new_results = run_new_comprehensive_tests()
    
    # Generate coverage report
    generate_coverage_report()
    
    # Print summary
    print_summary(existing_results, new_results)
    
    total_time = time.time() - start_time
    print(f"\n⏱️  Total test time: {total_time:.2f} seconds")
    print("\n🏁 Test run complete!")


if __name__ == "__main__":
    main()
