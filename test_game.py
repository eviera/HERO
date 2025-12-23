"""
Test script to verify the game loads without errors
"""
import sys
import importlib.util

def test_import():
    """Test if hero.py can be imported without errors"""
    try:
        spec = importlib.util.spec_from_file_location("hero", "hero.py")
        hero_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(hero_module)
        print("[OK] hero.py imported successfully")
        return True
    except Exception as e:
        print(f"[FAIL] Error importing hero.py: {e}")
        return False

def test_classes():
    """Test if all classes can be instantiated"""
    try:
        from hero import Game, Player, Enemy, Miner, Bullet, Dynamite

        # Test instantiation
        game = Game()
        print("[OK] Game class instantiated")

        player = Player()
        print("[OK] Player class instantiated")

        enemy = Enemy(0, 0)
        print("[OK] Enemy class instantiated")

        miner = Miner(0, 0)
        print("[OK] Miner class instantiated")

        bullet = Bullet(0, 0, 1)
        print("[OK] Bullet class instantiated")

        dynamite = Dynamite(0, 0)
        print("[OK] Dynamite class instantiated")

        return True
    except Exception as e:
        print(f"[FAIL] Error instantiating classes: {e}")
        return False

def test_maps():
    """Test if all maps are valid"""
    try:
        from hero import MAPS

        if len(MAPS) != 5:
            print(f"[FAIL] Expected 5 maps, found {len(MAPS)}")
            return False

        print(f"[OK] Found {len(MAPS)} levels")

        for i, level_map in enumerate(MAPS):
            if len(level_map) != 13:
                print(f"[FAIL] Level {i+1} has {len(level_map)} rows, expected 13")
                return False

            for row in level_map:
                if len(row) != 16:
                    print(f"[FAIL] Level {i+1} has row with {len(row)} columns, expected 16")
                    return False

            # Check for required elements
            map_string = "".join(level_map)
            if "S" not in map_string:
                print(f"[FAIL] Level {i+1} missing start position (S)")
                return False
            if "R" not in map_string:
                print(f"[FAIL] Level {i+1} missing rescue target (R)")
                return False

            print(f"[OK] Level {i+1} is valid")

        return True
    except Exception as e:
        print(f"[FAIL] Error testing maps: {e}")
        return False

def test_functions():
    """Test utility functions"""
    try:
        from hero import load_scores, save_scores, add_score

        # Test load_scores (should return empty list if no file)
        scores = load_scores()
        print(f"[OK] load_scores() returned: {type(scores)}")

        # Test add_score
        test_scores = add_score("TEST", 1000)
        print(f"[OK] add_score() works, {len(test_scores)} scores saved")

        return True
    except Exception as e:
        print(f"[FAIL] Error testing functions: {e}")
        return False

def main():
    print("=" * 50)
    print("H.E.R.O. Game Test Suite")
    print("=" * 50)
    print()

    tests = [
        ("Import Test", test_import),
        ("Classes Test", test_classes),
        ("Maps Test", test_maps),
        ("Functions Test", test_functions),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        result = test_func()
        results.append((test_name, result))
        print()

    print("=" * 50)
    print("Test Results Summary")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASSED]" if result else "[FAILED]"
        print(f"{test_name}: {status}")

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n*** All tests passed! Game is ready to play! ***")
        return 0
    else:
        print("\n*** Some tests failed. Please check the errors above. ***")
        return 1

if __name__ == "__main__":
    sys.exit(main())
